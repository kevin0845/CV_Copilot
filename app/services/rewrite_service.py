import re

from app.schemas.analysis import AnalyzeResponse
from app.schemas.parse import (
    JobDescriptionParseResponse,
    ProjectItem,
    ResumeParseResponse,
    WorkExperienceItem,
)
from app.schemas.rewrite import RewriteResponse, RewriteSuggestionItem


STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
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
VERB_NORMALIZATION = {
    "built": "build",
    "building": "build",
    "builds": "build",
    "maintained": "maintain",
    "maintaining": "maintain",
    "maintains": "maintain",
    "collaborated": "collaborate",
    "collaborating": "collaborate",
    "collaborates": "collaborate",
    "designed": "design",
    "designing": "design",
    "designs": "design",
    "implemented": "implement",
    "implementing": "implement",
    "implements": "implement",
    "led": "lead",
    "leading": "lead",
    "managed": "manage",
    "managing": "manage",
    "supports": "support",
    "supported": "support",
    "supporting": "support",
}


def build_rewrite_suggestions(
    resume: ResumeParseResponse,
    job: JobDescriptionParseResponse,
    gap_analysis: AnalyzeResponse,
) -> RewriteResponse:
    tailored_summary = _build_tailored_summary(resume, job)
    suggestions: list[RewriteSuggestionItem] = []

    if resume.summary and tailored_summary and _normalize_text(tailored_summary) != _normalize_text(resume.summary):
        suggestions.append(
            RewriteSuggestionItem(
                original=resume.summary,
                suggested=tailored_summary,
                rationale="Reorders existing experience, skills, and domain language to align more directly with the target role without adding new claims.",
            )
        )

    skills_suggestion = _build_skills_suggestion(resume, job)
    if skills_suggestion:
        suggestions.append(skills_suggestion)

    bullet_suggestions = _build_experience_suggestions(resume, job, gap_analysis, limit=4)
    suggestions.extend(bullet_suggestions)

    if not suggestions and tailored_summary and not resume.summary:
        suggestions.append(
            RewriteSuggestionItem(
                original="",
                suggested=tailored_summary,
                rationale="Creates a summary using only the candidate's existing title, skills, and domain evidence from the parsed resume.",
            )
        )

    return RewriteResponse(
        tailored_summary=tailored_summary,
        rewrite_suggestions=suggestions,
    )


def _build_tailored_summary(
    resume: ResumeParseResponse,
    job: JobDescriptionParseResponse,
) -> str | None:
    title = _choose_resume_title(resume)
    matched_skills = _matched_skills(resume.skills, job)
    industry_phrase = _industry_phrase(resume, job)
    collaboration_phrase = _collaboration_phrase(resume, job)

    summary_parts: list[str] = []

    if title:
        summary_parts.append(title)
    elif resume.summary:
        summary_parts.append(_clean_sentence(resume.summary))

    if matched_skills:
        summary_parts.append(
            "with experience in " + _join_list(matched_skills[:3])
        )

    if industry_phrase:
        summary_parts.append(industry_phrase)

    if collaboration_phrase:
        summary_parts.append(collaboration_phrase)

    summary = " ".join(part.strip().rstrip(".") for part in summary_parts if part).strip()
    if not summary:
        return _clean_sentence(resume.summary) if resume.summary else None

    return _clean_sentence(summary)


def _build_skills_suggestion(
    resume: ResumeParseResponse,
    job: JobDescriptionParseResponse,
) -> RewriteSuggestionItem | None:
    if not resume.skills:
        return None

    matched = _matched_skills(resume.skills, job)
    if not matched:
        return None

    remaining_skills = [skill for skill in resume.skills if skill not in matched]
    reordered_skills = matched + remaining_skills
    if reordered_skills == resume.skills:
        return None

    return RewriteSuggestionItem(
        original=", ".join(resume.skills),
        suggested=", ".join(reordered_skills),
        rationale="Moves the most relevant existing skills to the front so the resume aligns faster with the job description.",
    )


