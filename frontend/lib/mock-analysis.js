import { mockAnalysisResults } from "./mock-data";


const MOCK_RESUME_PROFILE = {
  directSkills: [
    "Python",
    "SQL",
    "Salesforce",
    "REST APIs",
    "JSON",
    "webhooks",
    "ChatGPT"
  ],
  evidence: [
    {
      text: "Automated manual business processes for operations teams.",
      concepts: ["automation", "workflow", "efficiency", "customerOps"],
      actions: ["automate"]
    },
    {
      text: "Developed an internal AI tool for support workflows.",
      concepts: ["ai", "workflow", "customerOps", "businessSoftware"],
      actions: ["build"]
    },
    {
      text: "Built REST API integrations and JSON webhook flows for internal business systems.",
      concepts: ["integration", "businessSoftware", "workflow"],
      actions: ["build"]
    },
    {
      text: "Partnered with support and business teams to reduce manual handoffs and improve productivity.",
      concepts: ["collaboration", "efficiency", "customerOps"],
      actions: ["collaborate", "automate"]
    },
    {
      text: "Supported software operations in internal tools used by customer-facing teams.",
      concepts: ["businessSoftware", "customerOps"],
      actions: ["support"]
    }
  ]
};

const SKILL_MATCHERS = [
  { label: "SQL", patterns: ["sql"] },
  { label: "Python", patterns: ["python"] },
  { label: "Workato", patterns: ["workato"] },
  { label: "Zapier", patterns: ["zapier"] },
  { label: "Make", patterns: ["make"] },
  { label: "Salesforce", patterns: ["salesforce"] },
  { label: "Gainsight", patterns: ["gainsight"] },
  { label: "Zendesk", patterns: ["zendesk"] },
  { label: "Snowflake", patterns: ["snowflake"] },
  { label: "REST APIs", patterns: ["rest api", "rest apis"] },
  { label: "JSON", patterns: ["json"] },
  { label: "webhooks", patterns: ["webhook", "webhooks"] },
  { label: "LLM", patterns: ["llm", "llms", "large language model", "large language models"] },
  { label: "ChatGPT", patterns: ["chatgpt"] },
  { label: "Gemini", patterns: ["gemini"] },
  { label: "FastAPI", patterns: ["fastapi"] },
  { label: "PostgreSQL", patterns: ["postgresql", "postgres"] },
  { label: "Docker", patterns: ["docker"] },
  { label: "Terraform", patterns: ["terraform"] }
];

const SECTION_ALIASES = {
  responsibilities: "responsibilities",
  "key responsibilities": "responsibilities",
  "what you will do": "responsibilities",
  "what you'll do": "responsibilities",
  "what you ll do": "responsibilities",
  "day to day": "responsibilities",
  requirements: "requirements",
  requirement: "requirements",
  qualifications: "requirements",
  qualification: "requirements",
  "minimum qualifications": "requirements",
  "must have": "requirements",
  "must haves": "requirements",
  preferred: "preferred",
  "preferred qualifications": "preferred",
  "preferred skills": "preferred",
  "nice to have": "preferred",
  "nice to haves": "preferred",
  "bonus points": "preferred",
  "bonus points if": "preferred"
};

const STOP_WORDS = new Set([
  "a",
  "an",
  "and",
  "the",
  "to",
  "for",
  "of",
  "in",
  "on",
  "with",
  "by",
  "at",
  "across",
  "through",
  "from",
  "your",
  "our",
  "their",
  "this",
  "that",
  "will",
  "you",
  "role",
  "team",
  "teams",
  "work",
  "experience",
  "using",
  "used"
]);

const ACTION_FAMILY_PATTERNS = {
  automate: ["automate", "automation", "automated", "improve", "reduce", "eliminate", "streamline", "optimize"],
  build: ["build", "design", "develop", "create", "implement", "pilot", "launch", "deliver", "maintain"],
  collaborate: ["partner", "collaborate", "coordinate", "support", "work with"],
  lead: ["lead", "own", "drive", "manage"]
};

const CONCEPT_BUCKETS = {
  automation: ["automation", "automate", "automated", "manual work", "manual process", "manual processes"],
  workflow: ["workflow", "workflows", "process", "processes", "pipeline", "pipelines"],
  ai: ["ai", "ai-enabled", "llm", "llms", "machine learning", "chatgpt", "gemini", "internal ai tool"],
  efficiency: ["efficiency", "productivity", "reduce manual work", "eliminate manual work", "streamline", "manual handoffs"],
  collaboration: ["cross-functional", "cross functional", "partner with", "business teams", "operations teams", "frontline teams", "stakeholders"],
  businessSoftware: ["saas", "software", "platform", "internal tools", "business systems"],
  customerOps: ["customer operations", "support", "customer success", "frontline", "zendesk", "gainsight"],
  integration: ["api", "apis", "rest api", "rest apis", "json", "webhook", "webhooks", "integration", "integrations"]
};

