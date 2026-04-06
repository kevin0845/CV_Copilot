import re
from dataclasses import dataclass

from app.schemas.analysis import AnalyzeResponse
from app.schemas.parse import (
    JobDescriptionParseResponse,
    ProjectItem,
    ResumeParseResponse,
    WorkExperienceItem,
)


STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "be",
    "build",
    "for",
    "in",
    "is",
    "of",
    "on",
    "or",
    "the",
    "to",
    "with",
}
WEIGHTS = {
    "required_skills": 40.0,
    "preferred_skills": 10.0,
    "experience_relevance": 25.0,
    "seniority_alignment": 15.0,
    "domain_fit": 10.0,
}
SENIORITY_LEVELS = {
    "intern": 1,
    "junior": 2,
    "mid-level": 3,
    "senior": 4,
    "lead": 5,
    "manager": 5,
    "staff": 6,
    "director": 6,
    "principal": 7,
    "executive": 8,
}
INDUSTRY_ALIASES = {
    "technology": ("technology", "software", "saas"),
    "fintech": ("fintech", "financial technology"),
    "finance": ("finance", "financial services", "banking"),
    "healthcare": ("healthcare", "health care", "medical"),
    "healthtech": ("healthtech", "digital health"),
    "education": ("education", "academic"),
    "edtech": ("edtech",),
    "retail": ("retail",),
    "e-commerce": ("e-commerce", "ecommerce"),
    "manufacturing": ("manufacturing",),
    "logistics": ("logistics", "supply chain"),
    "insurance": ("insurance", "insurtech"),
    "government": ("government", "public sector"),
    "cybersecurity": ("cybersecurity", "security"),
    "telecommunications": ("telecommunications", "telecom"),
    "media": ("media",),
    "marketing": ("marketing", "advertising"),
    "consulting": ("consulting",),
    "biotech": ("biotech", "biotechnology"),
    "nonprofit": ("nonprofit", "non-profit"),
}


@dataclass
class ResumeEvidence:
    label: str
    text: str


@dataclass
class MatchEvidence:
    target: str
    evidence: str
    label: str


def analyze_gap(
    resume: ResumeParseResponse,
    job: JobDescriptionParseResponse,
) -> AnalyzeResponse:
    resume_evidence = _build_resume_evidence(resume)
    strengths: list[str] = []
    gaps: list[str] = []
    evidence_notes: list[str] = []
    under_emphasized_experience: list[str] = []

    available_weight = 0.0
    weighted_score = 0.0

    matched_required, missing_required = _match_terms(job.required_skills, resume, resume_evidence)
    if job.required_skills:
        ratio = len(matched_required) / len(job.required_skills)
        available_weight += WEIGHTS["required_skills"]
        weighted_score += WEIGHTS["required_skills"] * ratio
        evidence_notes.append(
            f"Required skills: matched {len(matched_required)} of {len(job.required_skills)}."
        )
        strengths.extend(
            _format_skill_strengths("required skill", matched_required, limit=4)
        )
        gaps.extend(
            _format_missing_skill_gaps("required skill", missing_required, limit=4)
        )

    matched_preferred, missing_preferred = _match_terms(job.preferred_skills, resume, resume_evidence)
    if job.preferred_skills:
        ratio = len(matched_preferred) / len(job.preferred_skills)
        available_weight += WEIGHTS["preferred_skills"]
        weighted_score += WEIGHTS["preferred_skills"] * ratio
        evidence_notes.append(
            f"Preferred skills: matched {len(matched_preferred)} of {len(job.preferred_skills)}."
        )
        strengths.extend(
            _format_skill_strengths("preferred skill", matched_preferred, limit=2)
        )
        gaps.extend(
            _format_missing_skill_gaps("preferred skill", missing_preferred, limit=2)
        )

    matched_responsibilities, unmatched_responsibilities = _match_responsibilities(
        job.responsibilities,
        resume_evidence,
    )
    if job.responsibilities:
        ratio = len(matched_responsibilities) / len(job.responsibilities)
        available_weight += WEIGHTS["experience_relevance"]
        weighted_score += WEIGHTS["experience_relevance"] * ratio
        evidence_notes.append(
            "Experience relevance: matched "
            f"{len(matched_responsibilities)} of {len(job.responsibilities)} job responsibilities."
        )
        strengths.extend(
            _format_responsibility_strengths(matched_responsibilities, limit=3)
        )
        gaps.extend(
            _format_responsibility_gaps(unmatched_responsibilities, limit=3)
        )
        under_emphasized_experience.extend(
            _find_under_emphasized_experience(
                matched_responsibilities,
                resume,
                limit=3,
            )
        )

    seniority_result = _analyze_seniority_alignment(resume, job)
    if seniority_result["applicable"]:
        available_weight += WEIGHTS["seniority_alignment"]
        weighted_score += WEIGHTS["seniority_alignment"] * seniority_result["ratio"]
        evidence_notes.append(seniority_result["note"])
        if seniority_result["strength"]:
            strengths.append(seniority_result["strength"])
        if seniority_result["gap"]:
            gaps.append(seniority_result["gap"])

    domain_result = _analyze_domain_fit(resume, job, resume_evidence)
    if domain_result["applicable"]:
        available_weight += WEIGHTS["domain_fit"]
        weighted_score += WEIGHTS["domain_fit"] * domain_result["ratio"]
        evidence_notes.append(domain_result["note"])
        if domain_result["strength"]:
            strengths.append(domain_result["strength"])
        if domain_result["gap"]:
            gaps.append(domain_result["gap"])

    missing_keywords = _compute_missing_keywords(job, resume, resume_evidence)
    if missing_keywords:
        evidence_notes.append(
            "Missing keywords were derived from JD skills and keywords with no explicit resume evidence."
        )

    if available_weight == 0:
        match_score = 0.0
        evidence_notes.append(
            "No analyzable JD dimensions were present, so the match score defaulted to 0.0."
        )
    else:
        match_score = round((weighted_score / available_weight) * 100, 2)
        evidence_notes.append(
            f"Weighted score: {weighted_score:.2f} out of {available_weight:.2f}, normalized to {match_score:.2f}."
        )

    return AnalyzeResponse(
        match_score=match_score,
        strengths=_dedupe_preserve_order(strengths),
        gaps=_dedupe_preserve_order(gaps),
        missing_keywords=missing_keywords,
        under_emphasized_experience=_dedupe_preserve_order(under_emphasized_experience),
        evidence_notes=_dedupe_preserve_order(evidence_notes),
    )