def _build_experience_suggestions(
    resume: ResumeParseResponse,
    job: JobDescriptionParseResponse,
    gap_analysis: AnalyzeResponse,
    limit: int,
) -> list[RewriteSuggestionItem]:
    suggestions: list[RewriteSuggestionItem] = []
    responsibilities = job.responsibilities
    missing_keywords = {keyword.lower() for keyword in gap_analysis.missing_keywords}

    for item in resume.work_experience:
        item_context = _work_item_context(item)
        for bullet in item.bullets:
            best_responsibility = _best_matching_responsibility(bullet, responsibilities)
            if not best_responsibility:
                continue

            responsibility = best_responsibility
            overlap = _meaningful_tokens(bullet) & _meaningful_tokens(responsibility)
            candidate_terms = _responsibility_terms_supported_by_context(
                responsibility,
                item_context,
                missing_keywords,
            )
            if not candidate_terms and len(overlap) >= len(_meaningful_tokens(responsibility)):
                continue

            suggested = _rewrite_bullet(bullet, candidate_terms)
            if not suggested or _normalize_text(suggested) == _normalize_text(bullet):
                continue

            suggestions.append(
                RewriteSuggestionItem(
                    original=bullet,
                    suggested=suggested,
                    rationale=(
                        "Makes the existing experience more specific and closer to the target role language using only details already present in the same resume entry."
                    ),
                )
            )
            if len(suggestions) >= limit:
                return suggestions

    for project in resume.projects:
        project_suggestion = _build_project_suggestion(project, job, missing_keywords)
        if project_suggestion:
            suggestions.append(project_suggestion)
        if len(suggestions) >= limit:
            break

    return suggestions[:limit]


def _build_project_suggestion(
    project: ProjectItem,
    job: JobDescriptionParseResponse,
    missing_keywords: set[str],
) -> RewriteSuggestionItem | None:
    original = project.description
    if not original:
        return None

    matched_terms = _supported_terms_from_text(original, job.required_skills + job.preferred_skills)
    matched_terms = [term for term in matched_terms if term.lower() not in missing_keywords]
    if not matched_terms:
        return None

    suggested = original.rstrip(".")
    phrase = _join_list(matched_terms[:2])
    if phrase.lower() not in original.lower():
        suggested = f"{suggested}, highlighting {phrase}"
    suggested = _clean_sentence(suggested)

    if _normalize_text(suggested) == _normalize_text(original):
        return None

    return RewriteSuggestionItem(
        original=original,
        suggested=suggested,
        rationale="Clarifies how the existing project description connects to the target role using only skills already present in the project text.",
    )


def _best_matching_responsibility(
    bullet: str,
    responsibilities: list[str],
) -> str | None:
    bullet_tokens = _meaningful_tokens(bullet)
    best_match = None
    best_overlap = 0

    for responsibility in responsibilities:
        overlap = len(bullet_tokens & _meaningful_tokens(responsibility))
        if overlap > best_overlap:
            best_overlap = overlap
            best_match = responsibility

    if best_overlap == 0:
        return None
    return best_match


def _responsibility_terms_supported_by_context(
    responsibility: str,
    context: str,
    missing_keywords: set[str],
) -> list[str]:
    terms: list[str] = []
    context_tokens = _meaningful_tokens(context)

    for fragment in _split_responsibility_fragments(responsibility):
        normalized_fragment = fragment.lower()
        if normalized_fragment in missing_keywords:
            continue
        fragment_tokens = _meaningful_tokens(fragment)
        if fragment_tokens and fragment_tokens <= context_tokens:
            terms.append(fragment)

    return _dedupe_preserve_order(terms)


