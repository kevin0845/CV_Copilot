export const mockResults = {
  matchScore: 82,
  strengths: [
    "Resume shows strong overlap with the target backend stack through Python, FastAPI, and Docker.",
    "Healthcare experience is already present in the summary and work history, which supports the domain fit.",
    "Senior-level title evidence aligns well with the target role's seniority."
  ],
  gaps: [
    "PostgreSQL is requested in the JD but is not called out explicitly in the resume.",
    "Infrastructure tooling such as Terraform is missing from the resume language.",
    "One work bullet implies cross-functional collaboration, but it could be stated more directly."
  ],
  missingKeywords: ["PostgreSQL", "Terraform", "REST APIs"],
  tailoredSummary:
    "Senior Software Engineer with experience building healthcare-focused backend services using Python, FastAPI, and Docker, with cross-functional collaboration across product and engineering teams.",
  rewriteSuggestions: [
    {
      original: "Built backend services for healthcare workflows",
      suggested:
        "Built backend services for healthcare workflows using Python and FastAPI.",
      rationale:
        "Adds already-supported technical context from the skills section to better align the bullet with the target backend role."
    },
    {
      original: "Collaborated with product teams",
      suggested:
        "Collaborated with product teams to shape backend service requirements and delivery.",
      rationale:
        "Makes the collaboration more specific to backend work without inventing outcomes or new stakeholders."
    },
    {
      original: "Docker, Python, FastAPI",
      suggested: "Python, FastAPI, Docker",
      rationale:
        "Surfaces the most relevant role-aligned skills first for faster recruiter scanning."
    }
  ]
};

export const sampleJobDescription = `Senior Backend Engineer

We are looking for a backend engineer to build and maintain API services for a healthcare workflow platform.

Responsibilities
- Build and maintain FastAPI services
- Collaborate with product and design
- Improve service reliability and API quality

Requirements
- Python
- FastAPI
- PostgreSQL
- REST APIs

Preferred Qualifications
- Docker
- Terraform
- Healthcare experience`;
