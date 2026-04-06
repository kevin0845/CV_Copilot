"use client";

import { useMemo, useState } from "react";

import { mockResults, sampleJobDescription } from "../lib/mock-data";


const scoreTone = (score) => {
  if (score >= 80) {
    return {
      ring: "from-teal-600 to-emerald-400",
      pill: "bg-teal-100 text-teal-800"
    };
  }

  if (score >= 60) {
    return {
      ring: "from-amber-500 to-orange-400",
      pill: "bg-amber-100 text-amber-800"
    };
  }

  return {
    ring: "from-orange-700 to-rose-500",
    pill: "bg-orange-100 text-orange-800"
  };
};


function ResultCard({ title, children, tone = "default" }) {
  const toneStyles =
    tone === "danger"
      ? "border-[color:var(--danger-soft)] bg-[color:var(--panel-strong)]"
      : "border-[color:var(--border)] bg-[color:var(--panel)]";

  return (
    <section className={`rounded-[28px] border p-5 shadow-[var(--shadow)] backdrop-blur-sm ${toneStyles}`}>
      <h3 className="text-lg font-semibold tracking-tight text-[color:var(--foreground)]">
        {title}
      </h3>
      <div className="mt-4 text-sm text-[color:var(--muted)]">{children}</div>
    </section>
  );
}


function ListBlock({ items, accent = "default" }) {
  const bulletColor =
    accent === "danger" ? "bg-[color:var(--danger)]" : "bg-[color:var(--accent)]";

  if (!items.length) {
    return <p className="text-sm text-[color:var(--muted)]">No items to show yet.</p>;
  }

  return (
    <ul className="space-y-3">
      {items.map((item) => (
        <li
          key={item}
          className="flex items-start gap-3 rounded-2xl bg-white/70 px-4 py-3 text-sm leading-6 text-[color:var(--foreground)]"
        >
          <span className={`mt-2 h-2.5 w-2.5 rounded-full ${bulletColor}`} />
          <span>{item}</span>
        </li>
      ))}
    </ul>
  );
}


