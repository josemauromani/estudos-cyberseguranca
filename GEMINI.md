# AGENTS.md / GEMINI.md

This file provides guidance to AI agents (Antigravity, Claude Code, Codex, etc.) when working with code in this repository.

## Spec-Driven Development (Superpowers SDD)

This repository enforces **Spec-Driven Development (SDD)**, identical to the workflow used in Claude Code via the `superpowers` plugin and in Antigravity via workspace skills.

### Protocol & Skill Activation
Always check and activate process skills before taking action:
- **`using-superpowers`**: Establishes skill discipline. Check and invoke skills before responding or editing files.
- **`brainstorming`**: MUST be invoked before any creative work, new features, or architectural modifications.
  - **Spike**: Feasibility inquiry. Quick probe, throwaway output.
  - **Bounded**: Scoped change to existing code. In-chat design; get user approval before writing code.
  - **Architectural**: New subsystems, features, or interface changes. Full cycle:
    1. Interactive discovery & intent gathering.
    2. Propose 2-3 approaches with trade-offs.
    3. Present design sections in chat for feedback.
    4. Write design spec to `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`.
    5. Self-review spec & commit to git.
    6. **Hard Gate**: User must review and approve spec before moving to planning.
- **`writing-plans`**: MUST be invoked after spec approval.
  - Break design into bite-sized, test-driven, unambiguously specified tasks with checkable results.
  - Write implementation plan to `docs/superpowers/plans/YYYY-MM-DD-<topic>.md`.
  - Self-review plan & commit to git.
  - **Hard Gate**: User must review and approve implementation plan before execution.
- **`subagent-driven-development` (SDD)**: Default plan execution mode.
  - Resolve plan workspace in `.superpowers/sdd/<plan-slug>/` using:
    `bash .agents/skills/subagent-driven-development/scripts/sdd-workspace <plan>`
  - Extract task briefs using:
    `bash .agents/skills/subagent-driven-development/scripts/task-brief <plan> <task-number>`
  - Dispatch a fresh implementer subagent per task using `invoke_subagent` (`TypeName: "self"`).
  - Implementer follows TDD, verifies, commits, and self-reviews.
  - Generate review package using:
    `bash .agents/skills/subagent-driven-development/scripts/review-package <plan> <base-commit> <head-commit>`
  - Dispatch a task reviewer subagent using `invoke_subagent` (`TypeName: "self"`) checking spec compliance and code quality.
  - Fix any findings (up to 5 rounds) and dispatch re-reviews.
  - Record progress and rulings in `.superpowers/sdd/<plan-slug>/progress.md`.
  - **Continuous execution**: Do NOT pause to ask "should I continue" between tasks. Decide plan ambiguities, ledger rulings (`Ruling: <decision> — <why> — <cost>`), and keep executing until complete or hard-gated.
  - At the end, dispatch whole-branch review and clean up workspace.
- **`executing-plans`**: Alternative inline execution when subagents are not used.
- **`systematic-debugging`**: MUST be invoked for bug fixes (reproduce -> root cause -> fix -> regression test).
- **`test-driven-development`**: Follow Red -> Green -> Refactor for implementation tasks.
- **`verification-before-completion`**: Always verify with actual test runs and build outputs before declaring work complete.
- **`requesting-code-review` / `receiving-code-review`**: Use standard review checklists.

### Antigravity Tool Mapping
- **Subagents**: Use `invoke_subagent` with `TypeName: "self"` for full write/bash capabilities, or `TypeName: "research"` for read-only exploration.
- **Task Tracking**: Use task markdown artifacts via `write_to_file` (`UserFacing: true`) with checklists (`- [ ]` / `- [x]`) and update with `replace_file_content`. *Note: `manage_task` is for background OS processes, NOT for checklists.*
- **Questions**: Use `ask_question` for interactive multiple-choice clarification during brainstorming and decision-making.
- **Short-lived Artifacts**: Stored in `.superpowers/sdd/<plan-slug>/` (ignored by git).

---

## Project Overview

Estudos em Cibersegurança: Material autoinstrucional e prático sobre segurança cibernética, inspirado na estrutura modular de estudos técnicos do autor (com treinamentos interativos em HTML, geradores automatizados em Python e planilhas práticas).

Textos da interface, materiais de estudo e explicações são em Português do Brasil (**pt-BR**).
