import re

from app.schemas.parse import JobDescriptionParseRequest, JobDescriptionParseResponse


WORD_PATTERN = re.compile(r"\b[a-zA-Z][a-zA-Z0-9-]{2,}\b")
BULLET_PREFIX_PATTERN = re.compile(r"^(?:[-*]\s+|\d+\.\s+)")
HEADING_CLEAN_PATTERN = re.compile(r"[^a-z]+")
CHARACTER_TRANSLATION = str.maketrans(
    {
        "\u2022": "-",
        "\u2013": "-",
        "\u2014": "-",
    }
)
YEARS_EXPERIENCE_PATTERN = re.compile(
    r"\b\d+\+?\s+years?(?:\s+of\s+experience)?\b",
    re.IGNORECASE,
)
KNOWN_SKILLS = [
    "SQL",
    "Python",
    "Workato",
    "Zapier",
    "Make",
    "Salesforce",
    "Gainsight",
    "Zendesk",
    "Snowflake",
    "REST APIs",
    "JSON",
    "webhooks",
    "LLM",
    "ChatGPT",
    "Gemini",
]
SKILL_PATTERNS = [
    ("SQL", re.compile(r"\bsql\b", re.IGNORECASE)),
    ("Python", re.compile(r"\bpython\b", re.IGNORECASE)),
    ("Workato", re.compile(r"\bworkato\b", re.IGNORECASE)),
    ("Zapier", re.compile(r"\bzapier\b", re.IGNORECASE)),
    ("Make", re.compile(r"\bmake\b", re.IGNORECASE)),
    ("Salesforce", re.compile(r"\bsalesforce\b", re.IGNORECASE)),
    ("Gainsight", re.compile(r"\bgainsight\b", re.IGNORECASE)),
    ("Zendesk", re.compile(r"\bzendesk\b", re.IGNORECASE)),
    ("Snowflake", re.compile(r"\bsnowflake\b", re.IGNORECASE)),
    ("REST APIs", re.compile(r"\brest api(?:s)?\b", re.IGNORECASE)),
    ("JSON", re.compile(r"\bjson\b", re.IGNORECASE)),
    ("webhooks", re.compile(r"\bwebhooks?\b", re.IGNORECASE)),
    ("LLM", re.compile(r"\bllms?\b", re.IGNORECASE)),
    ("ChatGPT", re.compile(r"\bchatgpt\b", re.IGNORECASE)),
    ("Gemini", re.compile(r"\bgemini\b", re.IGNORECASE)),
]
STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "be",
    "by",
    "for",
    "from",
    "in",
    "into",
    "is",
    "it",
    "of",
    "on",
    "or",
    "our",
    "role",
    "that",
    "the",
    "their",
    "this",
    "to",
    "using",
    "we",
    "will",
    "with",
    "you",
    "your",
}
GENERIC_KEYWORD_EXCLUSIONS = {
    "company",
    "customers",
    "experience",
    "identify",
    "include",
    "manual",
    "opportunities",
    "partner",
    "pilot",
    "responsibilities",
    "requirements",
    "solutions",
    "teams",
    "work",
}
SECTION_ALIASES = {
    "requirements": "required_skills",
    "requiredskills": "required_skills",
    "minimumqualifications": "required_skills",
    "basicqualifications": "required_skills",
    "qualifications": "required_skills",
    "musthave": "required_skills",
    "musthaves": "required_skills",
    "whatyoullbring": "required_skills",
    "whatyouwillbring": "required_skills",
    "preferred": "preferred_skills",
    "preferredskills": "preferred_skills",
    "preferredqualifications": "preferred_skills",
    "nicetohave": "preferred_skills",
    "nicetohaves": "preferred_skills",
    "bonuspoints": "preferred_skills",
    "responsibilities": "responsibilities",
    "essentialresponsibilities": "responsibilities",
    "keyresponsibilities": "responsibilities",
    "roleoverview": "responsibilities",
    "whatyoulldo": "responsibilities",
    "whatyouwilldo": "responsibilities",
    "duties": "responsibilities",
}
PREFERRED_SIGNALS = (
    "preferred",
    "nice to have",
    "nice-to-have",
    "bonus",
    "plus",
)
REQUIRED_SIGNALS = (
    "requirements",
    "required",
    "must have",
    "must-have",
    "qualification",
    "experience with",
    "experience in",
    "proficiency in",
    "proficient in",
    "knowledge of",
    "familiarity with",
)
ACTION_LEAD_INS = (
    "you will ",
    "this role will ",
    "the role will ",
    "role will ",
    "responsibilities include ",
    "responsibility includes ",
    "responsible for ",
)
ACTION_VERBS = {
    "analyze",
    "automate",
    "build",
    "collaborate",
    "configure",
    "create",
    "define",
    "deliver",
    "design",
    "develop",
    "drive",
    "eliminate",
    "identify",
    "implement",
    "improve",
    "integrate",
    "lead",
    "maintain",
    "manage",
    "monitor",
    "optimize",
    "own",
    "partner",
    "pilot",
    "support",
}


