const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";


const buildUrl = (path) => `${API_BASE_URL}${path}`;

const parseErrorDetail = async (response) => {
  try {
    const payload = await response.json();

    if (typeof payload?.detail === "string") {
      return payload.detail;
    }

    if (Array.isArray(payload?.detail)) {
      return payload.detail
        .map((item) => item?.msg || JSON.stringify(item))
        .join(", ");
    }
  } catch {
    return null;
  }

  return null;
};

const fetchJson = async (path, options) => {
  const response = await fetch(buildUrl(path), options);

  if (!response.ok) {
    const detail = await parseErrorDetail(response);
    throw new Error(detail || `Request failed with status ${response.status}.`);
  }

  return response.json();
};

export const parseResumeFile = async (resumeFile) => {
  const formData = new FormData();
  formData.append("resume_file", resumeFile);

  return fetchJson("/parse-resume", {
    method: "POST",
    body: formData
  });
};

export const parseJobDescription = async (jobDescriptionText) =>
  fetchJson("/parse-jd", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      job_title: null,
      company_name: null,
      job_description_text: jobDescriptionText
    })
  });

export const analyzeRoleFit = async ({ parsedResume, parsedJobDescription }) =>
  fetchJson("/analyze", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      parsed_resume: parsedResume,
      parsed_job_description: parsedJobDescription
    })
  });
