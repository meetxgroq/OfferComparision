# OfferCompare Pro — Project Structure

Purpose: Central reference for the repository layout, module responsibilities, and dependencies.
Last Updated: 2026-03-28

## Overview

OfferCompare Pro is an intelligent job offer analysis platform built on the **PocketFlow** framework.
It compares compensation packages, work-life balance, growth opportunities, and market data across
multiple offers, then produces AI-powered recommendations.

**Inputs:** Job offer details (company, position, location, compensation), user preferences.
**Outputs:** Ranked offers with scores, AI analysis, visualizations, and a final report.

## Repository Tree

```
OfferComparision/
├── main.py                        # Application entry point (CLI menu)
├── flow.py                        # PocketFlow flow definitions & wiring
├── nodes.py                       # PocketFlow node implementations
├── api_server.py                  # FastAPI backend (production)
│
├── utils/                         # Utility / helper modules
│   ├── __init__.py
│   ├── auth.py                    # Authentication helpers (Supabase)
│   ├── cache.py                   # File-based caching with TTL
│   ├── call_llm.py                # Multi-provider LLM wrapper (Gemini/OpenAI/Claude)
│   ├── col_calculator.py          # Cost-of-living adjustment calculator
│   ├── company_db.py              # Company culture & benefits database
│   ├── config.py                  # Environment-driven configuration loader
│   ├── json_sanitize.py           # JSON response sanitization
│   ├── levels.py                  # Engineering levels / ladder mapping
│   ├── locations.py               # Location normalization & lookup
│   ├── market_data.py             # Salary benchmarking & market ranges
│   ├── positions.py               # Position / title normalization
│   ├── scoring.py                 # Weighted scoring algorithm
│   ├── tax_calculator.py          # Tax estimation by location
│   ├── us_cities.py               # US city metadata
│   ├── viz_formatter.py           # Chart.js data preparation
│   └── web_research.py            # AI-powered company research agent
│
├── scripts/                       # Helper / launcher scripts
│   ├── mock_api_server.py         # Mock FastAPI server for dev (no LLM calls)
│   ├── setup_local.py             # Interactive local environment setup
│   ├── start_server.py            # Server launcher (auto-detects real vs mock)
│   ├── start_all.bat              # Windows: start backend + frontend
│   └── start_backend.bat          # Windows: start backend only
│
├── tests/                         # Pytest test suite
│   ├── __init__.py
│   ├── conftest.py                # Shared fixtures
│   ├── test_integration.py        # End-to-end flow tests
│   ├── test_nodes.py              # Node unit tests
│   └── test_utils.py              # Utility function tests
│
├── frontend/                      # Next.js web UI
│   ├── app/                       # Next.js App Router pages
│   │   ├── globals.css
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── components/                # React components
│   │   ├── AdvancedOfferForm.tsx
│   │   ├── AnalysisResults.tsx
│   │   ├── FileUpload.tsx
│   │   ├── LoginButton.tsx
│   │   ├── OfferCards.tsx
│   │   ├── OfferForm.tsx
│   │   ├── PreferencesForm.tsx
│   │   ├── PreferencesPanel.tsx
│   │   ├── ProfileManager.tsx
│   │   ├── Results.tsx
│   │   ├── Slider.tsx
│   │   └── VisualDashboard.tsx
│   ├── contexts/
│   │   └── AuthContext.tsx         # Supabase auth context
│   ├── data/
│   │   └── companies.ts           # Static company data
│   ├── lib/
│   │   ├── api.ts                 # Backend API client
│   │   └── supabase/
│   │       ├── client.ts          # Supabase browser client
│   │       └── server.ts          # Supabase server client
│   ├── types/
│   │   └── index.ts               # TypeScript type definitions
│   ├── Dockerfile                 # Frontend container image
│   ├── package.json
│   ├── package-lock.json
│   ├── next.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── tsconfig.json
│   ├── .eslintrc.json
│   ├── .env.local                 # Frontend env vars (local)
│   └── next-env.d.ts
│
├── docs/                          # Project documentation
│   ├── README.md                  # Docs index & contributing guide
│   ├── design.md                  # Architecture & flow design
│   ├── DEPLOY.md                  # Deployment guide & operational runbook
│   └── Offer Comparison UI redesign Plan.md
│
├── supabase/
│   └── migrations/
│       └── 001_user_usage.sql     # User usage tracking schema
│
├── .github/workflows/
│   ├── ci.yml                     # CI: lint + pytest on push/PR
│   └── deploy-cloudrun.yml        # CD: deploy to Google Cloud Run
│
├── Dockerfile                     # Backend container image
├── docker-compose.yml             # Local multi-service orchestration
├── requirements.txt               # Python dependencies
├── environment.yml                # Conda environment spec
├── pytest.ini                     # Pytest configuration
├── .env.example                   # Environment variable template
├── .gitignore
├── .dockerignore
├── .cursorrules                   # AI agent coding guidelines
├── AGENTS.md                      # Workflow orchestration rules for agents
├── README.md                      # Project overview
├── SETUP_GUIDE.md                 # Quick-start setup guide
├── TODO.md                        # Development roadmap & progress
└── assets/
    └── banner.svg                 # Project banner image
```

