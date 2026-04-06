import re
from typing import TypeVar

from app.schemas.parse import (
    CertificationItem,
    ContactInfo,
    EducationItem,
    ProjectItem,
    ResumeParseRequest,
    ResumeParseResponse,
    WorkExperienceItem,
)


EMAIL_PATTERN = re.compile(r"\b[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}\b", re.IGNORECASE)
PHONE_PATTERN = re.compile(
    r"(?:(?:\+?\d{1,2}[\s.\-]?)?(?:\(?\d{3}\)?[\s.\-]?)\d{3}[\s.\-]?\d{4})"
)
URL_PATTERN = re.compile(r"(https?://\S+|www\.\S+)", re.IGNORECASE)
LINKEDIN_PATTERN = re.compile(r"(https?://)?(www\.)?linkedin\.com/\S+", re.IGNORECASE)
GITHUB_PATTERN = re.compile(r"(https?://)?(www\.)?github\.com/\S+", re.IGNORECASE)
DATE_RANGE_PATTERN = re.compile(
    r"(?i)\b(?:"
    r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\s+\d{4}"
    r"|\d{1,2}/\d{4}"
    r"|\d{4}"
    r")\s*(?:-|to)\s*(?:"
    r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\s+\d{4}"
    r"|\d{1,2}/\d{4}"
    r"|\d{4}"
    r"|present|current"
    r")\b"
)
BULLET_PREFIX_PATTERN = re.compile(r"^(?:[-*]\s+|\d+\.\s+)")
HEADING_CLEAN_PATTERN = re.compile(r"[^a-z]+")
CHARACTER_TRANSLATION = str.maketrans(
    {
        "\u2022": "-",
        "\u2013": "-",
        "\u2014": "-",
    }
)
SECTION_ALIASES = {
    "summary": "summary",
    "professionalsummary": "summary",
    "profilesummary": "summary",
    "profile": "summary",
    "objective": "summary",
    "about": "summary",
    "skills": "skills",
    "technicalskills": "skills",
    "corecompetencies": "skills",
    "competencies": "skills",
    "expertise": "skills",
    "workexperience": "work_experience",
    "professionalexperience": "work_experience",
    "experience": "work_experience",
    "employmenthistory": "work_experience",
    "careerhistory": "work_experience",
    "education": "education",
    "academicbackground": "education",
    "certifications": "certifications",
    "certification": "certifications",
    "licenses": "certifications",
    "licensescertifications": "certifications",
    "projects": "projects",
    "projectexperience": "projects",
    "selectedprojects": "projects",
}
ROLE_HINTS = {
    "engineer",
    "developer",
    "manager",
    "analyst",
    "consultant",
    "specialist",
    "intern",
    "lead",
    "director",
    "architect",
    "designer",
    "administrator",
    "coordinator",
    "scientist",
    "owner",
    "founder",
    "president",
    "associate",
}
ORG_HINTS = {
    "inc",
    "llc",
    "corp",
    "corporation",
    "company",
    "co",
    "ltd",
    "technologies",
    "technology",
    "solutions",
    "systems",
    "group",
    "partners",
    "university",
    "college",
    "school",
    "hospital",
    "agency",
    "labs",
}
DEGREE_HINTS = {
    "bachelor",
    "master",
    "phd",
    "mba",
    "b.s",
    "b.a",
    "m.s",
    "m.a",
    "bs",
    "ba",
    "ms",
    "ma",
    "associate",
    "degree",
}

T = TypeVar("T")


def parse_resume(payload: ResumeParseRequest) -> ResumeParseResponse:
    lines = _split_lines(payload.resume_text)
    intro_lines, sections = _partition_resume_sections(lines)

    return ResumeParseResponse(
        source_filename=payload.source_filename,
        normalized_text=payload.resume_text,
        name=payload.candidate_name or _extract_name(intro_lines),
        contact=_extract_contact(intro_lines),
        summary=_extract_summary(intro_lines, sections.get("summary", [])),
        skills=_parse_skills(sections.get("skills", [])),
        work_experience=_parse_work_experience(sections.get("work_experience", [])),
        education=_parse_education(sections.get("education", [])),
        certifications=_parse_certifications(sections.get("certifications", [])),
        projects=_parse_projects(sections.get("projects", [])),
    )


