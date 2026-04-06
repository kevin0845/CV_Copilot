from pydantic import BaseModel, ConfigDict, Field


class ResumeParseRequest(BaseModel):
    candidate_name: str | None = Field(default=None, description="Candidate full name.")
    source_filename: str | None = Field(
        default=None,
        description="Original uploaded resume filename.",
    )
    resume_text: str = Field(..., min_length=1, description="Raw resume text content.")


class ContactInfo(BaseModel):
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    linkedin: str | None = None
    github: str | None = None
    website: str | None = None


class WorkExperienceItem(BaseModel):
    company: str | None = None
    title: str | None = None
    date_range: str | None = None
    bullets: list[str] = Field(default_factory=list)


class EducationItem(BaseModel):
    institution: str | None = None
    degree: str | None = None
    date_range: str | None = None
    details: list[str] = Field(default_factory=list)


class CertificationItem(BaseModel):
    name: str | None = None
    issuer: str | None = None
    date_range: str | None = None


class ProjectItem(BaseModel):
    name: str | None = None
    description: str | None = None
    bullets: list[str] = Field(default_factory=list)


class ResumeParseResponse(BaseModel):
    source_filename: str | None
    normalized_text: str
    name: str | None
    contact: ContactInfo | None
    summary: str | None
    skills: list[str]
    work_experience: list[WorkExperienceItem]
    education: list[EducationItem]
    certifications: list[CertificationItem]
    projects: list[ProjectItem]


class JobDescriptionParseRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "job_title": "Customer Operations AI & Automation Lead",
                "company_name": "Optro",
                "job_description_text": (
                    "This role will identify automation opportunities, design AI-enabled "
                    "workflows, partner with frontline teams to eliminate manual work, "
                    "and pilot third-party AI and automated workflow solutions."
                ),
            }
        }
    )

    job_title: str | None = Field(default=None, description="Role title from the job posting.")
    company_name: str | None = Field(default=None, description="Company name.")
    job_description_text: str = Field(
        ...,
        min_length=1,
        description="Raw job description text content.",
    )


class JobDescriptionParseResponse(BaseModel):
    company: str | None
    title: str | None
    required_skills: list[str]
    preferred_skills: list[str]
    responsibilities: list[str]
    seniority: str | None
    industry: str | None
    keywords: list[str]