def _build_resume_evidence(resume: ResumeParseResponse) -> list[ResumeEvidence]:
    evidence: list[ResumeEvidence] = []

    if resume.summary:
        evidence.append(ResumeEvidence(label="resume summary", text=resume.summary))

    for skill in resume.skills:
        evidence.append(ResumeEvidence(label="resume skill", text=skill))

    for item in resume.work_experience:
        if item.title:
            evidence.append(
                ResumeEvidence(
                    label=f"work title at {item.company or 'unknown company'}",
                    text=item.title,
                )
            )
        for bullet in item.bullets:
            evidence.append(
                ResumeEvidence(
                    label=f"work bullet at {item.company or 'unknown company'}",
                    text=bullet,
                )
            )

    for project in resume.projects:
        if project.name:
            evidence.append(ResumeEvidence(label="project name", text=project.name))
        if project.description:
            evidence.append(ResumeEvidence(label=f"project {project.name or 'description'}", text=project.description))
        for bullet in project.bullets:
            evidence.append(
                ResumeEvidence(
                    label=f"project bullet for {project.name or 'project'}",
                    text=bullet,
                )
            )

    for certification in resume.certifications:
        if certification.name:
            evidence.append(ResumeEvidence(label="certification", text=certification.name))

    for education in resume.education:
        if education.degree:
            evidence.append(ResumeEvidence(label="education degree", text=education.degree))
        for detail in education.details:
            evidence.append(ResumeEvidence(label="education detail", text=detail))

    return evidence


def _match_terms(
    terms: list[str],
    resume: ResumeParseResponse,
    evidence_items: list[ResumeEvidence],
) -> tuple[list[MatchEvidence], list[str]]:
    matched: list[MatchEvidence] = []
    missing: list[str] = []

    normalized_resume_skills = {skill.lower(): skill for skill in resume.skills}
    for term in terms:
        direct_skill = normalized_resume_skills.get(term.lower())
        if direct_skill:
            matched.append(
                MatchEvidence(
                    target=term,
                    evidence=direct_skill,
                    label="resume skills",
                )
            )
            continue

        evidence = _find_term_evidence(term, evidence_items)
        if evidence:
            matched.append(
                MatchEvidence(target=term, evidence=evidence.text, label=evidence.label)
            )
        else:
            missing.append(term)

    return matched, missing


def _match_responsibilities(
    responsibilities: list[str],
    evidence_items: list[ResumeEvidence],
) -> tuple[list[MatchEvidence], list[str]]:
    matched: list[MatchEvidence] = []
    missing: list[str] = []

    for responsibility in responsibilities:
        evidence = _find_responsibility_evidence(responsibility, evidence_items)
        if evidence:
            matched.append(
                MatchEvidence(
                    target=responsibility,
                    evidence=evidence.text,
                    label=evidence.label,
                )
            )
        else:
            missing.append(responsibility)

    return matched, missing


