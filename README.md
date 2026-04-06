# CV Copilot

CV Copilot is a resume-tailoring workspace that helps compare a candidate resume against a target job description, surface role-fit gaps, and generate faithful rewrite suggestions. The project currently includes a FastAPI backend for parsing and analysis plus a Next.js frontend with a clean single-page mock UI.

## Project Overview

The goal of CV Copilot is to turn unstructured resume and job description text into structured, explainable guidance:

- Parse resume uploads from PDF or DOCX into normalized text and structured JSON
- Parse raw job descriptions into deterministic structured fields
- Run explainable gap analysis across skills, experience relevance, seniority, and domain fit
- Generate rewrite suggestions that stay faithful to the candidate's existing experience
- Provide a frontend workspace for upload, job input, and analysis review

## Features

- FastAPI backend with modular `api`, `services`, and `schemas` packages
- Resume file parsing with `pypdf` and `python-docx`
- Structured resume parsing for:
  - `name`
  - `contact`
  - `summary`
  - `skills`
  - `work_experience`
  - `education`
  - `certifications`
  - `projects`
- Structured job description parsing for:
  - `company`
  - `title`
  - `required_skills`
  - `preferred_skills`
  - `responsibilities`
  - `seniority`
  - `industry`
  - `keywords`
- Explainable gap analysis with evidence-backed strengths and gaps
- Rewrite suggestion generation with:
  - `tailored_summary`
  - itemized `rewrite_suggestions`
- Next.js + Tailwind frontend with:
  - left-side resume upload and JD input
  - right-side analysis display
  - mock data flow while backend wiring is still pending

## Architecture

The repo is split into a Python backend and a separate frontend app:

```text
CV_Copilot/
|-- app/
|   |-- api/
|   |   |-- router.py
|   |   `-- routes/
|   |       |-- health.py
|   |       `-- analysis.py
|   |-- schemas/
|   |   |-- analysis.py
|   |   |-- health.py
|   |   |-- parse.py
|   |   `-- rewrite.py
|   `-- services/
|       |-- analysis_service.py
|       |-- file_parsing_service.py
|       |-- gap_analysis_service.py
|       |-- jd_parser_service.py
|       |-- rewrite_service.py
|       `-- resume_parser_service.py
|-- frontend/
|   |-- app/
|   `-- lib/
|-- sample-data/
|-- requirements.txt
`-- README.md
```

Backend flow:

1. Resume upload is converted to plain text.
2. Resume text is parsed into structured resume JSON.
3. Job description text is parsed into structured job JSON.
4. Gap analysis compares the two structured objects.
5. Rewrite suggestions use parsed data plus gap analysis output.

Frontend flow:

1. User selects a resume and pastes a job description.
2. The current UI uses mock analysis data for display.
3. The page is already shaped for future API integration.

## Local Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- npm

### Backend Setup

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

The backend will be available at:

- API root: `http://127.0.0.1:8000`
- Swagger docs: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

### Frontend Setup

Install frontend dependencies:

```bash
cd frontend
npm install
```

Start the Next.js app:

```bash
npm run dev
```

The frontend will be available at:

- `http://localhost:3000`

## API Overview

### `GET /health`

Simple health check endpoint.

Response:

```json
{
  "status": "ok",
  "service": "cv-copilot"
}
```

### `POST /parse-resume`

Accepts a multipart form upload with:

- `resume_file`: PDF or DOCX
- `candidate_name`: optional text field

Returns structured resume JSON including normalized text, extracted sections, and work experience items.

### `POST /parse-jd`

Accepts raw job description text in JSON:

```json
{
  "job_title": "Senior Backend Engineer",
  "company_name": "Acme Health",
  "job_description_text": "Full job description text here"
}
```

Returns structured job description JSON with company, title, required skills, preferred skills, responsibilities, seniority, industry, and keywords.

### `POST /analyze`

Accepts structured resume and structured job description objects:

```json
{
  "parsed_resume": { "...": "resume parser output" },
  "parsed_job_description": { "...": "job parser output" }
}
```

Returns:

- `match_score`
- `strengths`
- `gaps`
- `missing_keywords`
- `under_emphasized_experience`
- `evidence_notes`

### `POST /rewrite-suggestions`

Accepts:

```json
{
  "parsed_resume": { "...": "resume parser output" },
  "parsed_job_description": { "...": "job parser output" },
  "gap_analysis": { "...": "analyze output" }
}
```

Returns:

- `tailored_summary`
- `rewrite_suggestions`

Each rewrite suggestion contains:

- `original`
- `suggested`
- `rationale`

## Sample Data

Sample text files are included for quick local testing:

- [sample-data/sample-resume.txt](sample-data/sample-resume.txt)
- [sample-data/sample-job-description.txt](sample-data/sample-job-description.txt)

These are useful for:

- parser development
- API smoke tests
- frontend demo flows

## Future Improvements

- Wire the frontend to the live FastAPI backend
- Add persistent file storage or session-based analysis history
- Improve parser coverage for more resume and JD formats
- Add automated tests for parsing, scoring, and rewrite behavior
- Introduce stronger validation and error messaging in the frontend
- Support export flows for tailored summaries and rewrite suggestions
- Add authentication and user workspaces
- Replace mock frontend data with real upload and analysis requests

## Notes

- The current frontend is intentionally using mock data first.
- Parsing and rewrite suggestions are deterministic and conservative by design.
- The rewrite service avoids inventing metrics, titles, projects, or achievements that are not already present in the resume.
