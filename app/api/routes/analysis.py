from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.schemas.analysis import AnalyzeRequest, AnalyzeResponse
from app.schemas.parse import (
    JobDescriptionParseRequest,
    JobDescriptionParseResponse,
    ResumeParseRequest,
    ResumeParseResponse,
)
from app.schemas.rewrite import RewriteRequest, RewriteResponse
from app.services.analysis_service import analyze_resume_against_job
from app.services.file_parsing_service import (
    CorruptedResumeFileError,
    UnsupportedResumeFileError,
    extract_text_from_resume_file,
)
from app.services.jd_parser_service import parse_job_description
from app.services.resume_parser_service import parse_resume
from app.services.rewrite_service import build_rewrite_suggestions


router = APIRouter()


@router.post("/parse-resume", response_model=ResumeParseResponse)
async def parse_resume_endpoint(
    resume_file: UploadFile = File(...),
    candidate_name: str | None = Form(default=None),
) -> ResumeParseResponse:
    try:
        file_bytes = await resume_file.read()
        normalized_text = extract_text_from_resume_file(resume_file.filename, file_bytes)
    except UnsupportedResumeFileError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except CorruptedResumeFileError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    return parse_resume(
        ResumeParseRequest(
            candidate_name=candidate_name,
            source_filename=resume_file.filename,
            resume_text=normalized_text,
        )
    )


@router.post("/parse-jd", response_model=JobDescriptionParseResponse)
async def parse_jd_endpoint(
    payload: JobDescriptionParseRequest,
) -> JobDescriptionParseResponse:
    return parse_job_description(payload)


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_endpoint(payload: AnalyzeRequest) -> AnalyzeResponse:
    return analyze_resume_against_job(payload)


@router.post("/rewrite-suggestions", response_model=RewriteResponse)
async def rewrite_suggestions_endpoint(payload: RewriteRequest) -> RewriteResponse:
    return build_rewrite_suggestions(
        resume=payload.parsed_resume,
        job=payload.parsed_job_description,
        gap_analysis=payload.gap_analysis,
    )
