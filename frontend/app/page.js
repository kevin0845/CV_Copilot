"use client";

import { useMemo, useState } from "react";

import { buildMockResponse } from "../lib/mock-analysis";
import { sampleJobDescription } from "../lib/mock-data";


const scoreTone = (score) => {
  if (score >= 80) {
    return {
      badge: "bg-emerald-100 text-emerald-800",
      gradient: "from-emerald-500 via-teal-500 to-cyan-400",
      label: "Strong fit"
    };
  }

  if (score >= 65) {
    return {
      badge: "bg-amber-100 text-amber-800",
      gradient: "from-amber-500 via-orange-500 to-rose-400",
      label: "Promising fit"
    };
  }

  return {
    badge: "bg-rose-100 text-rose-800",
    gradient: "from-rose-500 via-orange-500 to-amber-400",
    label: "Needs tailoring"
  };
};


function SectionCard({ eyebrow, title, children, className = "" }) {
  return (
    <section
      className={`rounded-[30px] border border-[color:var(--border)] bg-[color:var(--panel)] p-5 shadow-[var(--shadow)] backdrop-blur-md md:p-6 ${className}`}
    >
      {eyebrow ? (
        <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[color:var(--accent)]">
          {eyebrow}
        </p>
      ) : null}
      <h2 className="mt-2 text-xl font-semibold tracking-tight text-[color:var(--foreground)]">
        {title}
      </h2>
      <div className="mt-5">{children}</div>
    </section>
  );
}