## Module Dependency Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                          main.py                                 │
│                    (CLI entry point)                              │
└──────────┬───────────────────────────────────────────────────────┘
           │ imports
           ▼
┌──────────────────────┐       ┌───────────────────────────────────┐
│      flow.py         │──────▶│           nodes.py                │
│  (flow definitions)  │       │  (PocketFlow Node subclasses)     │
└──────────────────────┘       └───────────┬───────────────────────┘
                                           │ imports
                                           ▼
                               ┌───────────────────────────────────┐
                               │           utils/                   │
                               │  call_llm, scoring, market_data,  │
                               │  col_calculator, web_research,    │
                               │  company_db, viz_formatter, etc.  │
                               └───────────────────────────────────┘

┌──────────────────────┐
│    api_server.py     │──────▶ flow.py, nodes.py, utils/
│  (FastAPI backend)   │
└──────────────────────┘

┌──────────────────────┐
│     frontend/        │──────▶ api_server.py (HTTP)
│  (Next.js web UI)    │
└──────────────────────┘
```

## Module Descriptions

| Module | Responsibility |
|--------|---------------|
| `main.py` | CLI interface: interactive analysis, demo mode, utility testing |
| `flow.py` | Creates and wires PocketFlow flows connecting all nodes |
| `nodes.py` | Implements 8 PocketFlow nodes (collection, research, COL, benchmarking, scoring, AI analysis, visualization, reporting) |
| `api_server.py` | FastAPI REST API exposing `/api/analyze`, `/api/demo`, `/health` |
| `utils/` | Pure utility functions for LLM calls, data processing, caching, and external APIs |
| `scripts/` | Developer convenience scripts for setup, server launching, and mocking |
| `tests/` | Pytest suite covering utils, nodes, and integration flows |
| `frontend/` | Next.js web application with offer input forms, results display, and visualizations |
| `docs/` | Architecture design, deployment notes, and UI redesign plans |
| `supabase/` | Database migration scripts for user tracking |

## Cleanup Log (2026-03-28)

Files removed during cleanup:
- `Calculating` — orphaned log fragment (1 line)
- `Estimated` — orphaned log fragment (1 line)
- `GEMINI.md` — duplicate of `.cursorrules` framework docs (1670 lines)
- `company_levels_cache.json` — local cache artifact (already gitignored)
- `__pycache__/` directories — Python bytecode artifacts
- `.pytest_cache/` — pytest cache directory

Files reorganized:
- `start_server.py` → `scripts/start_server.py`
- `setup_local.py` → `scripts/setup_local.py`
- `start_all.bat` → `scripts/start_all.bat`
- `start_backend.bat` → `scripts/start_backend.bat`
- `mock_api_server.py` → `scripts/mock_api_server.py`

Added to `.gitignore`:
- `monitor.txt` — transient monitoring file
