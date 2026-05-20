# Symmetry Lite — Backend Senior Technical Assessment

Welcome to the repository for our backend senior technical assessment — a small but real Django REST codebase prepared for evaluating senior backend engineering candidates at Symmetry.

## Who will see this project?
Your submission will be reviewed by senior backend engineers at Symmetry. We are not looking for someone who can recite a textbook; we are looking for someone who can walk into a codebase they have never seen, read it fast, separate the signal from the noise, and ship work that the next engineer on call will not curse you for.

This is the exact kind of work you will do at Symmetry from day one. The codebase you see here is intentionally a miniature of the real one: same vertical-slice layout, same separation of concerns, same trade-offs between strict architecture and pragmatic shortcuts. If you join, you will spend most of your time in something that feels like this — only with 50× the volume.

## To what standards will we judge your work?
We will judge your work by:
- The quality of the code you ship in three hours.
- Your ability to **read** code that someone else wrote — including code that is intentionally messy.
- Your ability to **say what you would change** even if you do not have time to change it.
- Your alignment with Symmetry's 3 core values:
  - **Truth is King**
    - You search the truth without regards to other people's opinions or the way the codebase happens to be written today. If you believe something in this repo is wrong, say it — refactor it, or at least call it out in your report. The fact that a piece of code is already there is not an argument that it should stay there.
  - **Total Accountability**
    - You are responsible for everything that goes out under your name. If you spot a bug in a ticket that is not yours, you are still responsible for the user who will hit it. If your refactor breaks an unrelated path, that is on you, not on whoever wrote the path. There are no clean handoffs.
  - **Maximally Overdeliver**
    - You give more than what is asked. The tickets in [`docs/TASKS.md`](docs/TASKS.md) describe a minimum bar. If you finish them with time to spare, you do not stop — you add the test that was missing, you write the index that should exist, you sketch the next ticket. We did not build Symmetry hiring people who do exactly what they are told.

We know this is a high bar. Symmetry is not built for the ordinary; it is crafted for the exceptional. We are not looking for your average Joe. We are looking for engineers who treat a 3-hour test the same way they would treat a 3-month project — with care, with taste, and with skin in the game.

*Note: you might take the third value as a hint that the assignment is a minimum, not a ceiling.*

## The clock and the scope
You have **three hours**. The clock starts when you open [`docs/TASKS.md`](docs/TASKS.md). What we expect to see at the end:

- Code that we can pull and run.
- A short report at the bottom of `docs/TASKS.md` (or `REPORT.md` if you prefer a new file) describing what you did, what you would have done with more time, and what you would change about the codebase as you found it.
- Honesty about what is finished and what is not. A half-finished, well-flagged ticket is worth more to us than a finished one that hides its shortcuts.

You do not need to finish every ticket. You **do** need to make every minute count.

---

## Getting started