const CONCEPT_LABELS = {
  automation: "automation",
  workflow: "workflow work",
  ai: "AI-related work",
  efficiency: "manual-work reduction",
  collaboration: "cross-functional partnership",
  businessSoftware: "business-software context",
  customerOps: "customer operations context",
  integration: "integration experience"
};

const ACTION_VERBS = [
  "identify",
  "design",
  "build",
  "develop",
  "create",
  "lead",
  "manage",
  "partner",
  "collaborate",
  "pilot",
  "implement",
  "maintain",
  "automate",
  "analyze",
  "improve",
  "reduce",
  "support",
  "own",
  "drive",
  "deliver"
];

const REQUIRED_SIGNALS = [
  "required",
  "requirements",
  "must have",
  "minimum qualifications",
  "need",
  "needs",
  "should have"
];

const PREFERRED_SIGNALS = [
  "preferred",
  "nice to have",
  "nice-to-have",
  "bonus",
  "ideally",
  "plus"
];


const escapeRegExp = (value) => value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

const dedupePreserveOrder = (items) => {
  const seen = new Set();

  return items.filter((item) => {
    const key = item.toLowerCase();

    if (seen.has(key)) {
      return false;
    }

    seen.add(key);
    return true;
  });
};

const formatList = (items) => {
  if (!items.length) {
    return "";
  }

  if (items.length === 1) {
    return items[0];
  }

  if (items.length === 2) {
    return `${items[0]} and ${items[1]}`;
  }

  return `${items.slice(0, -1).join(", ")}, and ${items.at(-1)}`;
};

const capitalizeSentence = (value) => {
  if (!value) {
    return value;
  }

  return value.charAt(0).toUpperCase() + value.slice(1);
};

const normalizeHeading = (value) =>
  value
    .toLowerCase()
    .replace(/[:]/g, "")
    .replace(/[^a-z0-9\s'/-]/g, " ")
    .replace(/\s+/g, " ")
    .trim();

const hasPhrase = (text, phrase) => {
  const pattern = new RegExp(`(^|[^a-z0-9])${escapeRegExp(phrase.toLowerCase())}([^a-z0-9]|$)`, "i");
  return pattern.test(text.toLowerCase());
};

const normalizeToken = (token) => {
  const clean = token.toLowerCase();
  const replacements = {
    automated: "automate",
    automation: "automate",
    workflows: "workflow",
    processes: "process",
    pipelines: "pipeline",
    integrations: "integration",
    systems: "system",
    tools: "tool",
    teams: "team",
    responsibilities: "responsibility"
  };

  return replacements[clean] || clean;
};

const meaningfulTokens = (text) =>
  text
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, " ")
    .split(/\s+/)
    .map(normalizeToken)
    .filter((token) => token && !STOP_WORDS.has(token));

const intersection = (left, right) => {
  const rightSet = new Set(right);
  return left.filter((item) => rightSet.has(item));
};

const parseSections = (jobDescription) => {
  const sections = { overview: [] };
  const lines = jobDescription
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean);

  let currentSection = "overview";

  for (const line of lines) {
    const heading = normalizeHeading(line);
    const mappedSection = SECTION_ALIASES[heading];

    if (mappedSection) {
      currentSection = mappedSection;
      sections[currentSection] ||= [];
      continue;
    }

    sections[currentSection] ||= [];
    sections[currentSection].push(line.replace(/^[-*\u2022]\s*/, "").trim());
  }

  return sections;
};

const extractSkills = (text) =>
  dedupePreserveOrder(
    SKILL_MATCHERS
      .filter(({ patterns }) => patterns.some((pattern) => hasPhrase(text, pattern)))
      .map(({ label }) => label)
  );

const splitNarrativeUnits = (text) =>
  text
    .split(/\n+|(?<=[.!?])\s+/)
    .map((part) => part.trim())
    .filter(Boolean);

const extractSignaledSkills = (text, signals) => {
  const matches = [];

  for (const unit of splitNarrativeUnits(text)) {
    const normalizedUnit = unit.toLowerCase();

    if (signals.some((signal) => normalizedUnit.includes(signal))) {
      matches.push(...extractSkills(unit));
    }
  }

  return dedupePreserveOrder(matches);
};

