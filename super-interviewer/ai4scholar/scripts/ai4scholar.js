#!/usr/bin/env node

const fs = require("node:fs");
const path = require("node:path");

const skillRoot = path.resolve(__dirname, "..");
const configPath = path.join(skillRoot, "config.json");

function loadConfig() {
  const fileConfig = fs.existsSync(configPath)
    ? JSON.parse(fs.readFileSync(configPath, "utf8"))
    : {};
  return {
    apiKey: process.env.AI4SCHOLAR_API_KEY || fileConfig.apiKey || "",
    baseUrl: process.env.AI4SCHOLAR_BASE_URL || fileConfig.baseUrl || "https://ai4scholar.net",
  };
}

async function readInput() {
  if (process.argv[3]) {
    return JSON.parse(process.argv[3]);
  }
  const chunks = [];
  for await (const chunk of process.stdin) chunks.push(chunk);
  const raw = Buffer.concat(chunks).toString("utf8").trim();
  return raw ? JSON.parse(raw) : {};
}

function fail(message, extra) {
  const payload = { ok: false, error: message };
  if (extra !== undefined) payload.details = extra;
  console.error(JSON.stringify(payload, null, 2));
  process.exit(1);
}

function qs(params) {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params || {})) {
    if (value !== undefined && value !== null && value !== "") {
      search.set(key, String(value));
    }
  }
  const text = search.toString();
  return text ? `?${text}` : "";
}

async function httpJson(url, options = {}) {
  const res = await fetch(url, options);
  const text = await res.text();
  let data = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = text;
  }
  if (!res.ok) {
    fail(`HTTP ${res.status}`, data);
  }
  return data;
}

async function httpText(url, options = {}) {
  const res = await fetch(url, options);
  const text = await res.text();
  if (!res.ok) {
    fail(`HTTP ${res.status}`, text);
  }
  return text;
}

function authHeaders(config) {
  const headers = {
    "Content-Type": "application/json",
    "User-Agent": "codex-ai4scholar-skill/0.1",
  };
  if (config.apiKey) {
    headers.Authorization = `Bearer ${config.apiKey}`;
  }
  return headers;
}

function daysAgo(days) {
  const now = new Date();
  const past = new Date(now.getTime() - days * 86400000);
  return past.toISOString().slice(0, 10);
}

function parseArxivXml(xml) {
  const papers = [];
  const entries = xml.match(/<entry>[\s\S]*?<\/entry>/g) || [];
  for (const entry of entries) {
    const tag = (name) => {
      const match = entry.match(new RegExp(`<${name}[^>]*>([\\s\\S]*?)<\\/${name}>`));
      return match ? match[1].trim().replace(/\s+/g, " ") : "";
    };
    const authors = [...entry.matchAll(/<author>\s*<name>([^<]+)<\/name>/g)].map((m) => m[1].trim());
    const id = tag("id").replace("http://arxiv.org/abs/", "").replace(/v\d+$/, "");
    if (!id) continue;
    const pdfMatch = entry.match(/<link[^>]+title="pdf"[^>]+href="([^"]+)"/);
    papers.push({
      arxiv_id: id,
      title: tag("title"),
      abstract: tag("summary"),
      published: tag("published"),
      updated: tag("updated"),
      authors,
      pdf_url: pdfMatch ? pdfMatch[1] : `https://arxiv.org/pdf/${id}.pdf`,
    });
  }
  return papers;
}

function mapRxivPaper(item, server) {
  return {
    paper_id: item.doi,
    doi: item.doi,
    title: item.title,
    abstract: item.abstract,
    authors: String(item.authors || "")
      .split(";")
      .map((s) => s.trim())
      .filter(Boolean),
    category: item.category,
    published: item.date,
    source: server,
    url: `https://www.${server}.org/content/${item.doi}v${item.version || "1"}`,
    pdf_url: `https://www.${server}.org/content/${item.doi}v${item.version || "1"}.full.pdf`,
  };
}

