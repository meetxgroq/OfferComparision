# BenchMarked Documentation

This folder is the single source of project documentation.

## Contents

- `DEPLOY.md` — full deployment guide and operational runbook.
- `design.md` — product and flow design document.
- `Offer Comparison UI redesign Plan.md` — UI redesign implementation plan and references.

## Local Development (Quick Reference)

### Backend

```bash
python api_server.py
```

Runs on `http://localhost:8001`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Runs on `http://localhost:3001`.

## Notes

- Keep any new project documentation in this `docs/` directory.
- Use the root `README.md` only as a short entrypoint to this folder.

## Contributing Docs

- Keep all long-form project documentation in `docs/`.
- Prefer focused, purpose-based names (examples: `DEPLOYMENT_NOTES.md`, `API_AUTH.md`, `RUNBOOK_<topic>.md`).
- Update this index when adding, renaming, or removing any document.
- Keep root-level markdown minimal (entrypoint only) to avoid duplicate sources of truth.

### New Doc Template

Use this header at the top of every new document:

```md
# <Document Title>

Purpose: <1-2 sentence summary of what this document covers>
Owner: <team or person>
Last Updated: <YYYY-MM-DD>
```
