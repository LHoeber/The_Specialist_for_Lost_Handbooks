# Research context

Mirrored from the "Main Concept" and (partially) "Model Framework" pages in the PhD Topic Notion project (last synced 2026-08-28). Included so Claude Code sessions understand *why* the game has the constraints it has, without needing the full model-architecture material (which lives in Notion and isn't directly implementation-relevant here).

## Project title

"Information Theoretic Models of Curiosity in Hierarchical Models of the World"

## Basic goals

- Investigate drivers of curiosity in computer-game based experiments using information theory and reinforcement learning based approaches.
- Bridge the gap between first-principle based models of curiosity and data-driven models of human behavior.
- Develop new experimental paradigms for curiosity based on the models, to be tested with human participants at various ages and developmental states.
- Contribute to a computational benchmark that tests the explanatory power of different models of curiosity.

## Research questions

- What drives people to seek knowledge without any apparent use?
- What drives exploration without an externally given goal / from pure intrinsic motivation?
- How does intrinsic motivation differ between conditions, within participants (different levels of prior knowledge/familiarity; different kinds of uncertainty — epistemic, aleatoric)?
- How does intrinsic motivation differ between participants, within conditions?

## Where this game fits

The wider project's main paradigm is a VR room-exploration task feeding a learned world-model + curiosity-driver analysis pipeline (see the "Model Framework" Notion page for the full architecture — not reproduced here since it isn't implementation-relevant to the game). The machine-room game is being considered as an additional, more controlled condition: same underlying (PO)MDP structure and information-theoretic framing, but discrete, game-based, and easier to run across ages/developmental stages than full VR. Open questions still being worked through in the design chat (as of last sync):

- Whether the game's (PO)MDP structure is the key thing that differentiates it from related work in the group ("Maik's project").
- Whether it's meant to purely elicit goal-free exploration, or also include interaction/uncovering mechanics and a final task (e.g. a "sketch what you learned" style probe), possibly per Gruber's task design.
- Whether/how it contributes to the "benchmark" goal specifically, as a simple, controlled condition alongside the VR paradigm.

These are open — don't assume they're settled just because a game is being built. If an implementation choice hinges on one of them, flag it back to Laura rather than picking an answer.