function InsightList({ items, tone = "neutral", emptyLabel }) {
  const marker =
    tone === "danger"
      ? "bg-[color:var(--danger)]"
      : tone === "support"
        ? "bg-[color:var(--support)]"
        : "bg-[color:var(--accent)]";

  if (!items.length) {
    return (
      <div className="rounded-[24px] border border-dashed border-[color:var(--border)] bg-white/70 px-4 py-5 text-sm leading-6 text-[color:var(--muted)]">
        {emptyLabel}
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {items.map((item) => (
        <article
          key={item}
          className="flex items-start gap-3 rounded-[24px] bg-white/78 px-4 py-4 text-sm leading-6 text-[color:var(--foreground)]"
        >
          <span className={`mt-2 h-2.5 w-2.5 rounded-full ${marker}`} />
          <span>{item}</span>
        </article>
      ))}
    </div>
  );
}


function KeywordGrid({ items }) {
  if (!items.length) {
    return (
      <div className="rounded-[24px] border border-dashed border-[color:var(--border)] bg-white/70 px-4 py-5 text-sm text-[color:var(--muted)]">
        No missing keywords detected in this mock pass.
      </div>
    );
  }

  return (
    <div className="flex flex-wrap gap-3">
      {items.map((keyword) => (
        <span
          key={keyword}
          className="rounded-full border border-[color:var(--danger-soft)] bg-[color:var(--danger-soft)] px-4 py-2 text-sm font-semibold text-[color:var(--danger)]"
        >
          {keyword}
        </span>
      ))}
    </div>
  );
}


function MetricTile({ label, value, helper }) {
  return (
    <div className="rounded-[24px] border border-white/70 bg-white/80 px-4 py-4">
      <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[color:var(--muted)]">
        {label}
      </p>
      <p className="mt-3 text-3xl font-semibold tracking-tight text-[color:var(--foreground)]">
        {value}
      </p>
      <p className="mt-1 text-sm text-[color:var(--muted)]">{helper}</p>
    </div>
  );
}


export default function HomePage() {
  const [resumeFileName, setResumeFileName] = useState("");
  const [jobDescription, setJobDescription] = useState(sampleJobDescription);
  const [results, setResults] = useState(() =>
    buildMockResponse({ resumeFileName: "", jobDescription: sampleJobDescription })
  );
  const [statusLabel, setStatusLabel] = useState("Analysis preview ready");

  const scoreStyles = useMemo(
    () => scoreTone(results.match_score),
    [results.match_score]
  );

  const handleAnalyze = () => {
    setResults(buildMockResponse({ resumeFileName, jobDescription }));
    setStatusLabel("Analysis preview updated");
  };

  const handleReset = () => {
    setResumeFileName("");
    setJobDescription(sampleJobDescription);
    setResults(buildMockResponse({ resumeFileName: "", jobDescription: sampleJobDescription }));
    setStatusLabel("Analysis preview ready");
  };

  return (
    <main className="min-h-screen px-4 py-6 md:px-8 lg:px-10">
      <div className="mx-auto max-w-7xl">
        <header className="relative overflow-hidden rounded-[36px] border border-white/65 bg-white/62 px-6 py-6 shadow-[var(--shadow)] backdrop-blur-md md:px-8 md:py-8">
          <div className="absolute inset-y-0 right-0 w-1/2 bg-[radial-gradient(circle_at_top,rgba(15,118,110,0.14),transparent_60%)]" />
          <div className="relative flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
            <div className="max-w-3xl">
              <p className="text-sm font-semibold uppercase tracking-[0.3em] text-[color:var(--accent)]">
                CV Copilot
              </p>
              <h1 className="mt-3 text-4xl font-semibold tracking-tight text-[color:var(--foreground)] md:text-5xl">
                Compare a resume against a target role with clear, structured guidance.
              </h1>
              <p className="mt-4 max-w-2xl text-base leading-7 text-[color:var(--muted)]">
                Upload a resume, paste the job description, and review match score, strengths, gaps, missing keywords, and under-emphasized experience in one workspace. The current preview uses mock data aligned to the <code>/analyze</code> response so the interface is ready for live backend wiring.
              </p>
            </div>

            <div className="rounded-full border border-white/80 bg-white/85 px-4 py-3 text-sm font-semibold text-[color:var(--foreground)] shadow-sm">
              {statusLabel}
            </div>
          </div>
        </header>

        <div className="mt-6 grid gap-6 xl:grid-cols-[minmax(0,0.92fr)_minmax(0,1.08fr)]">
          <section className="rounded-[34px] border border-[color:var(--border)] bg-[color:var(--panel)] p-6 shadow-[var(--shadow)] backdrop-blur-md md:p-7">
            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="text-sm font-semibold uppercase tracking-[0.22em] text-[color:var(--accent)]">
                  Input workspace
                </p>
                <h2 className="mt-2 text-2xl font-semibold tracking-tight text-[color:var(--foreground)]">
                  Resume upload and role brief
                </h2>
              </div>
              <div className="rounded-full bg-[color:var(--accent-soft)] px-3 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-[color:var(--accent)]">
                Mock mode
              </div>
            </div>

            <div className="mt-6 space-y-6">
              <div className="rounded-[28px] border border-dashed border-[color:var(--border-strong)] bg-white/74 p-5">
                <label className="block text-sm font-semibold text-[color:var(--foreground)]">
                  Resume upload
                </label>
                <p className="mt-1 text-sm leading-6 text-[color:var(--muted)]">
                  Select a PDF or DOCX resume. The current page stores the filename locally and uses mock analysis data until end-to-end wiring is added.
                </p>

                <label className="mt-4 flex cursor-pointer items-center justify-between gap-4 rounded-[24px] bg-[color:var(--surface-soft)] px-4 py-4 transition hover:bg-white">
                  <div>
                    <span className="block text-sm font-semibold text-[color:var(--foreground)]">
                      {resumeFileName || "Choose a resume file"}
                    </span>
                    <span className="mt-1 block text-xs uppercase tracking-[0.2em] text-[color:var(--muted)]">
                      PDF or DOCX
                    </span>
                  </div>

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

              <div className="rounded-[28px] border border-[color:var(--border)] bg-white/78 p-5">
                <label
                  className="block text-sm font-semibold text-[color:var(--foreground)]"
                  htmlFor="job-description"
                >
                  Job description
                </label>
                <p className="mt-1 text-sm leading-6 text-[color:var(--muted)]">
                  Paste the target posting to preview how the current analysis service would frame strengths, gaps, keywords, and under-emphasized experience.
                </p>
                <textarea
                  id="job-description"
                  className="mt-4 min-h-[360px] w-full rounded-[24px] border border-[color:var(--border)] bg-[#fcfbf8] px-4 py-4 text-sm leading-6 text-[color:var(--foreground)] outline-none transition focus:border-[color:var(--accent)] focus:ring-4 focus:ring-[color:var(--accent-soft)]"
                  value={jobDescription}
                  onChange={(event) => setJobDescription(event.target.value)}
                />
              </div>

              <div className="rounded-[28px] border border-[color:var(--border)] bg-[color:var(--surface-soft)] px-4 py-4 text-sm leading-6 text-[color:var(--muted)]">
                The right panel is designed against the current backend response shape:
                <span className="mt-2 block font-mono text-xs text-[color:var(--foreground)]">
                  match_score, strengths, gaps, missing_keywords, under_emphasized_experience, evidence_notes
                </span>
              </div>

              <div className="flex flex-col gap-3 sm:flex-row">
                <button
                  className="inline-flex items-center justify-center rounded-full bg-[color:var(--foreground)] px-5 py-3 text-sm font-semibold tracking-[0.14em] text-white transition hover:-translate-y-0.5 hover:bg-[#101827]"
                  onClick={handleAnalyze}
                  type="button"
                >
                  Analyze role fit
                </button>
                <button
                  className="inline-flex items-center justify-center rounded-full border border-[color:var(--border-strong)] bg-white px-5 py-3 text-sm font-semibold tracking-[0.14em] text-[color:var(--foreground)] transition hover:border-[color:var(--accent)] hover:text-[color:var(--accent)]"
                  onClick={handleReset}
                  type="button"
                >
                  Reset preview
                </button>
              </div>
            </div>
          </section>

          <section className="space-y-6">
            <div className="grid gap-6 lg:grid-cols-[260px_minmax(0,1fr)]">
              <SectionCard eyebrow="Analysis score" title="Match score">
                <div className="flex justify-center">
                  <div className={`flex h-40 w-40 items-center justify-center rounded-full bg-gradient-to-br ${scoreStyles.gradient} p-[10px] shadow-lg`}>
                    <div className="flex h-full w-full flex-col items-center justify-center rounded-full bg-white text-center">
                      <span className="text-5xl font-semibold tracking-tight text-[color:var(--foreground)]">
                        {results.match_score}
                      </span>
                      <span className="mt-1 text-xs font-semibold uppercase tracking-[0.24em] text-[color:var(--muted)]">
                        score
                      </span>
                    </div>
                  </div>
                </div>
                <div className={`mt-5 inline-flex rounded-full px-3 py-2 text-xs font-semibold uppercase tracking-[0.18em] ${scoreStyles.badge}`}>
                  {scoreStyles.label}
                </div>
              </SectionCard>

              <SectionCard eyebrow="Fit overview" title="Analysis snapshot">
                <div className="grid gap-4 sm:grid-cols-3">
                  <MetricTile
                    label="Strengths"
                    value={results.strengths.length}
                    helper="Direct or clearly supported matches"
                  />
                  <MetricTile
                    label="Gaps"
                    value={results.gaps.length}
                    helper="Areas not yet evidenced clearly"
                  />
                  <MetricTile
                    label="Under-emphasized"
                    value={results.under_emphasized_experience.length}
                    helper="Relevant experience that needs sharper wording"
                  />
                </div>

                <div className="mt-4 rounded-[24px] bg-white/80 px-4 py-4 text-sm leading-6 text-[color:var(--muted)]">
                  The layout is intentionally product-oriented: concise score framing up top, evidence-backed lists below, and no raw backend blobs exposed to the end user.
                </div>
              </SectionCard>
            </div>

            <div className="grid gap-6 md:grid-cols-2">
              <SectionCard eyebrow="What already fits" title="Strengths">
                <InsightList
                  items={results.strengths}
                  tone="support"
                  emptyLabel="No strengths captured yet."
                />
              </SectionCard>

              <SectionCard eyebrow="Where the resume falls short" title="Gaps">
                <InsightList
                  items={results.gaps}
                  tone="danger"
                  emptyLabel="No gaps detected in this preview."
                />
              </SectionCard>
            </div>

            <div className="grid gap-6 md:grid-cols-[0.88fr_1.12fr]">
              <SectionCard eyebrow="Keyword coverage" title="Missing keywords">
                <KeywordGrid items={results.missing_keywords} />
              </SectionCard>

              <SectionCard eyebrow="Hidden relevance" title="Under-emphasized experience">
                <InsightList
                  items={results.under_emphasized_experience}
                  emptyLabel="No under-emphasized experience was identified."
                />
              </SectionCard>
            </div>

            <SectionCard eyebrow="Decision trail" title="Evidence notes">
              <div className="space-y-3">
                {results.evidence_notes.map((note, index) => (
                  <article
                    key={note}
                    className="flex items-start gap-4 rounded-[24px] bg-white/80 px-4 py-4"
                  >
                    <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-[color:var(--accent-soft)] text-sm font-semibold text-[color:var(--accent)]">
                      {index + 1}
                    </div>
                    <p className="text-sm leading-6 text-[color:var(--foreground)]">{note}</p>
                  </article>
                ))}
              </div>
            </SectionCard>
          </section>
        </div>
      </div>
    </main>
  );
}