def _find_term_evidence(term: str, evidence_items: list[ResumeEvidence]) -> ResumeEvidence | None:
    normalized_term = _normalize_text(term)
    term_tokens = _meaningful_tokens(term)

    for evidence in evidence_items:
        normalized_evidence = _normalize_text(evidence.text)
        if normalized_term and normalized_term in normalized_evidence:
            return evidence

    best_match: ResumeEvidence | None = None
    best_overlap = 0
    for evidence in evidence_items:
        overlap = len(term_tokens & _meaningful_tokens(evidence.text))
        threshold = 1 if len(term_tokens) <= 2 else 2
        if overlap >= threshold and overlap > best_overlap:
            best_match = evidence
            best_overlap = overlap

    return best_match


def _find_responsibility_evidence(
    responsibility: str,
    evidence_items: list[ResumeEvidence],
) -> ResumeEvidence | None:
    target_tokens = _meaningful_tokens(responsibility)
    if not target_tokens:
        return None

    best_match: ResumeEvidence | None = None
    best_overlap = 0
    for evidence in evidence_items:
        overlap = len(target_tokens & _meaningful_tokens(evidence.text))
        threshold = 1 if len(target_tokens) <= 2 else 2
        if overlap >= threshold and overlap > best_overlap:
            best_match = evidence
            best_overlap = overlap

    return best_match


def _analyze_seniority_alignment(
    resume: ResumeParseResponse,
    job: JobDescriptionParseResponse,
) -> dict[str, object]:
    job_seniority = job.seniority
    if not job_seniority:
        return {"applicable": False, "ratio": 0.0, "note": "", "strength": None, "gap": None}

    resume_seniority, evidence = _extract_resume_seniority(resume.work_experience, resume.summary)
    if not resume_seniority:
        return {
            "applicable": True,
            "ratio": 0.0,
            "note": f"Seniority alignment: JD specifies '{job_seniority}', but the resume does not show an explicit seniority marker.",
            "strength": None,
            "gap": f"JD seniority is '{job_seniority}', but the resume does not explicitly show that level in the summary or work titles.",
        }

    resume_level = SENIORITY_LEVELS[resume_seniority]
    job_level = SENIORITY_LEVELS[job_seniority]
    if resume_level >= job_level:
        return {
            "applicable": True,
            "ratio": 1.0,
            "note": f"Seniority alignment: resume shows '{resume_seniority}' evidence in {evidence}.",
            "strength": f"Resume seniority aligns with the JD '{job_seniority}' level based on {evidence}.",
            "gap": None,
        }

    if resume_level == job_level - 1:
        return {
            "applicable": True,
            "ratio": 0.5,
            "note": f"Seniority alignment: resume shows '{resume_seniority}' in {evidence}, one level below the JD '{job_seniority}' signal.",
            "strength": None,
            "gap": f"JD seniority is '{job_seniority}', while the strongest resume seniority evidence is '{resume_seniority}' from {evidence}.",
        }

    return {
        "applicable": True,
        "ratio": 0.0,
        "note": f"Seniority alignment: resume seniority '{resume_seniority}' from {evidence} is below the JD '{job_seniority}' signal.",
        "strength": None,
        "gap": f"JD seniority is '{job_seniority}', but the resume evidence points to '{resume_seniority}' based on {evidence}.",
    }


def _analyze_domain_fit(
    resume: ResumeParseResponse,
    job: JobDescriptionParseResponse,
    evidence_items: list[ResumeEvidence],
) -> dict[str, object]:
    industry = job.industry
    if not industry:
        return {"applicable": False, "ratio": 0.0, "note": "", "strength": None, "gap": None}

    aliases = INDUSTRY_ALIASES.get(industry, (industry,))
    for alias in aliases:
        evidence = _find_term_evidence(alias, evidence_items)
        if evidence:
            return {
                "applicable": True,
                "ratio": 1.0,
                "note": f"Domain fit: found '{alias}' in {evidence.label}.",
                "strength": f"Resume explicitly mentions '{alias}', which supports the JD industry '{industry}'.",
                "gap": None,
            }

    return {
        "applicable": True,
        "ratio": 0.0,
        "note": f"Domain fit: JD industry is '{industry}', but no explicit industry terms were found in the resume.",
        "strength": None,
        "gap": f"JD industry is '{industry}', but the resume does not explicitly mention {industry}-related work.",
    }


