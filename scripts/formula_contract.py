"""Versioned KPI formula validation."""

from __future__ import annotations

import ast
from typing import Any

V1_2_SCHEMA_VERSION = (1, 2, 0)
ALLOWED_FUNCTIONS = {
    "abs",
    "average",
    "cohort_rate",
    "count",
    "distinct_count",
    "index_value",
    "max",
    "min",
    "percentile",
    "rate",
    "retention_rate",
    "safe_divide",
    "sum",
    "weighted_average",
}
ALLOWED_BINARY_OPERATORS = {ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow}
ALLOWED_UNARY_OPERATORS = {ast.UAdd, ast.USub}
FORMULA_INPUT_ROLES = {"numerator", "denominator", "input"}
FUNCTION_ARITY = {
    "abs": (1, 1),
    "average": (1, 1),
    "cohort_rate": (2, 2),
    "count": (1, 1),
    "distinct_count": (1, 1),
    "index_value": (1, None),
    "max": (2, None),
    "min": (2, None),
    "percentile": (2, 2),
    "rate": (2, 2),
    "retention_rate": (2, 2),
    "safe_divide": (2, 2),
    "sum": (1, 1),
    "weighted_average": (2, 2),
}


def uses_v1_2_contract(data: dict[str, Any]) -> bool:
    version = data.get("schema_version")
    if not isinstance(version, str):
        return False
    try:
        parsed = tuple(int(part) for part in version.split("."))
    except ValueError:
        return False
    return parsed >= V1_2_SCHEMA_VERSION


def _parse_expression(
    expression: Any, path: str, errors: list[str]
) -> tuple[set[str], set[str], set[type[ast.operator]]]:
    if not isinstance(expression, str) or not expression.strip():
        return set(), set(), set()
    try:
        parsed = ast.parse(expression, mode="eval")
    except SyntaxError as exc:
        errors.append(f"{path}: expression is not valid arithmetic syntax ({exc.msg})")
        return set(), set(), set()

    symbols: set[str] = set()
    functions: set[str] = set()
    operators: set[type[ast.operator]] = set()

    def walk(node: ast.AST) -> None:
        if isinstance(node, ast.Expression):
            walk(node.body)
            return
        if isinstance(node, ast.BinOp):
            operator_type = type(node.op)
            if operator_type not in ALLOWED_BINARY_OPERATORS:
                errors.append(
                    f"{path}: operator {operator_type.__name__!r} is not allowed"
                )
            operators.add(operator_type)
            walk(node.left)
            walk(node.right)
            return
        if isinstance(node, ast.UnaryOp):
            operator_type = type(node.op)
            if operator_type not in ALLOWED_UNARY_OPERATORS:
                errors.append(
                    f"{path}: unary operator {operator_type.__name__!r} is not allowed"
                )
            walk(node.operand)
            return
        if isinstance(node, ast.Name):
            symbols.add(node.id)
            return
        if isinstance(node, ast.Constant):
            if isinstance(node.value, bool) or not isinstance(node.value, (int, float)):
                errors.append(f"{path}: only numeric constants are allowed")
            return
        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                errors.append(f"{path}: only named formula functions are allowed")
            elif node.func.id not in ALLOWED_FUNCTIONS:
                errors.append(
                    f"{path}: formula function {node.func.id!r} is not allowed"
                )
            else:
                functions.add(node.func.id)
                minimum, maximum = FUNCTION_ARITY[node.func.id]
                argument_count = len(node.args)
                if argument_count < minimum or (
                    maximum is not None and argument_count > maximum
                ):
                    expected = (
                        str(minimum) if maximum == minimum else f"at least {minimum}"
                    )
                    errors.append(
                        f"{path}: function {node.func.id!r} requires {expected} "
                        f"argument(s), got {argument_count}"
                    )
            if node.keywords:
                errors.append(f"{path}: keyword arguments are not allowed")
            for argument in node.args:
                walk(argument)
            return
        errors.append(
            f"{path}: expression element {type(node).__name__!r} is not allowed"
        )

    walk(parsed)
    return symbols, functions, operators


def validate_structured_formula(kpi: dict[str, Any], kpi_index: int) -> list[str]:
    errors: list[str] = []
    formula = kpi.get("formula")
    if not isinstance(formula, dict):
        return errors
    path = f"$.kpis[{kpi_index}].formula"
    for field in ("calculation_type", "result_unit"):
        if (
            not isinstance(formula.get(field), str)
            or not formula.get(field, "").strip()
        ):
            errors.append(f"{path}.{field}: required for schema 1.2.0")

    components = formula.get("components", [])
    declared_symbols: dict[str, dict[str, Any]] = {}
    if isinstance(components, list):
        for component_index, component in enumerate(components):
            if not isinstance(component, dict):
                continue
            component_path = f"{path}.components[{component_index}]"
            for field in ("symbol", "counting_unit", "grain"):
                if (
                    not isinstance(component.get(field), str)
                    or not component.get(field, "").strip()
                ):
                    errors.append(
                        f"{component_path}.{field}: required for schema 1.2.0"
                    )
            symbol = component.get("symbol")
            if not isinstance(symbol, str) or not symbol:
                continue
            if symbol in declared_symbols:
                errors.append(
                    f"{component_path}.symbol: duplicate formula symbol {symbol!r}"
                )
            declared_symbols[symbol] = component

    expression_path = f"{path}.expression"
    used_symbols, functions, operators = _parse_expression(
        formula.get("expression"), expression_path, errors
    )
    for symbol in sorted(used_symbols - set(declared_symbols)):
        errors.append(f"{expression_path}: undeclared component symbol {symbol!r}")

    required_symbols = {
        symbol
        for symbol, component in declared_symbols.items()
        if component.get("role") in FORMULA_INPUT_ROLES
    }
    for symbol in sorted(required_symbols - used_symbols):
        errors.append(
            f"{expression_path}: component symbol {symbol!r} is not used by the calculation"
        )
    if declared_symbols and not used_symbols:
        errors.append(
            f"{expression_path}: calculation uses no declared component symbol"
        )

    calculation_type = formula.get("calculation_type")
    division_functions = {"cohort_rate", "rate", "retention_rate", "safe_divide"}
    if calculation_type in {"ratio", "rate", "cohort", "retention"} and not (
        ast.Div in operators or functions & division_functions
    ):
        errors.append(
            f"{path}.calculation_type: {calculation_type!r} requires division or a rate function"
        )
    component_roles = {
        component.get("role")
        for component in components
        if isinstance(components, list) and isinstance(component, dict)
    }
    if calculation_type in {"ratio", "rate", "cohort", "retention"} and not {
        "numerator",
        "denominator",
    }.issubset(component_roles):
        errors.append(
            f"{path}.components: {calculation_type!r} requires numerator and denominator roles"
        )
    if calculation_type == "weighted_average" and "weighted_average" not in functions:
        errors.append(
            f"{path}.calculation_type: 'weighted_average' requires weighted_average(...)"
        )
    if calculation_type == "percentile" and "percentile" not in functions:
        errors.append(f"{path}.calculation_type: 'percentile' requires percentile(...)")
    return errors
