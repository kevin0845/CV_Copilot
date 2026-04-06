import re
from collections import Counter

from app.schemas.parse import JobDescriptionParseRequest, JobDescriptionParseResponse


WORD_PATTERN = re.compile(r"\b[a-zA-Z][a-zA-Z0-9+\-#.]{1,}\b")
BULLET_PREFIX_PATTERN = re.compile(r"^(?:[-*]\s+|\d+\.\s+)")
HEADING_CLEAN_PATTERN = re.compile(r"[^a-z]+")
CHARACTER_TRANSLATION = str.maketrans(
    {
        "\u2022": "-",
        "\u2013": "-",
        "\u2014": "-",
    }
)
STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "be",
    "building",
    "for",
    "in",
    "is",
    "of",
    "on",
    "or",
    "our",
    "the",
    "to",
    "we",
    "with",
    "you",
    "your",
}
SECTION_ALIASES = {
    "requirements": "required_skills",
    "requiredskills": "required_skills",
    "minimumqualifications": "required_skills",
    "basicqualifications": "required_skills",
    "qualifications": "required_skills",
    "whatareyoubring": "required_skills",
    "preferredskills": "preferred_skills",
    "preferredqualifications": "preferred_skills",
    "nicetohave": "preferred_skills",
    "bonuspoints": "preferred_skills",
    "responsibilities": "responsibilities",
    "whatyoulldo": "responsibilities",
    "whatyouwilldo": "responsibilities",
    "roleoverview": "responsibilities",
    "duties": "responsibilities",
    "keyresponsibilities": "responsibilities",
}
ROLE_HINTS = {
    "engineer",
    "developer",
    "manager",
    "analyst",
    "consultant",
    "specialist",
    "architect",
    "scientist",
    "designer",
    "coordinator",
    "administrator",
    "recruiter",
    "marketer",
    "accountant",
    "director",
    "lead",
    "intern",
    "associate",
    "officer",
}
SENIORITY_PATTERNS = [
    ("intern", re.compile(r"\bintern(ship)?\b", re.IGNORECASE)),
    ("junior", re.compile(r"\b(junior|jr\.?)\b", re.IGNORECASE)),
    ("mid-level", re.compile(r"\b(mid|mid-level|intermediate)\b", re.IGNORECASE)),
    ("senior", re.compile(r"\b(senior|sr\.?)\b", re.IGNORECASE)),
    ("lead", re.compile(r"\blead\b", re.IGNORECASE)),
    ("staff", re.compile(r"\bstaff\b", re.IGNORECASE)),
    ("principal", re.compile(r"\bprincipal\b", re.IGNORECASE)),
    ("manager", re.compile(r"\bmanager\b", re.IGNORECASE)),
    ("director", re.compile(r"\bdirector\b", re.IGNORECASE)),
    ("executive", re.compile(r"\b(vp|vice president|head|chief|executive)\b", re.IGNORECASE)),
]
INDUSTRY_TERMS = {
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
SKILL_SIGNAL_PATTERNS = [
    re.compile(r"(?i)(?:experience|expertise|proficiency|proficient|knowledge|familiarity)\s+(?:with|in)\s+(.+)$"),
    re.compile(r"(?i)(?:understanding|command)\s+of\s+(.+)$"),
    re.compile(r"(?i)(?:must have|should have|nice to have)\s+(.+)$"),
]


def parse_job_description(
    payload: JobDescriptionParseRequest,
) -> JobDescriptionParseResponse:
    lines = _split_lines(payload.job_description_text)
    sections = _partition_sections(lines)
    title = _extract_title(lines)
    company = _extract_company(lines, title)
    required_skills = _parse_skill_section(sections.get("required_skills", []))
    preferred_skills = _parse_skill_section(sections.get("preferred_skills", []))
    responsibilities = _parse_responsibilities(sections.get("responsibilities", []))
    seniority = _extract_seniority(payload.job_description_text, title)
    industry = _extract_industry(payload.job_description_text)
    keywords = _extract_keywords(
        payload.job_description_text,
        required_skills,
        preferred_skills,
        responsibilities,
        title,
        seniority,
        industry,
    )

    return JobDescriptionParseResponse(
        company=company,
        title=title,
        required_skills=required_skills,
        preferred_skills=preferred_skills,
        responsibilities=responsibilities,
        seniority=seniority,
        industry=industry,
        keywords=keywords,
    )


def _split_lines(text: str) -> list[str]:
    return [
        line.translate(CHARACTER_TRANSLATION).strip()
        for line in text.splitlines()
        if line.strip()
    ]


def _partition_sections(lines: list[str]) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    current_section: str | None = None

    for line in lines:
        section_name = _canonical_section_name(line)
        if section_name:
            current_section = section_name
            sections.setdefault(section_name, [])
            continue

        if current_section is not None:
            sections.setdefault(current_section, []).append(line)

    return sections


def _canonical_section_name(line: str) -> str | None:
    cleaned = HEADING_CLEAN_PATTERN.sub("", line.lower())
    return SECTION_ALIASES.get(cleaned)


def _extract_title(lines: list[str]) -> str | None:
    for line in lines[:8]:
        lowered = line.lower()
        if _canonical_section_name(line):
            continue
        if lowered.startswith(("company:", "about us", "location:", "team:")):
            continue
        if len(line.split()) > 10:
            continue
        if any(hint in lowered.split() for hint in ROLE_HINTS):
            return line
    return None


def _extract_company(lines: list[str], title: str | None) -> str | None:
    for line in lines[:12]:
        lowered = line.lower()
        if lowered.startswith("company:"):
            value = line.split(":", 1)[1].strip()
            return value or None

    for line in lines[:12]:
        match = re.match(r"(?i)about\s+([A-Z][A-Za-z0-9&.,' -]+)$", line)
        if match:
            return match.group(1).strip()

    if title:
        for index, line in enumerate(lines[:8]):
            if line == title:
                if index + 1 < len(lines):
                    candidate = lines[index + 1]
                    if _looks_like_company(candidate):
                        return candidate
                if index > 0:
                    candidate = lines[index - 1]
                    if _looks_like_company(candidate):
                        return candidate
    return None


def _parse_skill_section(lines: list[str]) -> list[str]:
    skills: list[str] = []
    for line in lines:
        cleaned = _clean_bullet(line)
        skills.extend(_extract_skill_candidates(cleaned))
    return _dedupe_preserve_order(skills)


def _parse_responsibilities(lines: list[str]) -> list[str]:
    responsibilities: list[str] = []
    for line in lines:
        cleaned = _clean_bullet(line)
        if cleaned:
            responsibilities.append(cleaned)
    return responsibilities


def _extract_skill_candidates(line: str) -> list[str]:
    if not line:
        return []

    working_line = line
    if ":" in working_line and len(working_line.split(":", 1)[0].split()) <= 3:
        working_line = working_line.split(":", 1)[1].strip()

    for pattern in SKILL_SIGNAL_PATTERNS:
        match = pattern.search(working_line)
        if match:
            working_line = match.group(1).strip().rstrip(".")
            break

    if len(working_line.split()) <= 1:
        return [working_line] if working_line else []

    if any(separator in working_line for separator in ("|", ",", ";", "/")):
        parts = re.split(r"[|,;/]+", working_line)
        return [part.strip().rstrip(".") for part in parts if part.strip()]

    if " and " in working_line and len(working_line.split()) <= 12:
        parts = working_line.split(" and ")
        return [part.strip().rstrip(".") for part in parts if part.strip()]

    return [working_line.rstrip(".")] if len(working_line.split()) <= 8 else []


def _extract_seniority(text: str, title: str | None) -> str | None:
    search_space = f"{title or ''}\n{text}"
    for label, pattern in SENIORITY_PATTERNS:
        if pattern.search(search_space):
            return label
    return None


def _extract_industry(text: str) -> str | None:
    lowered = text.lower()
    for label, aliases in INDUSTRY_TERMS.items():
        for alias in aliases:
            if alias in lowered:
                return label
    return None


def _extract_keywords(
    text: str,
    required_skills: list[str],
    preferred_skills: list[str],
    responsibilities: list[str],
    title: str | None,
    seniority: str | None,
    industry: str | None,
    limit: int = 12,
) -> list[str]:
    explicit_keywords = _dedupe_preserve_order(
        required_skills
        + preferred_skills
        + _extract_keywords_from_title(title)
        + ([seniority] if seniority else [])
        + ([industry] if industry else [])
    )

    if len(explicit_keywords) >= limit:
        return explicit_keywords[:limit]

    token_counts = Counter(
        token.lower()
        for token in WORD_PATTERN.findall(text)
        if token.lower() not in STOP_WORDS and len(token) > 2
    )
    fallback_tokens = [
        token
        for token, _ in token_counts.most_common(limit)
        if token.lower() not in {keyword.lower() for keyword in explicit_keywords}
        and token.lower() not in {"responsibilities", "requirements", "qualifications"}
    ]

    return (explicit_keywords + fallback_tokens)[:limit]


def _extract_keywords_from_title(title: str | None) -> list[str]:
    if not title:
        return []
    return [
        token
        for token in re.split(r"\s+", title)
        if token and token.lower() not in STOP_WORDS
    ]


def _looks_like_company(value: str) -> bool:
    if _canonical_section_name(value):
        return False
    if len(value.split()) > 8:
        return False
    if any(character.isdigit() for character in value):
        return False
    if any(hint in value.lower().split() for hint in ROLE_HINTS):
        return False
    return any(token[:1].isupper() for token in value.split())


def _clean_bullet(line: str) -> str:
    return BULLET_PREFIX_PATTERN.sub("", line).strip()


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