async function run(tool, input, config) {
  const baseUrl = config.baseUrl.replace(/\/$/, "");

  if (tool === "search_semantic") {
    const limit = input.max_results || input.limit || 10;
    return httpJson(
      `${baseUrl}/graph/v1/paper/search${qs({
        query: input.query,
        limit,
        year: input.year,
        fields:
          "paperId,title,abstract,year,venue,publicationDate,authors,citationCount,referenceCount,externalIds,openAccessPdf,url",
      })}`,
      { headers: authHeaders(config) },
    );
  }

  if (tool === "search_semantic_snippets") {
    const limit = input.limit || input.max_results || 10;
    return httpJson(
      `${baseUrl}/graph/v1/snippet/search${qs({ query: input.query, limit })}`,
      { headers: authHeaders(config) },
    );
  }

  if (tool === "search_semantic_paper_match") {
    return httpJson(
      `${baseUrl}/graph/v1/paper/search/match${qs({
        query: input.query,
        fields:
          "paperId,title,abstract,year,venue,publicationDate,authors,citationCount,referenceCount,externalIds,openAccessPdf,url",
      })}`,
      { headers: authHeaders(config) },
    );
  }

  if (tool === "get_semantic_paper_detail") {
    return httpJson(
      `${baseUrl}/graph/v1/paper/${encodeURIComponent(input.paper_id)}${qs({
        fields:
          "paperId,title,abstract,year,venue,publicationDate,authors,citationCount,referenceCount,externalIds,openAccessPdf,url",
      })}`,
      { headers: authHeaders(config) },
    );
  }

  if (tool === "get_semantic_citations") {
    return httpJson(
      `${baseUrl}/graph/v1/paper/${encodeURIComponent(input.paper_id)}/citations${qs({
        limit: input.limit || 20,
        offset: input.offset || 0,
        fields:
          "paperId,title,abstract,year,venue,publicationDate,authors,citationCount,referenceCount,externalIds,openAccessPdf,url",
      })}`,
      { headers: authHeaders(config) },
    );
  }

  if (tool === "get_semantic_references") {
    return httpJson(
      `${baseUrl}/graph/v1/paper/${encodeURIComponent(input.paper_id)}/references${qs({
        limit: input.limit || 20,
        offset: input.offset || 0,
        fields:
          "paperId,title,abstract,year,venue,publicationDate,authors,citationCount,referenceCount,externalIds,openAccessPdf,url",
      })}`,
      { headers: authHeaders(config) },
    );
  }

  if (tool === "search_pubmed") {
    return httpJson(`${baseUrl}/pubmed/v1/paper/search`, {
      method: "POST",
      headers: authHeaders(config),
      body: JSON.stringify({
        query: input.query,
        limit: input.max_results || 10,
        offset: 0,
        sort: input.sort || "relevance",
        minDate: input.min_date,
        maxDate: input.max_date,
      }),
    });
  }

  if (tool === "get_pubmed_paper_detail") {
    return httpJson(`${baseUrl}/pubmed/v1/paper/${encodeURIComponent(input.pmid)}`, {
      headers: authHeaders(config),
    });
  }

  if (tool === "get_pubmed_related") {
    return httpJson(
      `${baseUrl}/pubmed/v1/paper/${encodeURIComponent(input.pmid)}/related${qs({
        limit: input.limit || 20,
      })}`,
      { headers: authHeaders(config) },
    );
  }

  if (tool === "search_google_scholar") {
    return httpJson(`${baseUrl}/google-scholar/v1/search`, {
      method: "POST",
      headers: authHeaders(config),
      body: JSON.stringify({
        query: input.query,
        page: input.page || 1,
        yearFrom: input.year_from,
        yearTo: input.year_to,
      }),
    });
  }

  if (tool === "search_arxiv") {
    const maxResults = Math.min(input.max_results || 10, 50);
    let searchQuery = input.query;
    if (input.date_from) {
      const d = String(input.date_from).replace(/-/g, "");
      searchQuery = `${input.query} AND submittedDate:[${d}0000 TO 99991231]`;
    }
    const sortMap = {
      relevance: "relevance",
      lastupdateddate: "lastUpdatedDate",
      submitteddate: "submittedDate",
    };
    const sortKey = String(input.sort_by || "relevance").toLowerCase();
    const xml = await httpText(
      `https://export.arxiv.org/api/query${qs({
        search_query: searchQuery,
        start: 0,
        max_results: maxResults,
        sortBy: sortMap[sortKey] || "relevance",
        sortOrder: "descending",
      })}`,
      { headers: { "User-Agent": "codex-ai4scholar-skill/0.1" } },
    );
    return { papers: parseArxivXml(xml) };
  }

  if (tool === "search_biorxiv" || tool === "search_medrxiv") {
    const server = tool === "search_biorxiv" ? "biorxiv" : "medrxiv";
    const days = input.days || 30;
    const maxResults = input.max_results || 10;
    const category = String(input.query || "").toLowerCase().replace(/ /g, "_");
    const end = new Date().toISOString().slice(0, 10);
    const start = daysAgo(days);
    const url = `https://api.biorxiv.org/details/${server}/${start}/${end}/0?category=${encodeURIComponent(category)}`;
    const data = await httpJson(url, { headers: { "User-Agent": "codex-ai4scholar-skill/0.1" } });
    return {
      papers: (data.collection || []).slice(0, maxResults).map((item) => mapRxivPaper(item, server)),
    };
  }

  if (tool === "download_arxiv") {
    const paperId = input.paper_id;
    return {
      paper_id: paperId,
      abs_url: `https://arxiv.org/abs/${paperId}`,
      pdf_url: `https://arxiv.org/pdf/${paperId}.pdf`,
    };
  }

  if (tool === "auto_cite") {
    if (!config.apiKey) {
      fail("AI4Scholar API key is required for auto_cite");
    }
    return httpJson(`${baseUrl}/api/proxy/auto-cite`, {
      method: "POST",
      headers: authHeaders(config),
      body: JSON.stringify({
        text: input.text,
        mode: input.mode,
        minCitations: input.minCitations,
        field: input.field,
        yearPreference: input.yearPreference,
        excludePreprints: input.excludePreprints,
        excludeConferences: input.excludeConferences,
        citationStyle: input.citationStyle,
      }),
    });
  }

  fail(`Unsupported tool: ${tool}`);
}

async function main() {
  const tool = process.argv[2];
  if (!tool) {
    fail("Usage: ai4scholar.js <tool> '<json>'");
  }
  const input = await readInput();
  const config = loadConfig();
  const result = await run(tool, input, config);
  console.log(JSON.stringify({ ok: true, tool, result }, null, 2));
}

main().catch((error) => {
  fail(error instanceof Error ? error.message : String(error));
});