def _split_lines(text: str) -> list[str]:
    return [
        line.translate(CHARACTER_TRANSLATION).strip()
        for line in text.splitlines()
        if line.strip()
    ]


def _partition_resume_sections(lines: list[str]) -> tuple[list[str], dict[str, list[str]]]:
    intro_lines: list[str] = []
    sections: dict[str, list[str]] = {}
    current_section: str | None = None

    for line in lines:
        section_name = _canonical_section_name(line)
        if section_name:
            current_section = section_name
            sections.setdefault(section_name, [])
            continue

        if current_section is None:
            intro_lines.append(line)
        else:
            sections.setdefault(current_section, []).append(line)

    return intro_lines, sections


def _canonical_section_name(line: str) -> str | None:
    cleaned = HEADING_CLEAN_PATTERN.sub("", line.lower())
    return SECTION_ALIASES.get(cleaned)


def _extract_name(lines: list[str]) -> str | None:
    for line in lines[:5]:
        if _looks_like_name(line):
            return line
    return None


def _extract_contact(lines: list[str]) -> ContactInfo | None:
    window = lines[:8]
    joined = " | ".join(window)

    email = _first_match(EMAIL_PATTERN, joined)
    phone = _first_match(PHONE_PATTERN, joined)
    linkedin = _first_match(LINKEDIN_PATTERN, joined)
    github = _first_match(GITHUB_PATTERN, joined)
    website = None

    for match in URL_PATTERN.findall(joined):
        if linkedin and linkedin in match:
            continue
        if github and github in match:
            continue
        website = match
        break

    location = None
    for line in window:
        if _looks_like_location(line):
            location = line
            break

    if any([email, phone, location, linkedin, github, website]):
        return ContactInfo(
            email=email,
            phone=phone,
            location=location,
            linkedin=linkedin,
            github=github,
            website=website,
        )
    return None


def _extract_summary(intro_lines: list[str], summary_lines: list[str]) -> str | None:
    if summary_lines:
        return _join_lines(summary_lines)

    candidate_lines = []
    for line in intro_lines[1:]:
        if _is_contact_line(line):
            continue
        if _looks_like_name(line):
            continue
        if len(line.split()) >= 8:
            candidate_lines.append(line)

    return _join_lines(candidate_lines[:2]) if candidate_lines else None


def _parse_skills(lines: list[str]) -> list[str]:
    raw_skills: list[str] = []

    for line in lines:
        cleaned = _clean_bullet(line)
        value = (
            cleaned.split(":", 1)[1].strip()
            if ":" in cleaned and len(cleaned.split(":", 1)[0].split()) <= 3
            else cleaned
        )
        parts = re.split(r"[|,/;]+", value)
        if len(parts) == 1 and len(value.split()) <= 6:
            raw_skills.append(value.strip())
            continue
        raw_skills.extend(part.strip() for part in parts if part.strip())

    return _dedupe_preserve_order([skill for skill in raw_skills if skill])


def _parse_work_experience(lines: list[str]) -> list[WorkExperienceItem]:
    entries: list[WorkExperienceItem] = []
    current: WorkExperienceItem | None = None
    index = 0

    while index < len(lines):
        line = lines[index]
        next_line = lines[index + 1] if index + 1 < len(lines) else None

        if _looks_like_two_line_work_header(line, next_line):
            current = _finalize_and_start(
                entries,
                current,
                _build_two_line_work_item(line, next_line or ""),
            )
            index += 2
            continue

        if _looks_like_one_line_work_header(line):
            current = _finalize_and_start(entries, current, _build_one_line_work_item(line))
            index += 1
            continue

        if current:
            bullet = _clean_bullet(line)
            if bullet:
                current.bullets.append(bullet)

        index += 1

    if current and _has_work_content(current):
        entries.append(current)

    return entries


def _parse_education(lines: list[str]) -> list[EducationItem]:
    items: list[EducationItem] = []
    current: EducationItem | None = None

    for line in lines:
        cleaned = _clean_bullet(line)
        if _looks_like_education_header(cleaned):
            current = _finalize_and_start(items, current, _build_education_item(cleaned))
            continue

        if current:
            current.details.append(cleaned)
        elif cleaned:
            current = _build_education_item(cleaned)

    if current and _has_education_content(current):
        items.append(current)

    return items