def parse_job_description(
    payload: JobDescriptionParseRequest,
) -> JobDescriptionParseResponse:
    lines = _split_lines(payload.job_description_text)
    sections = _partition_sections(lines)
    sentences = _split_sentences(payload.job_description_text)

    required_lines = _collect_required_skill_lines(lines, sections, sentences)
    preferred_lines = _collect_preferred_skill_lines(lines, sections, sentences)
    responsibilities = _extract_responsibilities(sections, sentences)
    required_skills = _extract_skills(required_lines)
    preferred_skills = _extract_skills(preferred_lines)
    seniority = _extract_seniority(payload.job_description_text)
    industry = _extract_industry(payload.job_description_text)
    keywords = _extract_keywords(
        payload.job_description_text,
        responsibilities,
        required_skills,
        preferred_skills,
        payload.job_title,
        payload.company_name,
    )

    return JobDescriptionParseResponse(
        company=payload.company_name,
        title=payload.job_title,
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


def _split_sentences(text: str) -> list[str]:
    normalized_text = text.translate(CHARACTER_TRANSLATION).replace("\r", "\n")
    raw_sentences = re.split(r"(?<=[.!?])\s+|\n+", normalized_text)
    return [sentence.strip(" -\t") for sentence in raw_sentences if sentence.strip(" -\t")]


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


def _collect_required_skill_lines(
    lines: list[str],
    sections: dict[str, list[str]],
    sentences: list[str],
) -> list[str]:
    skill_lines = list(sections.get("required_skills", []))
    if skill_lines:
        return _dedupe_preserve_order(skill_lines)

    for sentence in sentences:
        if _is_preferred_signal_line(sentence):
            continue
        if _is_required_signal_line(sentence):
            skill_lines.append(sentence)

    return _dedupe_preserve_order(skill_lines)


def _collect_preferred_skill_lines(
    lines: list[str],
    sections: dict[str, list[str]],
    sentences: list[str],
) -> list[str]:
    skill_lines = list(sections.get("preferred_skills", []))
    if skill_lines:
        return _dedupe_preserve_order(skill_lines)

    for sentence in sentences:
        if _is_preferred_signal_line(sentence):
            skill_lines.append(sentence)

    return _dedupe_preserve_order(skill_lines)


def _extract_skills(lines: list[str]) -> list[str]:
    matches: list[str] = []
    for line in lines:
        cleaned = _clean_bullet(line)
        line_matches: list[tuple[int, str]] = []
        for skill_name, pattern in SKILL_PATTERNS:
            match = pattern.search(cleaned)
            if match:
                line_matches.append((match.start(), skill_name))
        for _, skill_name in sorted(line_matches, key=lambda item: item[0]):
            matches.append(skill_name)
    return _dedupe_preserve_order(matches)


def _extract_responsibilities(
    sections: dict[str, list[str]],
    sentences: list[str],
) -> list[str]:
    section_lines = sections.get("responsibilities", [])
    if section_lines:
        responsibilities = _extract_responsibilities_from_lines(section_lines)
        if responsibilities:
            return responsibilities

    return _extract_responsibilities_from_sentences(sentences)


def _extract_responsibilities_from_lines(lines: list[str]) -> list[str]:
    responsibilities: list[str] = []
    for line in lines:
        cleaned = _clean_bullet(line)
        if _looks_like_action_statement(cleaned):
            responsibilities.append(_format_responsibility(cleaned))
            continue

        clauses = _extract_action_clauses(cleaned)
        if clauses:
            responsibilities.extend(clauses)
    return _dedupe_preserve_order(responsibilities)


def _extract_responsibilities_from_sentences(sentences: list[str]) -> list[str]:
    responsibilities: list[str] = []
    for sentence in sentences:
        clauses = _extract_action_clauses(sentence)
        if clauses:
            responsibilities.extend(clauses)
    return _dedupe_preserve_order(responsibilities)


def _extract_action_clauses(text: str) -> list[str]:
    normalized = text.strip()
    lowered = normalized.lower()
    clause_source = None

    for lead_in in ACTION_LEAD_INS:
        if lead_in in lowered:
            start_index = lowered.index(lead_in) + len(lead_in)
            clause_source = normalized[start_index:]
            break

    if clause_source is None and _looks_like_action_statement(normalized):
        clause_source = normalized

    if clause_source is None:
        return []

    clause_source = clause_source.strip(" :.-")
    if not clause_source:
        return []

    raw_clauses = re.split(r",\s+and\s+|,\s+", clause_source)
    clauses = [
        _format_responsibility(clause)
        for clause in raw_clauses
        if _looks_like_action_statement(clause)
    ]
    return _dedupe_preserve_order(clauses)


def _looks_like_action_statement(text: str) -> bool:
    words = _normalize_words(text)
    return bool(words and words[0] in ACTION_VERBS)


def _extract_seniority(text: str) -> str | None:
    match = YEARS_EXPERIENCE_PATTERN.search(text)
    return match.group(0) if match else None


def _extract_industry(text: str) -> str | None:
    return "SaaS" if re.search(r"\bsaas\b", text, re.IGNORECASE) else None


def _extract_keywords(
    text: str,
    responsibilities: list[str],
    required_skills: list[str],
    preferred_skills: list[str],
    job_title: str | None,
    company_name: str | None,
    limit: int = 8,
) -> list[str]:
    excluded_terms = {
        token.lower()
        for token in _normalize_words(" ".join(required_skills + preferred_skills))
    }
    excluded_terms.update(token.lower() for token in _normalize_words(company_name or ""))
    excluded_terms.update(skill.lower() for skill in KNOWN_SKILLS)

    source_text = " ".join(responsibilities) if responsibilities else text
    tokens = WORD_PATTERN.findall(source_text.translate(CHARACTER_TRANSLATION))
    keywords: list[str] = []

    for token in tokens:
        lowered = token.lower()
        if lowered in STOP_WORDS or lowered in GENERIC_KEYWORD_EXCLUSIONS:
            continue
        if lowered in excluded_terms:
            continue
        if lowered in ACTION_VERBS:
            continue
        keywords.append(token)

    return _dedupe_preserve_order(keywords)[:limit]


def _is_required_signal_line(text: str) -> bool:
    lowered = text.lower()
    return any(signal in lowered for signal in REQUIRED_SIGNALS)


def _is_preferred_signal_line(text: str) -> bool:
    lowered = text.lower()
    return any(signal in lowered for signal in PREFERRED_SIGNALS)


def _clean_bullet(line: str) -> str:
    return BULLET_PREFIX_PATTERN.sub("", line).strip().rstrip(".")


def _format_responsibility(text: str) -> str:
    cleaned = _clean_bullet(text)
    if not cleaned:
        return ""
    return cleaned[0].upper() + cleaned[1:]


def _normalize_words(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z][a-zA-Z-]*", text.lower())


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
