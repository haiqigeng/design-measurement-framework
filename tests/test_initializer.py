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
            locales=["en"],
            source_reference="Test brief",
        )
        self.assertEqual(draft["schema_version"], "1.3.0")
        self.assertEqual(draft["document"]["products"], ["Public website"])
        self.assertEqual(draft["document"]["locales"], ["en"])
        self.assertEqual(
            draft["intake_baseline"]["targets"][0]["resolved_scope_targets"],
            ["https://example.com/"],
        )
        self.assertRegex(draft["document"]["run_id"], r"^run_[a-f0-9]{32}$")
        self.assertNotIn("notes", draft["document"])
        self.assertEqual(draft["journeys"], [])
        self.assertTrue(
            all(gate["status"] == "fail" for gate in draft["quality_gates"].values())
        )

    def test_description_only_future_scope_does_not_require_a_site_placeholder(
        self,
    ) -> None:
        draft = build_draft(
            title="Future service",
            scope="Planned authenticated service",
            language="en",
            target_state="to_be",
            scope_claim="journey_subset",
            target_sites=[],
            products=["Future service"],
            markets=[],
            audiences=["Members"],
            locales=["en"],
            source_reference="Approved design brief",
        )
        self.assertEqual(draft["document"]["target_sites"], [])
        self.assertEqual(draft["intake_baseline"]["targets"], [])


if __name__ == "__main__":
    unittest.main()