def _parse_certifications(lines: list[str]) -> list[CertificationItem]:
    items: list[CertificationItem] = []

    for line in lines:
        cleaned = _clean_bullet(line)
        if not cleaned:
            continue

        date_range = _extract_date_range(cleaned)
        content = cleaned.replace(date_range, "").strip(" |-(),") if date_range else cleaned
        parts = [
            part.strip()
            for part in re.split(r"\s+\|\s+|\s+-\s+|,\s*", content)
            if part.strip()
        ]

        name = parts[0] if parts else None
        issuer = parts[1] if len(parts) > 1 else None
        if name:
            items.append(CertificationItem(name=name, issuer=issuer, date_range=date_range))

    return items


def _parse_projects(lines: list[str]) -> list[ProjectItem]:
    items: list[ProjectItem] = []
    current: ProjectItem | None = None

    for line in lines:
        cleaned = _clean_bullet(line)
        if _looks_like_project_header(line):
            current = _finalize_and_start(items, current, _build_project_item(cleaned))
            continue

        if current:
            if line.startswith(("-", "*")) or BULLET_PREFIX_PATTERN.match(line):
                current.bullets.append(cleaned)
            elif current.description is None:
                current.description = cleaned
            else:
                current.bullets.append(cleaned)
        elif cleaned:
            current = _build_project_item(cleaned)

    if current and _has_project_content(current):
        items.append(current)

    return items


def _finalize_and_start(items: list[T], current: T | None, new_item: T) -> T:
    if current is not None and _has_content(current):
        items.append(current)
    return new_item


def _has_content(item: object) -> bool:
    if isinstance(item, WorkExperienceItem):
        return _has_work_content(item)
    if isinstance(item, EducationItem):
        return _has_education_content(item)
    if isinstance(item, ProjectItem):
        return _has_project_content(item)
    return True


def _has_work_content(item: WorkExperienceItem) -> bool:
    return any([item.company, item.title, item.date_range, item.bullets])


def _has_education_content(item: EducationItem) -> bool:
    return any([item.institution, item.degree, item.date_range, item.details])


def _has_project_content(item: ProjectItem) -> bool:
    return any([item.name, item.description, item.bullets])


def _build_one_line_work_item(line: str) -> WorkExperienceItem:
    date_range = _extract_date_range(line)
    header = line.replace(date_range, "").strip(" |-(),") if date_range else line.strip()
    company, title = _extract_company_and_title(header)
    return WorkExperienceItem(company=company, title=title, date_range=date_range, bullets=[])


def _build_two_line_work_item(line: str, next_line: str) -> WorkExperienceItem:
    date_range = _extract_date_range(next_line)
    secondary = next_line.replace(date_range, "").strip(" |-(),") if date_range else next_line.strip()

    first_line = line.strip()
    company = first_line if _looks_like_company(first_line) else None
    title = secondary or None

    if not company and _looks_like_company(secondary):
        company = secondary
        title = first_line if _looks_like_title(first_line) else None
    elif company and not _looks_like_title(title or ""):
        title = secondary or None

    if not company and not title:
        company, title = _extract_company_and_title(f"{first_line} | {secondary}")

    return WorkExperienceItem(company=company, title=title, date_range=date_range, bullets=[])


def _build_education_item(line: str) -> EducationItem:
    date_range = _extract_date_range(line)
    content = line.replace(date_range, "").strip(" |-(),") if date_range else line
    parts = [
        part.strip()
        for part in re.split(r"\s+\|\s+|\s+-\s+|,\s*", content)
        if part.strip()
    ]

    institution = None
    degree = None
    for part in parts:
        if institution is None and _looks_like_company(part):
            institution = part
            continue
        if degree is None and _looks_like_degree(part):
            degree = part

    if institution is None and parts:
        institution = parts[0] if len(parts) == 1 or _looks_like_company(parts[0]) else None
    if degree is None and len(parts) > 1:
        degree = parts[1]

    return EducationItem(
        institution=institution,
        degree=degree,
        date_range=date_range,
        details=[],
    )