def _rewrite_bullet(original: str, supported_terms: list[str]) -> str | None:
    bullet = original.strip().rstrip(".")
    if not bullet:
        return None
    if not supported_terms:
        return None

    existing_tokens = _meaningful_tokens(bullet)
    additions = [
        term
        for term in supported_terms
        if not _meaningful_tokens(term) <= existing_tokens
    ]
    if not additions:
        return None

    addition_text = _join_list(additions[:2])
    if bullet.lower().startswith("collaborated"):
        return _clean_sentence(f"{bullet} to support {addition_text}")
    if bullet.lower().startswith("built"):
        return _clean_sentence(f"{bullet} focused on {addition_text}")
    if bullet.lower().startswith("implemented"):
        return _clean_sentence(f"{bullet} for {addition_text}")
    return _clean_sentence(f"{bullet} related to {addition_text}")


def _work_item_context(item: WorkExperienceItem) -> str:
    parts = [item.title or "", item.company or ""]
    parts.extend(item.bullets)
    return " ".join(part for part in parts if part)


def _matched_skills(skills: list[str], job: JobDescriptionParseResponse) -> list[str]:
    job_terms = _dedupe_preserve_order(job.required_skills + job.preferred_skills + job.keywords)
    matched: list[str] = []
    for term in job_terms:
        for skill in skills:
            if skill.lower() == term.lower():
                matched.append(skill)
                break
    return _dedupe_preserve_order(matched)


def _choose_resume_title(resume: ResumeParseResponse) -> str | None:
    for item in resume.work_experience:
        if item.title:
            return item.title
    return None


def _industry_phrase(
    resume: ResumeParseResponse,
    job: JobDescriptionParseResponse,
) -> str | None:
    if not job.industry:
        return None
    aliases = INDUSTRY_ALIASES.get(job.industry, (job.industry,))
    resume_text = " ".join(
        [
            resume.summary or "",
            " ".join(bullet for item in resume.work_experience for bullet in item.bullets),
            " ".join(project.description or "" for project in resume.projects),
        ]
    ).lower()
    for alias in aliases:
        if alias in resume_text:
            return f"in {job.industry}"
    return None


def _collaboration_phrase(
    resume: ResumeParseResponse,
    job: JobDescriptionParseResponse,
) -> str | None:
    responsibilities = " ".join(job.responsibilities).lower()
    if "collaborat" not in responsibilities:
        return None

    for item in resume.work_experience:
        for bullet in item.bullets:
            if "collaborat" in bullet.lower():
                return "and cross-functional collaboration"
    return None


def _supported_terms_from_text(text: str, terms: list[str]) -> list[str]:
    normalized_text = _normalize_text(text)
    matches: list[str] = []
    for term in terms:
        if _normalize_text(term) and _normalize_text(term) in normalized_text:
            matches.append(term)
    return _dedupe_preserve_order(matches)


def _split_responsibility_fragments(responsibility: str) -> list[str]:
    parts = [
        part.strip()
        for part in re.split(r"\band\b|,|/|\bto\b", responsibility, flags=re.IGNORECASE)
        if part.strip()
    ]
    return parts or [responsibility]


def _clean_sentence(text: str) -> str:
    compact = re.sub(r"\s+", " ", text).strip().rstrip(".")
    return f"{compact}." if compact else compact


def _join_list(items: list[str]) -> str:
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return ", ".join(items[:-1]) + f", and {items[-1]}"


def _normalize_text(text: str) -> str:
    return re.sub(r"[^a-z0-9+#]+", " ", text.lower()).strip()


def _meaningful_tokens(text: str) -> set[str]:
    return {
        _normalize_token(token)
        for token in _normalize_text(text).split()
        if token not in STOP_WORDS and len(token) > 2
    }


def _normalize_token(token: str) -> str:
    if token in VERB_NORMALIZATION:
        return VERB_NORMALIZATION[token]
    if token.endswith("ies") and len(token) > 4:
        return token[:-3] + "y"
    if token.endswith("ing") and len(token) > 5:
        return token[:-3]
    if token.endswith("ed") and len(token) > 4:
        return token[:-2]
    if token.endswith("s") and len(token) > 4:
        return token[:-1]
    return token


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
