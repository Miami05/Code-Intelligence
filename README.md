# Code Intelligence Platform

> AI-Powered Code Analysis & Quality Gates — Built over 14 Sprints

![Tech Stack](https://img.shields.io/badge/Backend-FastAPI%20%7C%20PostgreSQL%20%7C%20pgvector-38bdf8?style=flat-square)
![AI](https://img.shields.io/badge/AI-OpenAI%20GPT--4%20%7C%20Embeddings-38bdf8?style=flat-square)
![Frontend](https://img.shields.io/badge/Frontend-React%20%7C%20TypeScript%20%7C%20Tailwind-38bdf8?style=flat-square)
![Languages](https://img.shields.io/badge/Languages-Python%20%7C%20C%20%7C%20COBOL%20%7C%20Assembly-38bdf8?style=flat-square)
![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF?style=flat-square&logo=github-actions)

---

## Overview

The **Code Intelligence Platform** is an AI-powered system that automatically analyzes code quality, detects issues before they reach production, and enforces quality standards through configurable gates integrated directly into your development workflow.

It eliminates the pain of manual code reviews, silently accumulating technical debt, and inconsistent quality enforcement across teams.

---

## Features

### 🧠 Intelligence Layer
- **AI Code Smell Detection** — GPT-4 powered analysis identifying 12 types of code smells
- **Duplication Engine** — Detects similar code blocks across files with similarity scoring
- **Semantic Code Search** — Vector embeddings (OpenAI Ada) with cosine similarity search
- **Security Vulnerability Scanner** — Scans for known vulnerabilities across multiple languages
- **Performance Profiling** — Identifies bottlenecks and hotspots in your codebase

### ⚙️ Automation Layer
- **Auto-Documentation Generator** — Creates docstrings for undocumented functions automatically
- **Quality Gate Engine** — 7 configurable threshold types to block failing deployments
- **GitHub Actions Integration** — Automatic quality checks on every Pull Request
- **GitHub Webhook Integration** — Real-time PR analysis triggered on `opened`, `synchronize`, and `reopened` events
- **Run History & Reports** — Detailed HTML reports for every quality gate run
- **Notifications** — Real-time alerts via Slack and email

---

## CI/CD Integration (Sprint 14)

Every Pull Request is automatically analyzed by the Quality Gate engine via GitHub Actions.

### How It Works

```
Pull Request Opened
       │
       ▼
GitHub Actions Workflow
       │
       ▼
POST /api/cicd/webhook/github
       │
       ▼
Quality Gate Engine runs 4 checks:
  ✅ Complexity
  ✅ Code Smells
  ✅ Vulnerabilities
  ✅ Duplication
       │
       ▼
Result posted as PR comment
       │
  ┌────┴────┐
  ▼         ▼
PASSED   BLOCKED
  ✅        ❌
```

### Setup

1. Add the workflow file to your repo at `.github/workflows/code-intelligence.yml`
2. Set the `CODE_INTEL_URL` secret to your backend URL (e.g. via [ngrok](https://ngrok.com) for local dev)
3. Open a Pull Request — the quality gate runs automatically

### Quality Gate Thresholds

| Check | Default Threshold |
|---|---|
| Max Cyclomatic Complexity | 10 |
| Max Code Smells | 20 |
| Max Critical Smells | 0 |
| Max Vulnerabilities | 5 |
| Max Critical Vulnerabilities | 0 |
| Min Quality Score | 70% |
| Max Duplication | 10% |

All thresholds are configurable via `PUT /api/cicd/quality-gate/{repository_id}`.

---

## Tech Stack

| Layer | Technologies |
|---|---|
| **Backend** | FastAPI, PostgreSQL 15, pgvector, Alembic, Redis |
| **AI / ML** | OpenAI GPT-4, Ada Embeddings, pgvector |
| **Frontend** | React 18, TypeScript, Tailwind CSS, Recharts, Lucide Icons |
| **DevOps** | GitHub Actions, GitHub Webhooks, Docker, ngrok |

---

## Development Journey

| Sprints | Phase | Key Deliverables |
|---|---|---|
| 1–7 | **Foundation** | GitHub ingestion, PostgreSQL + pgvector, AST parsing, React dashboard |
| 8–11 | **Intelligence** | GPT-4 smell detection, duplication engine, semantic search, security scanner |
| 12–13 | **Automation** | Auto-docs, quality metrics tracking, 4-tab analysis dashboard |
| 14 | **CI/CD Integration** | Quality gate engine, GitHub Actions workflow, webhook handlers, Slack/email notifications, HTML reports |

---

## Supported Languages

- Python
- C
- COBOL
- Assembly

---

## Key Metrics

- ✅ **14 Sprints** completed
- ✅ **25+ Database migrations** managed via Alembic
- ✅ **4 Programming languages** supported
- ✅ **7 Configurable quality gate** threshold types
- ✅ **1536-dimension** vector embeddings for semantic search
- ✅ **GitHub Actions** CI/CD pipeline with automatic PR quality checks

---

## Roadmap

- [ ] Multi-language expansion — Go, Rust, C++
- [ ] IDE plugins for VS Code, IntelliJ, and PyCharm
- [ ] ML-powered predictive bug detection using historical patterns
- [ ] Integrations with Jira, Linear, Azure DevOps, and GitLab
- [ ] Custom quality gate rule engine
- [ ] Team collaboration features and code review workflows

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

<p align="center">
  <b>Code Intelligence Platform</b> • February 2026 • Built by <a href="https://github.com/Miami05">Miami05</a>
</p>
