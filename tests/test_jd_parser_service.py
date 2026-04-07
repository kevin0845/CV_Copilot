import unittest

from app.schemas.parse import JobDescriptionParseRequest
from app.services.jd_parser_service import parse_job_description


class JobDescriptionParserTests(unittest.TestCase):
    def test_maps_input_fields_and_extracts_fallback_responsibilities(self) -> None:
        payload = JobDescriptionParseRequest(
            job_title="Customer Operations AI & Automation Lead",
            company_name="Optro",
            job_description_text=(
                "This role will identify automation opportunities, design AI-enabled "
                "workflows, partner with frontline teams to eliminate manual work, "
                "and pilot third-party AI and automated workflow solutions."
            ),
        )

        result = parse_job_description(payload)

        self.assertEqual(result.company, "Optro")
        self.assertEqual(result.title, "Customer Operations AI & Automation Lead")
        self.assertEqual(result.required_skills, [])
        self.assertEqual(result.preferred_skills, [])
        self.assertEqual(
            result.responsibilities,
            [
                "Identify automation opportunities",
                "Design AI-enabled workflows",
                "Partner with frontline teams to eliminate manual work",
                "Pilot third-party AI and automated workflow solutions",
            ],
        )
        self.assertIsNone(result.seniority)
        self.assertIsNone(result.industry)
        self.assertEqual(
            result.keywords[:4],
            ["automation", "AI-enabled", "workflows", "frontline"],
        )

    def test_parses_section_based_skills_responsibilities_seniority_and_saas(self) -> None:
        payload = JobDescriptionParseRequest(
            job_title="Customer Operations AI & Automation Lead",
            company_name="Optro",
            job_description_text=(
                "Optro is a SaaS platform for customer operations.\n"
                "Key Responsibilities\n"
                "- Build REST APIs for automation workflows\n"
                "- Partner with teams in Salesforce and Zendesk\n"
                "Requirements\n"
                "- 5+ years of experience with Python, SQL, REST APIs, JSON, and webhooks\n"
                "- Experience with Snowflake\n"
                "Preferred Qualifications\n"
                "- Experience with Workato, Zapier, Make, LLM, ChatGPT, and Gemini"
            ),
        )

        result = parse_job_description(payload)

        self.assertEqual(
            result.required_skills,
            ["Python", "SQL", "REST APIs", "JSON", "webhooks", "Snowflake"],
        )
        self.assertEqual(
            result.preferred_skills,
            ["Workato", "Zapier", "Make", "LLM", "ChatGPT", "Gemini"],
        )
        self.assertEqual(
            result.responsibilities,
            [
                "Build REST APIs for automation workflows",
                "Partner with teams in Salesforce and Zendesk",
            ],
        )
        self.assertEqual(result.seniority, "5+ years of experience")
        self.assertEqual(result.industry, "SaaS")
        self.assertIn("automation", result.keywords)
        self.assertIn("workflows", result.keywords)

    def test_parses_inline_required_and_preferred_signals(self) -> None:
        payload = JobDescriptionParseRequest(
            job_title="Automation Specialist",
            company_name="Optro",
            job_description_text=(
                "Required: Python and JSON. "
                "Nice to have: Workato, Zapier, and Salesforce. "
                "You will automate workflows and support Salesforce operations."
            ),
        )

        result = parse_job_description(payload)

        self.assertEqual(result.required_skills, ["Python", "JSON"])
        self.assertEqual(result.preferred_skills, ["Workato", "Zapier", "Salesforce"])
        self.assertEqual(
            result.responsibilities,
            ["Automate workflows and support Salesforce operations"],
        )

    def test_keeps_section_responsibility_lines_as_complete_bullets(self) -> None:
        payload = JobDescriptionParseRequest(
            job_title="SQL Engineer / Data Analyst",
            company_name="The MLC",
            job_description_text=(
                "Essential Responsibilities\n"
                "Design, develop, and maintain complex SQL queries, stored procedures, and views to support business operations and reporting\n"
                "Optimize database performance through query tuning, indexing strategies, and execution plan analysis"
            ),
        )

        result = parse_job_description(payload)

        self.assertEqual(
            result.responsibilities,
            [
                "Design, develop, and maintain complex SQL queries, stored procedures, and views to support business operations and reporting",
                "Optimize database performance through query tuning, indexing strategies, and execution plan analysis",
            ],
        )


if __name__ == "__main__":
    unittest.main()