### Technologies used
- [Django 5.1](https://docs.djangoproject.com/en/5.1/)
- [Django REST Framework 3.15](https://www.django-rest-framework.org/)
- [PostgreSQL 16](https://www.postgresql.org/docs/16/index.html)
- [Docker Compose](https://docs.docker.com/compose/)

You do not need to know any of these deeply. You do need to read fast.

### Quickstart
```bash
cp .env.example .env
docker compose up
```

That's it. On the first run the container migrates the schema, seeds a realistic demo dataset (~190k rows: catalogue, users, plans, sessions, social graph, projections), and starts the dev server. The seed step is idempotent, so subsequent runs only re-attach to existing data.

The API will be available at **`http://localhost:8000/`**.

### Interactive API docs
The OpenAPI schema and Swagger UI ship out of the box:

- **`http://localhost:8000/api/schema/docs/`** — Swagger UI. Click *Authorize* and paste a user id (1–5) to send `X-Test-User-Id` automatically with every "Try it out" request.
- `http://localhost:8000/api/schema/` — raw OpenAPI 3 YAML.

### Authentication
Real auth is intentionally out of scope. You identify yourself by sending the `X-Test-User-Id` header with the user's primary key. Users `1`–`5` are good starting points.

> **In production this is Firebase + short-lived JWTs with refresh.** When you reason about scale in FT-3, assume `request.user` is hot and not free — every request resolves it via a Firebase call and a JWT verification. The fake `X-Test-User-Id` here is a 3-hour convenience, not a representative cost.

```bash
curl -H "X-Test-User-Id: 1" http://localhost:8000/users/me/
curl -H "X-Test-User-Id: 1" http://localhost:8000/exercises/
```

Endpoints that do not require a caller (catalogue reads, plan details) work without the header.

### Running tests
```bash
docker compose exec web python manage.py test
```
One example test ships in `workout_sessions/features/get_workout_details_feature/tests/` so you can see the local convention (DRF `APITestCase` + `X-Test-User-Id` header).

### Re-seeding from scratch
```bash
docker compose down -v   # drops the postgres volume
docker compose up        # re-seeds clean
```

---

## Production context — for reasoning, not for replication

The numbers below describe the live system, not this repo. You do not need to replicate this infrastructure in three hours. You are expected to reason as if you were shipping into it — an endpoint that takes 800 ms on the seed data is not "fast enough", even if the seed only has 120 users.

- More than 1M registered users, tens of thousands daily active, with peaks in the 30k–60k concurrent range.
- Mobile-first, offline-first: clients write locally and sync periodically. Expect duplicate writes, retried writes, and out-of-order arrivals.
- Postgres single primary, Redis (cache + Celery broker), Celery for fan-out and background work. Yes, the cache layer in this repo is real — it is the same stack as production.

## Deliverable

- **Format.** Clone this repo (don't fork) into a fresh folder, then create a **private** repo in your own GitHub account and push your work there. Invite the reviewer as a collaborator and open Pull Requests inside your private repo. See [`SETUP.md`](SETUP.md) for the exact commands.
- **Commits.** At least one commit per ticket, prefixed with the ticket key (`FT-1: …`). Splitting a ticket into two or three logical commits is fine and encouraged. The history is read as a signal of how you organize work.
- **Reports.** One per ticket in `reports/FT-N.md`. See [About the reports](#about-the-reports) below — they are not a tech spec. `reports/` is your submission; `docs/` is the repo's own documentation — don't conflate them.
- **If you get blocked**, do not stop. Write the question you would have asked the team in `reports/QUESTIONS.md`, take the best decision you can with the info you have, and keep moving. We evaluate how you unblock yourself, not whether you do.

### About the reports

We assume the code in your submission was largely written by an LLM, supervised by you. That's how engineers ship in 2026, and we're not going to pretend otherwise.

The reports are different. They can be drafted with an LLM too — that's fine. What we **don't** want is the standard LLM output: five-page walkthroughs, exhaustive bullet lists, every section padded to look thorough. We want something a teammate can actually skim and walk away knowing how you thought about the ticket.

For each ticket, write `reports/FT-N.md`. Direct, focused, **as long as it needs to be and no longer**. Cover:

- What you decided where the ticket gave you freedom.
- What you considered and rejected, and why.
- What you would have asked the team if this were a real sprint.
- What you would change with more time.

If you ran out of time on a section, write "ran out of time" and move on. We read this for how you think, not for completeness.

---

## Now, the assignment...
Your work is described as a small set of Jira-style tickets in [`docs/TASKS.md`](docs/TASKS.md). They are deliberately written the way a real ticket would be written: a goal, a context, a definition of done — not a step-by-step recipe. Figuring out the *how* is part of what we are evaluating.

### Before you write a line of code (first 15–20 minutes)

Spend the first 15–20 minutes reading, in order. Submissions that skip this step are visibly worse — we've measured.

1. [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) (5 min) — bounded contexts and folder layout.
2. [`docs/CODING_GUIDELINES.md`](docs/CODING_GUIDELINES.md) (5 min) — the CGs reviewers cite by number (`CG3.1`, `CG7.2`, …).
3. [`workout_sessions/features/get_workout_details_feature/services/get_workout_details.py`](workout_sessions/features/get_workout_details_feature/services/get_workout_details.py) (5 min) — the local template for **read paths**.
4. [`workout_sessions/features/create_workout_feature/services/create_workout.py`](workout_sessions/features/create_workout_feature/services/create_workout.py) (5 min) — the local template for **write paths**.

## Index
- **[`docs/TASKS.md`](docs/TASKS.md)** — your tickets. Start here once you have skimmed the architecture.
- **[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)** — bounded contexts, per-app responsibilities, and where to put new code.
- **[`docs/CODING_GUIDELINES.md`](docs/CODING_GUIDELINES.md)** — the conventions every new feature is expected to follow. Reviewer comments will reference them as `CG{n}`.
- **[`SETUP.md`](SETUP.md)** — how to clone, create your private repo and open PRs against it. Read this first if you haven't set up your submission yet.

## A final note
You will find rough edges in this repo. Some of them are intentional — they exist to see whether you notice them and what you choose to do about them. Calling them out, leaving them alone, or refactoring them are all defensible. **Not noticing them is the one move that is not.**

Good luck. Make it count.
