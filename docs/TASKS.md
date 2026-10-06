# Tasks

Welcome to the sprint board. These are real-shaped tickets — the kind a tech lead drops into Jira on a Monday morning. They tell you **what**, not **how**. Figuring out the *how* is part of what we are evaluating.

**Priority:** FT-0 first, then FT-1 and FT-2 are the main ones. FT-3 is optional — only if you have time left. A finished `FT-1` with a clean diff is a stronger submission than two rushed tickets with broken tests.

When in doubt:
- Read [`ARCHITECTURE.md`](ARCHITECTURE.md) to know where code lives.
- Read [`CODING_GUIDELINES.md`](CODING_GUIDELINES.md) to know what good looks like.
- Write down anything you would have asked the team in a real sprint.

---

## FT-0 · Architecture review

**Type:** Reading + writing
**Estimate:** ~25 min
**Priority:** P0

### Story
As a senior joining this codebase, before I touch anything I want to form an opinion on what's well-built and what I would change, so my later commits aim at the right things.

### Context
The repo has rough edges. Some are intentional, some are not. We want to see what you notice in your first half hour — before you start writing code.

### What to do
Read at minimum:

- [`docs/ARCHITECTURE.md`](ARCHITECTURE.md) and [`docs/CODING_GUIDELINES.md`](CODING_GUIDELINES.md).
- [`workout_sessions/features/get_workout_details_feature/`](../workout_sessions/features/get_workout_details_feature/) — the "good" read-path template.
- [`workout_sessions/features/create_workout_feature/`](../workout_sessions/features/create_workout_feature/) — the "good" write-path template.

Read whatever else you need (other features, the `models.py` files) to feel like you understand the place.

Then write `reports/ARCHITECTURE_REVIEW.md` covering:

1. **What's solid.** Two or three things you'd keep as-is.
2. **What you'd change.** Two or three things you'd change — what, where (`<file>:<line>`), and why. Generic critique ("this could be more tested") doesn't count.
3. **What confused you.** What took longer to understand than it should have.

