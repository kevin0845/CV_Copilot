# CV Copilot

CV Copilot is a resume-tailoring workspace built to help candidates compare their resume against a target job description, understand where the fit is strong or weak, and improve wording without inventing experience. The project currently includes a FastAPI backend for parsing and analysis plus a Next.js + Tailwind frontend with a polished single-page mock interface.

## Project Overview

CV Copilot turns unstructured resume files and job description text into structured, explainable guidance:

- Parse PDF and DOCX resumes into normalized plain text
- Convert resume text into structured JSON
- Parse job descriptions into deterministic structured fields
- Run rule-based gap analysis across skills, responsibilities, seniority, and domain fit
- Surface under-emphasized experience when the resume is relevant but phrased differently
- Generate rewrite suggestions that stay faithful to the candidate's existing background

## Features

### Backend

- FastAPI app organized into `app/api`, `app/services`, and `app/schemas`
- Resume upload parsing with `pypdf` and `python-docx`
- Structured resume output with:
  - `name`
  - `contact`
  - `summary`
  - `skills`
  - `work_experience`
  - `education`
  - `certifications`
  - `projects`
- Structured job description output with:
  - `company`
  - `title`
  - `required_skills`
  - `preferred_skills`
  - `responsibilities`
  - `seniority`
  - `industry`
  - `keywords`
- Explainable gap analysis output with:
  - `match_score`
  - `strengths`
  - `gaps`
  - `missing_keywords`
  - `under_emphasized_experience`
  - `evidence_notes`
- Conservative rewrite suggestions with:
  - `tailored_summary`
  - `rewrite_suggestions`

### Frontend

- Next.js + Tailwind single-page interface
- Left panel for:
  - resume upload
  - job description input
  - analysis trigger
- Right panel for:
  - match score card
  - strengths
  - gaps
  - missing keywords
  - under-emphasized experience
  - evidence notes
- Product-style mock results aligned to the current `/analyze` response schema

## Architecture

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
|   |   |-- globals.css
|   |   |-- layout.js
|   |   `-- page.js
|   `-- lib/
|       `-- mock-data.js
|-- sample-data/
|-- tests/
|-- requirements.txt
`-- README.md
```

Backend flow:

1. Upload a resume through `/parse-resume`.
2. Extract and normalize resume text.
3. Parse resume text into structured resume JSON.
4. Parse job description text into structured JD JSON.
5. Compare both objects in `/analyze`.
6. Optionally generate rewrite guidance in `/rewrite-suggestions`.

Frontend flow:

1. Select a resume file and paste a job description.
2. Click the analyze button.
3. Review the structured results layout on the right.
4. The current page uses mock analysis data until live API wiring is added.

## Local Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- npm

### Backend

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the FastAPI app:

```bash
uvicorn app.main:app --reload
```

Backend URLs:

- API root: `http://127.0.0.1:8000`
- Swagger docs: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

### Frontend

Install frontend dependencies:

```bash
cd frontend
npm install
```

Start the Next.js app:

```bash
npm run dev
```

Frontend URL:

- `http://localhost:3000`

## Using the UI

1. Open `http://localhost:3000`.
2. Upload a PDF or DOCX resume in the left panel.
3. Paste a target job description into the text area.
4. Click `Analyze role fit`.
5. Review the right-side results for:
   - score
   - strengths
   - gaps
   - missing keywords
   - under-emphasized experience
   - evidence notes

Current UI behavior:

- The interface is in mock mode for analysis results.
- Resume upload currently stores the selected filename in the UI.
- The displayed results are shaped to match the backend `/analyze` response.

## API Overview

### `GET /health`

Simple health check endpoint.

```json
{
  "status": "ok",
  "service": "cv-copilot"
}
```

### `POST /parse-resume`

Accepts multipart form data:

- `resume_file`: PDF or DOCX
- `candidate_name`: optional text field

Returns structured resume JSON including normalized text and extracted sections.

### `POST /parse-jd`

Accepts:

```json
{
  "job_title": "Customer Operations AI & Automation Lead",
  "company_name": "Optro",
  "job_description_text": "Full job description text here"
}
```

Returns:

- `company`
- `title`
- `required_skills`
- `preferred_skills`
- `responsibilities`
- `seniority`
- `industry`
- `keywords`

### `POST /analyze`

Accepts:

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

Sample text files are included for quick testing:

- [sample-data/sample-resume.txt](sample-data/sample-resume.txt)
- [sample-data/sample-job-description.txt](sample-data/sample-job-description.txt)

They are useful for parser development, API smoke tests, and frontend demos.

## Future Improvements

- Wire the frontend directly to `/parse-resume`, `/parse-jd`, `/analyze`, and `/rewrite-suggestions`
- Add loading, validation, and error states in the frontend
- Replace mock frontend analysis with live backend data
- Expand parser coverage for more resume and JD formats
- Add broader automated tests for frontend and backend behavior
- Support exporting tailored summaries and resume suggestions
- Add authentication and saved analysis sessions

## Notes

- The parsing and analysis services are deterministic and rule-based by design.
- The gap analysis intentionally distinguishes between full gaps and under-emphasized but relevant experience.
- The rewrite service does not invent metrics, titles, projects, or achievements that are not already supported by the resume.
