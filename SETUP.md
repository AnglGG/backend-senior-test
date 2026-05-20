# Setup — submitting your work

This document is about how you ship your work to us.

## TL;DR

1. Clone this repo into a fresh folder.
2. Reset its history so your commits start from a clean slate.
3. Create a **private** repo in your own GitHub account, push to it, and invite the reviewer as a collaborator.
4. Work in branches (one per ticket) and open Pull Requests against the `main` of **your** repo.
5. Send the PR link(s) to the reviewer when you're done.

## Setup

```bash
git clone <URL of this repo> my-submission
cd my-submission
rm -rf .git && git init -b main
git add . && git commit -m "chore: starting point"

gh repo create <your-handle>/symmetry-backend-submission --private --source=. --push
gh api repos/<your-handle>/symmetry-backend-submission/collaborators/<reviewer-handle> --method PUT
```

## Daily flow

```bash
git checkout -b ft-1
# ...work...
git commit -m "FT-1: short description"
git push -u origin ft-1
gh pr create --base main --head ft-1
```

Repeat per ticket. One PR per ticket is the cleanest, but a single PR with the ticket name in each commit message also works.

## What to send the reviewer

A single message with:
- Link to your repo (the reviewer already has access via the collaborator invite).
- Links to your PR(s).
- Anything you want flagged before they start reading.
