
# job-alerts

A small personal scraper that checks several companies' careers pages daily and
tells you about **new** openings that match your profile.

## How it works

```
fetch every company  →  drop jobs seen before  →  keep profile matches  →  notify
```

State lives in `data/seen_jobs.json`, so after the first run you only ever hear
about postings that are genuinely new.

## Setup (uv)

```bash
uv sync                     # install deps from pyproject.toml / uv.lock
uv run main.py              # run once, print matches to the console
```

## Configure

Two files you'll edit regularly:

- **`companies.yaml`** — the companies to track. Adding one on a known ATS
  (Greenhouse, Lever, Ashby) is just a name + `slug`.
- **`profile.yaml`** — your `include` / `exclude` keywords and optional
  `locations`.

## Email digests

```bash
cp .env.example .env        # fill in SMTP creds (Gmail → use an App Password)
uv run main.py --channel email
```

## Run it daily in the cloud

`.github/workflows/daily.yml` runs the whole thing every morning via GitHub
Actions — no server needed. Put your SMTP values in the repo's
**Settings → Secrets and variables → Actions**.

## Add a new company

1. **On a supported ATS?** (Greenhouse / Lever / Ashby) — add an entry to
   `companies.yaml` with its `slug`. Done, no code.
2. **Bespoke site?** — copy `jobalerts/scrapers/cabify.py`, adjust the parsing,
   `@register("yourname")`, add an import line to
   `jobalerts/scrapers/__init__.py`, and reference `ats: yourname` in the config.

## Project layout

```
companies.yaml            # companies to track  (edit often)
profile.yaml              # your match criteria (edit often)
main.py                   # entrypoint
jobalerts/
  models.py               # Job, Company
  config.py               # loads the YAML files
  registry.py             # ATS name -> scraper (decorator-based)
  matching.py             # profile matching
  storage.py              # seen-jobs state (JSON, swappable)
  scrapers/               # one file per ATS; self-registering
  notify/                 # console + email channels
data/seen_jobs.json       # state (gitignored)
tests/                    # offline unit tests
```

## Tests

```bash
uv run pytest
```