def _build_project_item(line: str) -> ProjectItem:
    parts = [
        part.strip()
        for part in re.split(r"\s+\|\s+|\s+-\s+", line, maxsplit=1)
        if part.strip()
    ]
    if not parts:
        return ProjectItem(name=None, description=None, bullets=[])
    if len(parts) == 1:
        return ProjectItem(name=parts[0], description=None, bullets=[])
    return ProjectItem(name=parts[0], description=parts[1], bullets=[])


def _extract_company_and_title(header: str) -> tuple[str | None, str | None]:
    parts = [
        part.strip()
        for part in re.split(r"\s+\|\s+|\s+at\s+|\s+-\s+|,\s*", header)
        if part.strip()
    ]
    if len(parts) < 2:
        if not parts:
            return None, None
        if _looks_like_company(parts[0]):
            return parts[0], None
        if _looks_like_title(parts[0]):
            return None, parts[0]
        return None, None

    company = None
    title = None
    for part in parts:
        if company is None and _looks_like_company(part):
            company = part
            continue
        if title is None and _looks_like_title(part):
            title = part

    return company, title


def _extract_date_range(line: str) -> str | None:
    match = DATE_RANGE_PATTERN.search(line)
    return match.group(0) if match else None


def _looks_like_name(line: str) -> bool:
    lowered = line.lower()
    if any(token in lowered for token in ("@", "linkedin", "github", "http", ".com")):
        return False
    if any(character.isdigit() for character in line):
        return False
    if _canonical_section_name(line):
        return False

    words = line.replace("|", " ").split()
    if not 1 < len(words) <= 4:
        return False

    alpha_words = [
        word for word in words if re.fullmatch(r"[A-Za-z][A-Za-z'.-]*", word)
    ]
    return len(alpha_words) == len(words)


def _looks_like_location(line: str) -> bool:
    if _is_contact_line(line):
        return False
    return bool(re.search(r"\b[A-Za-z .'-]+,\s*[A-Z]{2}\b", line))


def _is_contact_line(line: str) -> bool:
    lowered = line.lower()
    return any(
        [
            bool(EMAIL_PATTERN.search(line)),
            bool(PHONE_PATTERN.search(line)),
            bool(URL_PATTERN.search(line)),
            "linkedin" in lowered,
            "github" in lowered,
        ]
    )


def _join_lines(lines: list[str]) -> str | None:
    cleaned = [line.strip() for line in lines if line.strip()]
    return " ".join(cleaned) if cleaned else None


def _clean_bullet(line: str) -> str:
    return BULLET_PREFIX_PATTERN.sub("", line).strip()


def _looks_like_one_line_work_header(line: str) -> bool:
    if BULLET_PREFIX_PATTERN.match(line):
        return False
    if not _extract_date_range(line):
        return False
    return len(line.split()) <= 16


def _looks_like_two_line_work_header(line: str, next_line: str | None) -> bool:
    if not next_line:
        return False
    if BULLET_PREFIX_PATTERN.match(line) or BULLET_PREFIX_PATTERN.match(next_line):
        return False
    if _extract_date_range(line):
        return False
    if not _extract_date_range(next_line):
        return False
    return len(line.split()) <= 8 and len(next_line.split()) <= 14


def _looks_like_education_header(line: str) -> bool:
    if BULLET_PREFIX_PATTERN.match(line):
        return False
    return bool(_looks_like_company(line) or _looks_like_degree(line) or _extract_date_range(line))


def _looks_like_project_header(line: str) -> bool:
    if BULLET_PREFIX_PATTERN.match(line):
        return False
    if _canonical_section_name(line):
        return False
    return len(line.split()) <= 10


def _looks_like_title(value: str) -> bool:
    lowered = value.lower()
    return any(hint in lowered.split() for hint in ROLE_HINTS)


def _looks_like_company(value: str) -> bool:
    lowered = value.lower()
    if any(hint in lowered.split() for hint in ORG_HINTS):
        return True
    return any(token.istitle() for token in value.split()) and len(value.split()) <= 8


def _looks_like_degree(value: str) -> bool:
    lowered = value.lower()
    return any(hint in lowered for hint in DEGREE_HINTS)


def _dedupe_preserve_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        key = item.lower()
        if key in seen:
            continue
        seen.add(key)
        ordered.append(item)
    return ordered


def _first_match(pattern: re.Pattern[str], text: str) -> str | None:
    match = pattern.search(text)
    return match.group(0) if match else None
