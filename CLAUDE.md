# The Specialist for Lost Handbooks

This repo holds the PhD-side game prototype for "Information Theoretic Models of Curiosity in Hierarchical Models of the World" — a machine-room puzzle game used to elicit and study curiosity-driven behavior.

- `Version_0/` — first prototype (Pygame). Kept as legacy reference for asset style and prior implementation patterns. Not being extended further.
- `Version_1/` — the active rebuild: assets restructured into a coherent block-module form, code architecture cleaned up. See `Version_1/CLAUDE.md` for full context. This is a working Pygame prototype, not the shipped experiment — it doesn't run in a browser, so it can't be deployed to online participants as-is.
- `Version_2/` — the browser-deployable port of `Version_1` (renamed from `Version_1_web` on 2026-09-05, since this is now where all active development happens), needed because participant recruitment (Prolific / Mechanical Turk) requires a zero-install, browser-based experience. **Start here for anything related to running the actual study.** See `Version_2/CLAUDE.md` for the full deployment-strategy reasoning and the file-by-file porting plan. Its `assets/` is its own independent copy of `Version_1/assets/` (not a reference to it) — edit sprites there, not in `Version_1/`.

Design and research decisions for this project are tracked in a Claude.ai project ("PhD Topic") backed by a Notion workspace, not in this repo's issue tracker. `Version_1/docs/design/` mirrors the relevant Notion pages as of the last sync — if something here looks stale, ask the user to confirm against the live Notion docs before assuming it's current.