Same rules as every other report: direct, for a human reader, no LLM slop. See [About the reports](../README.md#about-the-reports).

### Definition of done
- [ ] `reports/ARCHITECTURE_REVIEW.md` exists.
- [ ] At least two `<file>:<line>` references in the "what you'd change" section.
- [ ] Commits prefixed with `FT-0:`.

### How we read this
We're not looking for a polished essay. We're looking for signal:

- That you actually read the docs and the templates — precise `<file>:<line>` refs tell us.
- That you have taste — "what you'd change" is concrete, not generic.
- That you're honest about what you didn't get. Saying "I was confused by X" beats pretending.
- Bonus: things you flag here that we expect a senior to dig into later (FT-2) tell us your eye was already sharp on the first read.

---

## FT-1 · Social activity feed

**Type:** Feature
**Estimate:** ~60 min
**Priority:** P0

### Story
As a user opening the Social screen, I want to see a feed of recent workouts from the people I follow, so that I have a reason to come back every day.

### Context
The feed must be built to power the Social screen of the current production version of Symmetry. It has to stay fast on realistic data: if it's slow, users feel it straight away.

### Design freedom — your call
The shape of this feature is the part we want you to design. We won't tell you:

- **Route, method, URL.** Pick one consistent with the existing URL conventions in this repo and justify it.
- **Response shape.** Design it so the frontend can render each feed item in one round-trip — workout meta, owner, counts (likes / comments / exercises), the three latest likers (id + display name + avatar), and whether the caller already liked the workout. Justify your trade-offs.
- **Pagination strategy.** Offset/limit or cursor. Pick one, say why.
- **Where the feature folder lives.** Across `social/`, `users/`, `workout_sessions/`. Pick one and justify.
- **Cross-domain queries.** Pulling workouts (`workout_sessions`) filtered by follows (`social`) means crossing an app boundary. Decide whether to go through `core/apis/domain_to_domain/` or keep the join local — and justify.

In `reports/FT-1.md`, list **two alternatives you considered and rejected**, and why. We want to see the design space you explored, not only the option you landed on.

### Definition of done
- [ ] Endpoint returns everything the Social screen needs for each feed item in a single round-trip: workout meta, owner, counts, three latest likers, whether the caller liked it.
- [ ] Feed contains workouts from everyone the caller follows, sorted most recent first. No artificial cap — the client can keep paginating until there are no more workouts to return.
- [ ] Caller follows nobody → empty `200`, not `500`.
- [ ] The caller's own workouts never appear in the response.
- [ ] Loads fast on realistic data. The test proves it: an N+1 should fail your suite, not be discovered in code review.
- [ ] **Cache.** If your design caches anything, name the key, the TTL, and who invalidates it in `reports/FT-1.md`. Note where the invalidation runs (e.g. inside `transaction.on_commit` to avoid firing on a rolled-back write). If you don't cache, justify why.
- [ ] **Migrations.** If your design adds an index or a column, include the migration plan in `reports/FT-1.md`: how would you ship it on a table with millions of rows in production without locking it?
- [ ] Test covers the happy path and at least one of the edge cases above.
- [ ] Commits prefixed with `FT-1:`. `reports/FT-1.md` written.

### Out of scope (don't build)
- A feed for users the caller does **not** follow ("discovery").
- Like/unlike actions invoked from the feed response.
- Push, email, or any kind of notification.
- A read-receipt / "seen" mechanism.

### Edge cases the reviewer will check
- Caller follows nobody → empty `200`, not `500`.
- Caller follows users with no workouts → empty `200`.
- The caller's own workouts are never in the response.
- "Three latest likers" stays correct when a workout has 0, 1, 2 or 3+ likes.

### Questions for the team
The candidate adds theirs here, with the decision taken in the meantime.

- _(empty)_

---

## FT-2 · Code review — `PATCH /users/me/preferences/`

**Type:** Code review
**Estimate:** ~30 min
**Priority:** P0

### Story
As a senior reviewing a teammate's PR, I want to deliver the version of the feature I would have signed off on, so the code we ship is the code we'd want to maintain.

### Context
The frontend team needed an endpoint to update the caller's fitness preferences. A teammate picked up the ticket and shipped a first version. They verified manually that the endpoint returns the expected response for the inputs the spec calls out, and tagged you as the reviewer.

The spec they worked from was:

> `PATCH /users/me/preferences/` accepts a partial update of the caller's preferences:
>
> - `experience_level` — one of `BEGINNER` / `INTERMEDIATE` / `ADVANCED`.
> - `primary_goal` — one of the `TrainingGoal` choices.
> - `training_frequency_per_week` — positive integer.
> - `available_equipment` — list of `Equipment` codes.
>
> The response returns the caller's updated preference fields plus a `trainable_exercise_count` — the number of exercises in the catalog the user can perform with their current equipment selection. The frontend team uses that count for the "X exercises available for you" card on the home screen.

The implementation lives in [`users/features/update_my_preferences_feature/`](../users/features/update_my_preferences_feature/).

### Design freedom — your call
- **How deep you go.** You decide what's worth changing and what's a stylistic taste call. Be opinionated either way.
- **What you choose to leave as-is.** If you decide some change isn't worth making in this PR, that's a valid choice — you just have to justify it.

### Definition of done
- [ ] The endpoint behaves identically from the outside for every input it used to accept.
- [ ] `reports/FT-2.md` lists every change you made (and anything you considered changing but chose not to), with what you saw, why, and what you did about it. Using `CG` numbers helps the reviewer match your comments to the conventions.
- [ ] Commits prefixed with `FT-2:`.

### Out of scope (don't build)
- A new endpoint, a new model, a new field.
- A whole rewrite of `UserProfile` or `ExerciseTemplate`.
- Tests for unrelated features — Boy Scout Rule applies to **this** feature only.

### How we read this
The diff tells us what you changed. The report tells us what you **saw**. The two answers are not the same — a senior who changed 5 things but noticed 8 is stronger than one who changed 7 silently without noticing the eighth. We count the second number.

---

## FT-3 · Design exercise — pick one and sketch it

**Type:** Design
**Estimate:** ~45 min
**Priority:** P1 (optional — only if you finish FT-0, FT-1 and FT-2)

### Why this ticket exists

This one is different from the rest. Beyond evaluating how you write code, we also want to know **what part of the backend pulls you in** — and how you think when a problem doesn't fit on the back of an envelope.

So this ticket is not about programming. It is about **designing a solution**. We picked four topics we think are interesting and we let you choose the one that interests you the most (or propose your own under the same constraints). A senior engineer spends a serious chunk of their time thinking, reading and organising before writing a line of code — that is the part of the role we want to see in action here. Use the time to read, think, and write; not to ship code we won't run.

What we get out of this ticket:

- Where you'd want to go deeper if you joined the team.
- How you reason about something complex and unfamiliar.
- Your taste for tradeoffs — what you keep, what you cut.
- How you communicate a design to people who weren't in your head while you wrote it.

### Pick one

**Option A — AI workout coach.** Design an LLM-powered feature that recommends the user's next workout given their history, goals, recovery state, and available equipment. Things you will probably want to think about: context window (what does the model actually see?), latency and cost, safety (what stops it from suggesting a 1RM attempt to a beginner?), evaluation (how do you know the suggestion was any good?), and the fallback when the LLM is down.

**Option B — Exercise search.** Design `GET /exercises/search/` as a power user expects it: fast typeahead, fuzzy matching, multi-locale name resolution, and synonyms. The current `/exercises/?search=` does a substring filter and that is it. Think about indexing strategy, ranking (popularity vs. relevance), how to incorporate `ExerciseTemplateAlias`, graceful degradation on a typo, and whether you would put the index inside Postgres or in a separate store.

**Option C — "What should I train today?"** Design an endpoint that, given the requesting user, returns a concrete recommendation: which routine inside their active plan to do, with which exercises swapped out based on recent recovery and available equipment. Think about how you combine `UserActiveWorkoutPlan` + `MuscleGroupRecovery` + `UserProfile`, the cold-start case (no history), what "swap an exercise" means in this model, and where the computation runs (request time, cached, background job).

**Option D — Your own.** If none of the above is the most interesting question to you, propose one. Constraints: it must touch at least two of the existing apps **and** it must require either a denormalization or a Celery task — i.e., the answer must be non-trivial.

### Template

Open [`docs/DESIGN.md`](DESIGN.md) in the repo. The file is already there with the four sections you must fill — write your design directly under each heading. The structure is fixed; the content is yours. Each section has a short note (in HTML comments) describing what to cover; delete them as you write or leave them, your call.

The four sections are:

1. **Solution overview** — a short, plain-language description of the approach.
2. **Reasoning & decisions** — the interesting half of the document. Argument, not assertion.
3. **Codebase tree** — where the new code lives in the repo.
4. **Task breakdown** — the tickets that would come out of this design, parallelisable, plus open questions at the end.

### Out of scope (don't build)
- Working code. This is a design doc — no `views.py`, no migrations, no tests.
- A ten-page essay. A senior knows when to stop writing.
- A full RFC structure with seven sections. The four above are enough — if a thought doesn't fit any of them, it probably doesn't belong in the doc.

### Definition of done
- [ ] `docs/DESIGN.md` filled with the four sections above.
- [ ] Commit prefixed with `FT-3:`.

### How we read this

We're reading for **five things**, distributed across the four sections:

- **Clarity of the overview.** Can a reader skim section 1 and understand the shape of the solution? If not, the rest of the document is wasted.
- **Quality of the reasoning + depth on what matters at scale.** Section 2 is where a senior shows up. Arguments backed by references, benchmarks or honest comparisons beat "I think". Cache invalidation, Celery fan-out, migration safety on large tables — address them or explain why they don't apply; don't skip.
- **Architectural sensibility.** Does the codebase tree in section 3 fit with the vertical-slice layout, the cross-domain rules, the conventions you read in `CODING_GUIDELINES.md`? Or does it ignore them?
- **A team mindset.** Section 4 should let two or three engineers pick this up in parallel. A serial chain of 1 → 2 → 3 → 4 tells us you'd ship this alone.
- **Honesty about what you don't know.** A design doc with zero open questions is a design doc with hidden assumptions. We read the close of section 4 carefully.

Beyond the technical signal, this ticket is also how we read which part of the backend you'd want to own. We are not deciding hiring level from it — we are calibrating what to put in your hands first.

---

## Wrap-up — One last note before you submit

Once you are out of time (or out of tickets), add a short closing block in `reports/WRAP_UP.md` covering:

1. **What you finished and what you didn't.** Per ticket: shipped, partially shipped with a known gap, or not started. Be honest — a well-flagged incomplete ticket is worth more than one that pretends to be done.
2. **What of what we asked you would change or not build at all.** A senior says "this shouldn't exist" when it shouldn't. Tell us if any of FT-0 to FT-3 falls into that category, and why.

That's it. Don't re-write your per-ticket reports — those already live in `reports/`. We read the wrap-up for the two things above and nothing else.

Good luck.
