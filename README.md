# CV Copilot

CV Copilot is a resume-tailoring workspace built to help candidates compare a resume against a target job description, understand where the fit is strong or weak, and improve wording without inventing experience. The project includes a FastAPI backend for parsing and analysis plus a Next.js + Tailwind frontend that can run live analysis against the local backend.

## Project Overview

CV Copilot turns unstructured resume files and job description text into structured, explainable guidance:

- Parse PDF and DOCX resumes into normalized plain text
- Convert resume text into structured JSON
- Parse job descriptions into deterministic structured fields
- Run rule-based gap analysis across skills, responsibilities, seniority, and domain fit
- Surface under-emphasized experience when the resume is relevant but phrased differently
- Suggest revised bullets for hidden relevance without changing job titles or inventing new claims
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
- Hidden Relevance output that pairs concise resume evidence with a suggested revised bullet
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
  - hidden relevance with suggested revised bullets
  - evidence notes
- Live backend mode for uploaded resumes and pasted job descriptions
- Preview mode fallback when a resume is missing or the backend request fails

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
|       |-- api.js
|       |-- mock-analysis.js
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
2. Click `Analyze role fit`.
3. Frontend calls `/parse-resume`, `/parse-jd`, and `/analyze`.
4. Review the structured results layout on the right.
5. If the backend is unavailable, the UI falls back to preview mode with mock analysis.

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

The backend allows local frontend requests from:

- `http://localhost:3000`
- `http://127.0.0.1:3000`

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

The frontend uses `http://127.0.0.1:8000` as the backend URL by default. To point the UI at another backend, set:

```bash
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

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
   - hidden relevance
   - suggested revised bullets
   - evidence notes

Current UI behavior:

- `Live backend` means the uploaded resume and pasted JD were parsed and analyzed by FastAPI.
- `Preview mode` means the frontend is using mock analysis because a resume was not uploaded or the backend request failed.
- Hidden Relevance cards show the detected relevance first, then a suggested revised bullet in a separate green-highlighted block.

## Hidden Relevance Behavior

Hidden Relevance is used when the resume contains relevant experience but the wording does not clearly mirror the JD. The analyzer returns a concise evidence note plus a suggested revised bullet in the same `under_emphasized_experience` string.

Example:

```text
Automated manual business processes supports 'Partner with frontline teams to reduce manual work'. || Suggested bullet: Automated manual business processes to emphasize automation and manual-work reduction.
```

The frontend splits that string into two visual areas:

- The evidence note is displayed as the hidden relevance.
- The suggested revised bullet is displayed in a green-highlighted block.

The analyzer does not use job titles as Hidden Relevance suggestions because titles are not editable resume bullets.

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

Example `under_emphasized_experience` item:

```text
Developed an internal AI tool supports 'Design AI-enabled workflows'. || Suggested bullet: Developed an internal AI tool to emphasize AI-enabled workflow experience.
```

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

## Testing

Run focused backend tests:

```bash
python -m unittest tests.test_gap_analysis_service tests.test_jd_parser_service
```

Run a Python syntax check across backend code and tests:

```bash
python -c "import pathlib; [compile(path.read_text(encoding='utf-8'), str(path), 'exec') for path in pathlib.Path('app').rglob('*.py')]; [compile(path.read_text(encoding='utf-8'), str(path), 'exec') for path in pathlib.Path('tests').rglob('*.py')]; print('syntax ok')"
```

Run a frontend production build:

```bash
cd frontend
npm run build
```

If `next build` fails on Windows with an `EPERM` error under `frontend/.next`, stop the active dev server or remove the locked `.next` directory and rerun the build.

## Future Improvements

- Wire `/rewrite-suggestions` into the frontend results workflow
- Add richer loading, validation, and error states in the frontend
- Expand parser coverage for more resume and JD formats
- Add broader automated tests for frontend and backend behavior
- Support exporting tailored summaries and resume suggestions
- Add authentication and saved analysis sessions

## Notes

- The parsing and analysis services are deterministic and rule-based by design.
- The gap analysis intentionally distinguishes between full gaps and under-emphasized but relevant experience.
- Hidden Relevance suggests revised bullets only from editable resume evidence, not work experience titles.
- The rewrite service does not invent metrics, titles, projects, or achievements that are not already supported by the resume.
