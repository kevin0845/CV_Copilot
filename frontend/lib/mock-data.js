export const mockAnalysisResults = {
  match_score: 78,
  strengths: [
    "Resume shows direct automation experience through process improvement work and API-based internal tooling.",
    "The candidate has explicit AI exposure, which supports the role's AI-enabled workflow focus.",
    "Cross-functional collaboration is already present through work with operations and business teams."
  ],
  gaps: [
    "The resume does not explicitly mention customer operations platforms such as Gainsight or Zendesk.",
    "No direct evidence was found for workflow-automation vendors like Workato or Make."
  ],
  missing_keywords: ["Workato", "Gainsight", "Zendesk", "SaaS"],
  under_emphasized_experience: [
    "Resume evidence 'Automated manual business processes for operations teams' supports workflow automation and eliminating manual work, but the connection could be stated more directly.",
    "Resume evidence 'Developed an internal AI tool for support workflows' is relevant to AI-enabled workflows and piloting AI solutions, even though it does not mirror the JD wording exactly."
  ],
  evidence_notes: [
    "Skills alignment: matched Python, SQL, Salesforce, REST APIs, and automation-related experience; missing explicit evidence for Workato and Gainsight.",
    "Experience relevance: one responsibility is directly supported, two are partially supported through related concepts, and one remains unproven.",
    "Domain fit: resume shows adjacent business-software evidence through internal tools, API integrations, and operations-facing process work."
  ]
};

export const sampleJobDescription = `Customer Operations AI & Automation Lead

Optro is hiring a builder who can identify automation opportunities, design AI-enabled workflows, and partner with frontline teams to eliminate manual work.

Key Responsibilities
- Identify automation opportunities across customer operations
- Design AI-enabled workflows and internal process improvements
- Partner with frontline and business teams to reduce manual work
- Pilot third-party AI and workflow automation solutions

Requirements
- Python
- SQL
- Salesforce
- REST APIs
- JSON
- webhooks

Preferred Qualifications
- Workato
- Gainsight
- Zendesk
- SaaS experience`;
