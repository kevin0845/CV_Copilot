import unittest

from app.schemas.parse import JobDescriptionParseResponse, ResumeParseResponse, WorkExperienceItem
from app.services.gap_analysis_service import analyze_gap


class GapAnalysisServiceTests(unittest.TestCase):
    def test_related_responsibility_moves_to_under_emphasized_experience(self) -> None:
        resume = ResumeParseResponse(
            source_filename=None,
            normalized_text="sample",
            name="Candidate",
            contact=None,
            summary="Operations-focused builder improving team workflows.",
            skills=[],
            work_experience=[
                WorkExperienceItem(
                    company="Acme",
                    title="Automation Specialist",
                    date_range="2022 - Present",
                    bullets=["Automated manual business processes for operations teams"],
                )
            ],
            education=[],
            certifications=[],
            projects=[],
        )
        job = JobDescriptionParseResponse(
            company="Optro",
            title="Customer Operations AI & Automation Lead",
            required_skills=[],
            preferred_skills=[],
            responsibilities=["Partner with frontline teams to eliminate manual work"],
            seniority=None,
            industry=None,
            keywords=[],
        )

        result = analyze_gap(resume, job)

        self.assertEqual(result.gaps, [])
        self.assertEqual(len(result.under_emphasized_experience), 1)
        self.assertIn("Automated manual business processes for operations teams", result.under_emphasized_experience[0])
        self.assertIn("Partner with frontline teams to eliminate manual work", result.under_emphasized_experience[0])
        self.assertTrue(any("partially supported" in note for note in result.evidence_notes))

    def test_ai_workflow_responsibility_gets_partial_credit_not_full_gap(self) -> None:
        resume = ResumeParseResponse(
            source_filename=None,
            normalized_text="sample",
            name="Candidate",
            contact=None,
            summary="Built internal tools for support operations.",
            skills=[],
            work_experience=[
                WorkExperienceItem(
                    company="Acme",
                    title="Software Engineer",
                    date_range="2021 - Present",
                    bullets=["Developed an internal AI tool for support workflows"],
                )
            ],
            education=[],
            certifications=[],
            projects=[],
        )
        job = JobDescriptionParseResponse(
            company="Optro",
            title="AI Automation Lead",
            required_skills=[],
            preferred_skills=[],
            responsibilities=["Design AI-enabled workflows"],
            seniority=None,
            industry=None,
            keywords=[],
        )

        result = analyze_gap(resume, job)

        self.assertEqual(result.gaps, [])
        self.assertEqual(len(result.under_emphasized_experience), 1)
        self.assertIn("Developed an internal AI tool for support workflows", result.under_emphasized_experience[0])
        self.assertTrue(any("related concepts" in item for item in result.under_emphasized_experience))

    def test_adjacent_saas_domain_evidence_is_reported_conservatively(self) -> None:
        resume = ResumeParseResponse(
            source_filename=None,
            normalized_text="sample",
            name="Candidate",
            contact=None,
            summary="Built backend services and internal tools for business teams.",
            skills=["Python"],
            work_experience=[
                WorkExperienceItem(
                    company="Acme",
                    title="Software Engineer",
                    date_range="2021 - Present",
                    bullets=["Implemented API integrations for internal tools"],
                )
            ],
            education=[],
            certifications=[],
            projects=[],
        )
        job = JobDescriptionParseResponse(
            company="Optro",
            title="Platform Engineer",
            required_skills=[],
            preferred_skills=[],
            responsibilities=[],
            seniority=None,
            industry="SaaS",
            keywords=[],
        )

        result = analyze_gap(resume, job)

        self.assertTrue(any("adjacent domain evidence" in strength for strength in result.strengths))
        self.assertFalse(any("does not explicitly mention SaaS-related work" in gap for gap in result.gaps))
        self.assertTrue(any("adjacent business-software evidence" in note for note in result.evidence_notes))


if __name__ == "__main__":
    unittest.main()