export default function HomePage() {
  const [resumeFileName, setResumeFileName] = useState("");
  const [jobDescription, setJobDescription] = useState(sampleJobDescription);
  const [results, setResults] = useState(mockResults);

  const scoreStyles = useMemo(
    () => scoreTone(results.matchScore),
    [results.matchScore]
  );

  const handleAnalyze = () => {
    setResults({
      ...mockResults,
      missingKeywords:
        jobDescription.trim().length === 0 ? ["Paste a job description to preview analysis"] : mockResults.missingKeywords
    });
  };

  return (
    <main className="min-h-screen px-4 py-6 md:px-8 lg:px-10">
      <div className="mx-auto max-w-7xl">
        <header className="mb-8 rounded-[32px] border border-white/60 bg-white/55 px-6 py-6 shadow-[var(--shadow)] backdrop-blur-md md:px-8">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
            <div className="max-w-2xl">
              <p className="text-sm font-semibold uppercase tracking-[0.28em] text-[color:var(--accent)]">
                CV Copilot
              </p>
              <h1 className="mt-3 text-4xl font-semibold tracking-tight text-[color:var(--foreground)] md:text-5xl">
                Tailor resumes with a sharper role-fit lens.
              </h1>
              <p className="mt-4 max-w-xl text-base leading-7 text-[color:var(--muted)]">
                Upload a resume, paste a job description, and review structured match insights with rewrite ideas.
              </p>
            </div>

            <div className="inline-flex items-center gap-3 rounded-full border border-white/80 bg-white/80 px-4 py-3 text-sm text-[color:var(--foreground)]">
              <span className="h-2.5 w-2.5 rounded-full bg-[color:var(--accent)]" />
              Mock preview mode
            </div>
          </div>
        </header>

        <div className="grid gap-6 xl:grid-cols-[minmax(0,0.92fr)_minmax(0,1.08fr)]">
          <section className="rounded-[32px] border border-[color:var(--border)] bg-[color:var(--panel)] p-6 shadow-[var(--shadow)] backdrop-blur-md md:p-7">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-sm font-semibold uppercase tracking-[0.22em] text-[color:var(--accent)]">
                  Inputs
                </p>
                <h2 className="mt-2 text-2xl font-semibold tracking-tight text-[color:var(--foreground)]">
                  Resume + job setup
                </h2>
              </div>
            </div>

            <div className="mt-6 space-y-6">
              <div className="rounded-[28px] border border-dashed border-[color:var(--border)] bg-white/75 p-5">
                <label className="block text-sm font-semibold text-[color:var(--foreground)]">
                  Resume Upload
                </label>
                <p className="mt-1 text-sm text-[color:var(--muted)]">
                  Supports PDF or DOCX. This mock UI stores the selected filename locally for now.
                </p>

                <label className="mt-4 flex cursor-pointer items-center justify-between rounded-2xl bg-[color:var(--accent-soft)] px-4 py-4 transition hover:bg-white">
                  <span>
                    <span className="block text-sm font-semibold text-[color:var(--foreground)]">
                      {resumeFileName || "Choose resume file"}
                    </span>
                    <span className="mt-1 block text-xs uppercase tracking-[0.2em] text-[color:var(--muted)]">
                      Upload resume
                    </span>
                  </span>

                  <span className="rounded-full bg-[color:var(--foreground)] px-4 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-white">
                    Browse
                  </span>

                  <input
                    className="hidden"
                    type="file"
                    accept=".pdf,.doc,.docx"
                    onChange={(event) => {
                      const file = event.target.files?.[0];
                      setResumeFileName(file ? file.name : "");
                    }}
                  />
                </label>
              </div>

              <div className="rounded-[28px] border border-[color:var(--border)] bg-white/75 p-5">
                <label
                  className="block text-sm font-semibold text-[color:var(--foreground)]"
                  htmlFor="job-description"
                >
                  Job Description
                </label>
                <p className="mt-1 text-sm text-[color:var(--muted)]">
                  Paste the target posting to preview role-fit analysis and rewrite guidance.
                </p>
                <textarea
                  id="job-description"
                  className="mt-4 min-h-[300px] w-full rounded-[24px] border border-[color:var(--border)] bg-[#fcfbf8] px-4 py-4 text-sm leading-6 text-[color:var(--foreground)] outline-none transition focus:border-[color:var(--accent)] focus:ring-4 focus:ring-[color:var(--accent-soft)]"
                  value={jobDescription}
                  onChange={(event) => setJobDescription(event.target.value)}
                />
              </div>

              <div className="flex flex-col gap-3 sm:flex-row">
                <button
                  className="inline-flex items-center justify-center rounded-full bg-[color:var(--foreground)] px-5 py-3 text-sm font-semibold tracking-[0.12em] text-white transition hover:-translate-y-0.5 hover:bg-[#0f172a]"
                  onClick={handleAnalyze}
                  type="button"
                >
                  Run mock analysis
                </button>
                <button
                  className="inline-flex items-center justify-center rounded-full border border-[color:var(--border)] bg-white px-5 py-3 text-sm font-semibold tracking-[0.12em] text-[color:var(--foreground)] transition hover:border-[color:var(--accent)] hover:text-[color:var(--accent)]"
                  onClick={() => {
                    setResumeFileName("");
                    setJobDescription(sampleJobDescription);
                    setResults(mockResults);
                  }}
                  type="button"
                >
                  Reset
                </button>
              </div>
            </div>
          </section>

          <section className="space-y-6">
            <div className="grid gap-6 lg:grid-cols-[220px_minmax(0,1fr)]">
              <div className="rounded-[32px] border border-[color:var(--border)] bg-[color:var(--panel-strong)] p-6 shadow-[var(--shadow)] backdrop-blur-md">
                <p className="text-sm font-semibold uppercase tracking-[0.22em] text-[color:var(--accent)]">
                  Match score
                </p>
                <div className="mt-5 flex items-center justify-center">
                  <div className={`flex h-36 w-36 items-center justify-center rounded-full bg-gradient-to-br ${scoreStyles.ring} p-[10px]`}>
                    <div className="flex h-full w-full flex-col items-center justify-center rounded-full bg-white text-center">
                      <span className="text-4xl font-semibold tracking-tight text-[color:var(--foreground)]">
                        {results.matchScore}
                      </span>
                      <span className="mt-1 text-xs font-semibold uppercase tracking-[0.24em] text-[color:var(--muted)]">
                        out of 100
                      </span>
                    </div>
                  </div>
                </div>
                <div className={`mt-5 inline-flex rounded-full px-3 py-2 text-xs font-semibold uppercase tracking-[0.18em] ${scoreStyles.pill}`}>
                  {results.matchScore >= 80 ? "Strong fit" : results.matchScore >= 60 ? "Promising fit" : "Needs tailoring"}
                </div>
              </div>

              <ResultCard title="Tailored Summary">
                <p className="rounded-[24px] bg-white/80 px-4 py-4 text-base leading-7 text-[color:var(--foreground)]">
                  {results.tailoredSummary}
                </p>
              </ResultCard>
            </div>

            <div className="grid gap-6 md:grid-cols-2">
              <ResultCard title="Strengths">
                <ListBlock items={results.strengths} />
              </ResultCard>

              <ResultCard title="Gaps" tone="danger">
                <ListBlock items={results.gaps} accent="danger" />
              </ResultCard>
            </div>

            <div className="grid gap-6 md:grid-cols-[0.85fr_1.15fr]">
              <ResultCard title="Missing Keywords" tone="danger">
                <div className="flex flex-wrap gap-3">
                  {results.missingKeywords.map((keyword) => (
                    <span
                      key={keyword}
                      className="rounded-full bg-[color:var(--danger-soft)] px-4 py-2 text-sm font-semibold text-[color:var(--danger)]"
                    >
                      {keyword}
                    </span>
                  ))}
                </div>
              </ResultCard>

              <ResultCard title="Rewrite Suggestions">
                <div className="space-y-4">
                  {results.rewriteSuggestions.map((item) => (
                    <article
                      key={`${item.original}-${item.suggested}`}
                      className="rounded-[24px] bg-white/80 p-4"
                    >
                      <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[color:var(--muted)]">
                        Original
                      </p>
                      <p className="mt-2 text-sm leading-6 text-[color:var(--foreground)]">
                        {item.original}
                      </p>
                      <p className="mt-4 text-xs font-semibold uppercase tracking-[0.18em] text-[color:var(--accent)]">
                        Suggested
                      </p>
                      <p className="mt-2 text-sm leading-6 text-[color:var(--foreground)]">
                        {item.suggested}
                      </p>
                      <p className="mt-4 text-xs font-semibold uppercase tracking-[0.18em] text-[color:var(--muted)]">
                        Rationale
                      </p>
                      <p className="mt-2 text-sm leading-6 text-[color:var(--muted)]">
                        {item.rationale}
                      </p>
                    </article>
                  ))}
                </div>
              </ResultCard>
            </div>
          </section>
        </div>
      </div>
    </main>
  );
}