const startsWithActionVerb = (value) =>
  ACTION_VERBS.some((verb) => new RegExp(`^${verb}\\b`, "i").test(value.trim()));

const splitActionClauses = (value) => {
  const trimmed = value
    .replace(/^[-*\u2022]\s*/, "")
    .replace(/^(this role will|the role will|you will|you'll|you would)\s+/i, "")
    .replace(/^responsible for\s+/i, "")
    .replace(/[.]+$/g, "")
    .trim();

  if (!trimmed) {
    return [];
  }

  const parts = trimmed
    .split(/,|;/g)
    .map((part) => part.replace(/^and\s+/i, "").trim())
    .filter(Boolean);

  const actionClauses = parts.filter(startsWithActionVerb).map(capitalizeSentence);

  if (actionClauses.length > 1) {
    return actionClauses;
  }

  if (startsWithActionVerb(trimmed)) {
    return [capitalizeSentence(trimmed)];
  }

  return [];
};

const extractResponsibilities = (jobDescription, sections) => {
  const sectionLines = sections.responsibilities || [];

  if (sectionLines.length) {
    return dedupePreserveOrder(
      sectionLines.flatMap((line) => {
        const clauses = splitActionClauses(line);

        if (clauses.length) {
          return clauses;
        }

        return [capitalizeSentence(line.replace(/[.]+$/g, "").trim())];
      })
    );
  }

  const fallback = [];

  for (const unit of splitNarrativeUnits(jobDescription)) {
    const normalized = unit.toLowerCase();
    const hasResponsibilitySignal =
      normalized.includes("you will") ||
      normalized.includes("this role will") ||
      normalized.includes("responsible for") ||
      startsWithActionVerb(unit);

    if (hasResponsibilitySignal) {
      fallback.push(...splitActionClauses(unit));
    }
  }

  return dedupePreserveOrder(fallback).slice(0, 6);
};

const extractConcepts = (text) =>
  Object.entries(CONCEPT_BUCKETS)
    .filter(([, patterns]) => patterns.some((pattern) => hasPhrase(text, pattern)))
    .map(([concept]) => concept);

const extractActionFamilies = (text) =>
  Object.entries(ACTION_FAMILY_PATTERNS)
    .filter(([, patterns]) => patterns.some((pattern) => hasPhrase(text, pattern)))
    .map(([family]) => family);

const scoreResponsibilitySupport = (responsibility) => {
  const responsibilityTokens = meaningfulTokens(responsibility);
  const responsibilityConcepts = extractConcepts(responsibility);
  const responsibilityActions = extractActionFamilies(responsibility);

  let bestMatch = null;

  for (const evidence of MOCK_RESUME_PROFILE.evidence) {
    const tokenOverlap = intersection(responsibilityTokens, meaningfulTokens(evidence.text));
    const conceptOverlap = intersection(responsibilityConcepts, evidence.concepts);
    const actionOverlap = intersection(responsibilityActions, evidence.actions);
    const lexicalCoverage = responsibilityTokens.length
      ? tokenOverlap.length / responsibilityTokens.length
      : 0;

    let support = "none";

    if (lexicalCoverage >= 0.45) {
      support = "full";
    } else if (lexicalCoverage >= 0.2 || conceptOverlap.length > 0 || actionOverlap.length > 0) {
      support = "partial";
    }

    const score = lexicalCoverage + conceptOverlap.length * 0.3 + actionOverlap.length * 0.15;

    if (!bestMatch || score > bestMatch.score) {
      bestMatch = {
        responsibility,
        support,
        evidence: evidence.text,
        concepts: conceptOverlap,
        score
      };
    }
  }

  return bestMatch || {
    responsibility,
    support: "none",
    evidence: null,
    concepts: [],
    score: 0
  };
};

const analyzeDomainFit = (jobDescription) => {
  const normalized = jobDescription.toLowerCase();
  const mentionsSaaS = hasPhrase(normalized, "saas") || hasPhrase(normalized, "software as a service");
  const mentionsSoftwareContext =
    mentionsSaaS || hasPhrase(normalized, "software") || hasPhrase(normalized, "platform");
  const mentionsCustomerOps =
    hasPhrase(normalized, "customer operations") ||
    hasPhrase(normalized, "customer success") ||
    hasPhrase(normalized, "support");

  if (mentionsSaaS) {
    return {
      score: 0.65,
      strength: "Resume shows adjacent business-software experience relevant to SaaS-oriented roles.",
      note:
        "Domain fit: the job description mentions SaaS, and the mock resume shows adjacent business-software evidence through internal tools and operations systems."
    };
  }

  if (mentionsSoftwareContext || mentionsCustomerOps) {
    return {
      score: 0.85,
      strength: "Resume shows adjacent domain evidence in software-supported operations work.",
      note:
        "Domain fit: the job description points to software or customer operations context, and the mock resume includes internal tools and operations workflow experience."
    };
  }

  return null;
};

const buildStrengths = ({
  matchedRequiredSkills,
  matchedPreferredSkills,
  fullResponsibilities,
  domainFit
}) => {
  const strengths = [];

  if (matchedRequiredSkills.length) {
    strengths.push(
      `Resume directly matches required skills including ${formatList(matchedRequiredSkills.slice(0, 4))}.`
    );
  }

  if (matchedPreferredSkills.length) {
    strengths.push(
      `Resume also overlaps with preferred technologies such as ${formatList(matchedPreferredSkills.slice(0, 3))}.`
    );
  }

  for (const match of fullResponsibilities.slice(0, 2)) {
    strengths.push(
      `Resume evidence '${match.evidence}' directly supports the responsibility '${match.responsibility}'.`
    );
  }

  if (domainFit?.strength) {
    strengths.push(domainFit.strength);
  }

  return strengths.length
    ? dedupePreserveOrder(strengths)
    : ["The job description shares some overlapping language with the mock candidate profile, but the fit remains limited."];
};

const buildGaps = ({
  missingRequiredSkills,
  missingPreferredSkills,
  missingResponsibilities,
  domainFit,
  jobDescription
}) => {
  const gaps = [];

  if (missingRequiredSkills.length) {
    gaps.push(
      `The resume does not explicitly mention ${formatList(missingRequiredSkills.slice(0, 4))}, which appear as required skills in the job description.`
    );
  }

  if (!missingRequiredSkills.length && missingPreferredSkills.length) {
    gaps.push(
      `Preferred tools such as ${formatList(missingPreferredSkills.slice(0, 3))} are not explicitly named in the current resume preview.`
    );
  }

  for (const responsibility of missingResponsibilities.slice(0, 2)) {
    gaps.push(
      `The job description emphasizes '${responsibility}', but the current resume preview does not show direct supporting evidence for it.`
    );
  }

  if (!domainFit && hasPhrase(jobDescription, "saas")) {
    gaps.push("The role calls for SaaS context, and the current preview does not show direct SaaS language.");
  }

  return dedupePreserveOrder(gaps);
};

const buildUnderEmphasized = (partialResponsibilities) =>
  partialResponsibilities.slice(0, 3).map((match) => {
    const relatedConcepts = match.concepts.map((concept) => CONCEPT_LABELS[concept] || concept);
    const conceptText = relatedConcepts.length
      ? ` through ${formatList(relatedConcepts)}`
      : "";
    const suggestion = buildHiddenRelevanceSuggestion(match, relatedConcepts);

    return `${match.evidence} supports '${match.responsibility}'${conceptText}. || Suggested bullet: ${suggestion}`;
  });

const buildHiddenRelevanceSuggestion = (match, relatedConcepts) => {
  const base = match.evidence.replace(/[.]+$/g, "");

  if (relatedConcepts.length) {
    return `${base} to emphasize ${formatList(relatedConcepts.slice(0, 2))}.`;
  }

  return `${base}; clarify how this supports ${match.responsibility.toLowerCase()}.`;
};

const buildEvidenceNotes = ({
  resumeFileName,
  requiredSkills,
  preferredSkills,
  matchedRequiredSkills,
  matchedPreferredSkills,
  fullResponsibilities,
  partialResponsibilities,
  missingResponsibilities,
  domainFit
}) => {
  const notes = [];

  if (resumeFileName) {
    notes.push(
      `Selected resume file '${resumeFileName}' is shown in the UI, but this preview is still scored against the built-in sample candidate profile until file parsing is wired into the frontend.`
    );
  } else {
    notes.push(
      "No resume file is connected to the live backend yet, so this preview uses the built-in sample candidate profile."
    );
  }

  notes.push(
    `Skills alignment: matched ${matchedRequiredSkills.length} of ${requiredSkills.length || 0} required skills and ${matchedPreferredSkills.length} of ${preferredSkills.length || 0} preferred skills identified in the job description.`
  );

  notes.push(
    `Experience relevance: ${fullResponsibilities.length} responsibilities directly supported, ${partialResponsibilities.length} partially supported, and ${missingResponsibilities.length} not yet evidenced.`
  );

  if (domainFit?.note) {
    notes.push(domainFit.note);
  }

  return notes;
};

const buildMissingKeywords = (missingRequiredSkills, missingPreferredSkills, jobDescription) => {
  const missing = [...missingRequiredSkills, ...missingPreferredSkills];

  if (hasPhrase(jobDescription, "saas")) {
    missing.push("SaaS");
  }

  return dedupePreserveOrder(missing);
};

const calculateScore = ({
  requiredSkills,
  preferredSkills,
  responsibilities,
  matchedRequiredSkills,
  matchedPreferredSkills,
  fullResponsibilities,
  partialResponsibilities,
  domainFit
}) => {
  const scoreInputs = [];

  if (requiredSkills.length) {
    scoreInputs.push({
      weight: 45,
      ratio: matchedRequiredSkills.length / requiredSkills.length
    });
  }

  if (preferredSkills.length) {
    scoreInputs.push({
      weight: 10,
      ratio: matchedPreferredSkills.length / preferredSkills.length
    });
  }

  if (responsibilities.length) {
    scoreInputs.push({
      weight: 35,
      ratio: (fullResponsibilities.length + partialResponsibilities.length * 0.5) / responsibilities.length
    });
  }

  if (domainFit) {
    scoreInputs.push({
      weight: 10,
      ratio: domainFit.score
    });
  }

  if (!scoreInputs.length) {
    return mockAnalysisResults.match_score;
  }

  const weightedTotal = scoreInputs.reduce((sum, item) => sum + item.weight * item.ratio, 0);
  const totalWeight = scoreInputs.reduce((sum, item) => sum + item.weight, 0);

  return Math.max(18, Math.min(96, Math.round((weightedTotal / totalWeight) * 100)));
};

export const buildMockResponse = ({ resumeFileName, jobDescription }) => {
  const normalizedDescription = jobDescription.trim();

  if (!normalizedDescription) {
    return {
      match_score: 0,
      strengths: [],
      gaps: ["Paste a job description to generate a role-fit preview."],
      missing_keywords: [],
      under_emphasized_experience: [],
      evidence_notes: ["No job description text was provided."]
    };
  }

  const sections = parseSections(normalizedDescription);
  const requiredSkills = dedupePreserveOrder([
    ...extractSkills((sections.requirements || []).join("\n")),
    ...extractSignaledSkills(normalizedDescription, REQUIRED_SIGNALS)
  ]);
  const preferredSkills = dedupePreserveOrder([
    ...extractSkills((sections.preferred || []).join("\n")),
    ...extractSignaledSkills(normalizedDescription, PREFERRED_SIGNALS)
  ]).filter((skill) => !requiredSkills.includes(skill));
  const responsibilities = extractResponsibilities(normalizedDescription, sections);

  const matchedRequiredSkills = requiredSkills.filter((skill) => MOCK_RESUME_PROFILE.directSkills.includes(skill));
  const missingRequiredSkills = requiredSkills.filter((skill) => !MOCK_RESUME_PROFILE.directSkills.includes(skill));
  const matchedPreferredSkills = preferredSkills.filter((skill) => MOCK_RESUME_PROFILE.directSkills.includes(skill));
  const missingPreferredSkills = preferredSkills.filter((skill) => !MOCK_RESUME_PROFILE.directSkills.includes(skill));

  const responsibilityMatches = responsibilities.map(scoreResponsibilitySupport);
  const fullResponsibilities = responsibilityMatches.filter((match) => match.support === "full");
  const partialResponsibilities = responsibilityMatches.filter((match) => match.support === "partial");
  const missingResponsibilities = responsibilityMatches
    .filter((match) => match.support === "none")
    .map((match) => match.responsibility);

  const domainFit = analyzeDomainFit(normalizedDescription);

  return {
    match_score: calculateScore({
      requiredSkills,
      preferredSkills,
      responsibilities,
      matchedRequiredSkills,
      matchedPreferredSkills,
      fullResponsibilities,
      partialResponsibilities,
      domainFit
    }),
    strengths: buildStrengths({
      matchedRequiredSkills,
      matchedPreferredSkills,
      fullResponsibilities,
      domainFit
    }),
    gaps: buildGaps({
      missingRequiredSkills,
      missingPreferredSkills,
      missingResponsibilities,
      domainFit,
      jobDescription: normalizedDescription
    }),
    missing_keywords: buildMissingKeywords(
      missingRequiredSkills,
      missingPreferredSkills,
      normalizedDescription
    ),
    under_emphasized_experience: buildUnderEmphasized(partialResponsibilities),
    evidence_notes: buildEvidenceNotes({
      resumeFileName,
      requiredSkills,
      preferredSkills,
      matchedRequiredSkills,
      matchedPreferredSkills,
      fullResponsibilities,
      partialResponsibilities,
      missingResponsibilities,
      domainFit
    })
  };
};
