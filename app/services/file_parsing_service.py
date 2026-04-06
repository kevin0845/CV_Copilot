from io import BytesIO
import re

from docx import Document
from pypdf import PdfReader


SUPPORTED_RESUME_EXTENSIONS = {".pdf", ".docx"}
WHITESPACE_PATTERN = re.compile(r"\s+")


class FileParsingError(Exception):
    """Base error for resume file parsing."""


class UnsupportedResumeFileError(FileParsingError):
    """Raised when the uploaded resume format is not supported."""


class CorruptedResumeFileError(FileParsingError):
    """Raised when the uploaded file cannot be read as a valid resume document."""


def extract_text_from_resume_file(filename: str | None, content: bytes) -> str:
    extension = _get_extension(filename)

    if extension not in SUPPORTED_RESUME_EXTENSIONS:
        raise UnsupportedResumeFileError(
            "Unsupported file type. Please upload a PDF or DOCX resume."
        )

    if not content:
        raise CorruptedResumeFileError("The uploaded file is empty or unreadable.")

    if extension == ".pdf":
        raw_text = _extract_text_from_pdf(content)
    else:
        raw_text = _extract_text_from_docx(content)

    normalized_text = normalize_text(raw_text)
    if not normalized_text:
        raise CorruptedResumeFileError(
            "No readable text could be extracted from the uploaded file."
        )

    return normalized_text


def normalize_text(text: str) -> str:
    normalized_lines = []
    for line in text.splitlines():
        compact_line = WHITESPACE_PATTERN.sub(" ", line).strip()
        if compact_line:
            normalized_lines.append(compact_line)
    return "\n".join(normalized_lines)


def _get_extension(filename: str | None) -> str:
    if not filename or "." not in filename:
        return ""
    return "." + filename.rsplit(".", 1)[1].lower()


def _extract_text_from_pdf(content: bytes) -> str:
    try:
        reader = PdfReader(BytesIO(content))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception as exc:
        raise CorruptedResumeFileError(
            "The PDF file appears to be corrupted or could not be parsed."
        ) from exc


def _extract_text_from_docx(content: bytes) -> str:
    try:
        document = Document(BytesIO(content))
        return "\n".join(paragraph.text for paragraph in document.paragraphs)
    except Exception as exc:
        raise CorruptedResumeFileError(
            "The DOCX file appears to be corrupted or could not be parsed."
        ) from exc