def _extract_resume_seniority(
    work_experience: list[WorkExperienceItem],
    summary: str | None,
) -> tuple[str | None, str | None]:
    evidence_pool: list[tuple[str, str]] = []
    if summary:
        evidence_pool.append((summary, "the resume summary"))
    for item in work_experience:
        if item.title:
            company = item.company or "an unnamed company"
            evidence_pool.append((item.title, f"the title '{item.title}' at {company}"))

    best_label = None
    best_level = 0
    best_evidence = None
    for text, label in evidence_pool:
        normalized = text.lower()
        for seniority_label, level in SENIORITY_LEVELS.items():
            if re.search(rf"\b{re.escape(seniority_label)}\b", normalized):
                if level > best_level:
                    best_level = level
                    best_label = seniority_label
                    best_evidence = label

    return best_label, best_evidence


def _compute_missing_keywords(
    job: JobDescriptionParseResponse,
    resume: ResumeParseResponse,
    evidence_items: list[ResumeEvidence],
    limit: int = 10,
) -> list[str]:
    title_terms = set(_meaningful_tokens(job.title or ""))
    excluded = title_terms | ({job.seniority.lower()} if job.seniority else set())
    keyword_candidates = _dedupe_preserve_order(
        job.required_skills + job.preferred_skills + job.keywords
    )

    missing_keywords: list[str] = []
    for keyword in keyword_candidates:
        keyword_tokens = _meaningful_tokens(keyword)
        if not keyword_tokens:
            continue
        if keyword.lower() in excluded:
            continue
        if keyword.lower() in {skill.lower() for skill in resume.skills}:
            continue
        if _find_term_evidence(keyword, evidence_items):
            continue
        missing_keywords.append(keyword)
        if len(missing_keywords) >= limit:
            break

    return missing_keywords


def _find_under_emphasized_experience(
    matched_responsibilities: list[MatchEvidence],
    resume: ResumeParseResponse,
    limit: int,
) -> list[str]:
    explicit_skill_terms = {skill.lower() for skill in resume.skills}
    notes: list[str] = []

    for match in matched_responsibilities:
        evidence_lower = match.evidence.lower()
        target_lower = match.target.lower()
        if target_lower in evidence_lower:
            continue

        if match.label.startswith(("work bullet", "project bullet", "project ")):
            responsibility_tokens = _meaningful_tokens(match.target)
            missing_explicit_terms = [
                token for token in responsibility_tokens if token not in explicit_skill_terms
            ]
            if missing_explicit_terms:
                notes.append(
                    f"{match.label.capitalize()} '{match.evidence}' supports JD responsibility '{match.target}', but the resume does not state the JD wording explicitly."
                )
        if len(notes) >= limit:
            break

    return notes


def _format_skill_strengths(
    skill_type: str,
    matched: list[MatchEvidence],
    limit: int,
) -> list[str]:
    return [
        f"Resume matches the JD {skill_type} '{item.target}' through {item.label}: '{item.evidence}'."
        for item in matched[:limit]
    ]


def _format_missing_skill_gaps(
    skill_type: str,
    missing: list[str],
    limit: int,
) -> list[str]:
    return [
        f"JD lists '{term}' as a {skill_type}, but the resume does not explicitly mention it."
        for term in missing[:limit]
    ]


def _format_responsibility_strengths(
    matches: list[MatchEvidence],
    limit: int,
) -> list[str]:
    return [
        f"Resume evidence '{item.evidence}' in {item.label} aligns with the JD responsibility '{item.target}'."
        for item in matches[:limit]
    ]


def _format_responsibility_gaps(
    responsibilities: list[str],
    limit: int,
) -> list[str]:
    return [
        f"The resume does not show clear evidence for the JD responsibility '{responsibility}'."
        for responsibility in responsibilities[:limit]
    ]


def _normalize_text(text: str) -> str:
    return re.sub(r"[^a-z0-9+#]+", " ", text.lower()).strip()


def _meaningful_tokens(text: str) -> set[str]:
    return {
        _normalize_token(token)
        for token in _normalize_text(text).split()
        if token not in STOP_WORDS and len(token) > 2
    }


def _dedupe_preserve_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        cleaned = item.strip()
        if not cleaned:
            continue
        key = cleaned.lower()
        if key in seen:
            continue
        seen.add(key)
        ordered.append(cleaned)
    return ordered


def _normalize_token(token: str) -> str:
    irregular_forms = {
        "built": "build",
        "building": "build",
        "maintained": "maintain",
        "maintaining": "maintain",
        "collaborated": "collaborate",
        "collaborating": "collaborate",
        "designed": "design",
        "designing": "design",
    }
    if token in irregular_forms:
        return irregular_forms[token]
    if token.endswith("ies") and len(token) > 4:
        return token[:-3] + "y"
    if token.endswith("ing") and len(token) > 5:
        return token[:-3]
    if token.endswith("ed") and len(token) > 4:
        return token[:-2]
    if token.endswith("s") and len(token) > 4:
        return token[:-1]
    return token
