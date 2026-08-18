from __future__ import annotations

import sys
import unittest

from helpers import ROOT

sys.path.insert(0, str(ROOT / "scripts"))

from init_framework import build_draft  # noqa: E402


class MeasurementFrameworkInitializerTests(unittest.TestCase):
    def test_initializer_creates_explicit_incomplete_working_state(self) -> None:
        draft = build_draft(
            title="Draft",
            scope="Whole site",
            language="en",
            target_state="as_is",
            scope_claim="whole_site",
            target_sites=["https://example.com/"],
            products=["Public website"],
            markets=[],
            audiences=[],
            source_reference="Test brief",
        )
        self.assertEqual(draft["schema_version"], "1.1.0")
        self.assertEqual(draft["document"]["products"], ["Public website"])
        self.assertRegex(draft["document"]["run_id"], r"^run_[a-f0-9]{32}$")
        self.assertEqual(draft["journeys"], [])
        self.assertTrue(
            all(gate["status"] == "fail" for gate in draft["quality_gates"].values())
        )


if __name__ == "__main__":
    unittest.main()
