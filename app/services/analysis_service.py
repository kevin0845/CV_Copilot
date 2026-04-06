from app.schemas.analysis import AnalyzeRequest, AnalyzeResponse
from app.services.gap_analysis_service import analyze_gap


def analyze_resume_against_job(payload: AnalyzeRequest) -> AnalyzeResponse:
    return analyze_gap(
        resume=payload.parsed_resume,
        job=payload.parsed_job_description,
    )
