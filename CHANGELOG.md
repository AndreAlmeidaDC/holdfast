# Changelog

All notable changes to this skill are documented here. This file is the preferred
human-readable source for update checks.

| Date | Time | Version | Changes |
|---|---|---|---|
| 2026-08-21 | 12:00 GMT-3 | 1.1.0 | Standardized the repository to match this author's other skills: added `metadata.json` with real declared capabilities (subprocess true, network egress false, dependency install false, each justified), the shared origin version-check protocol (`references/version-check.md` + a version-check section in `SKILL.md`), `GOVERNANCE.md`, `CONTRIBUTING.md`, and `scripts/validate_skill.py` for local structural validation. `README.md`, `GOVERNANCE.md` and `CONTRIBUTING.md` are now bilingual (English + PT-BR). No change to the skill's behavior, workflow or scripts. |
| 2026-08-21 | — | 1.0.0 | Initial release: the six practices, `holdfast-init.sh` / `holdfast-status.sh` / `holdfast-collect.py`, protocol/handoff/dispatch/resume templates, and the runtime adaptation guide covering push runtimes (Claude Code, Codex, Antigravity), Cursor, and pull runtimes (OpenClaw, Hermes, Gemini-CLI, Kimi CLI, Grok CLI, pi). |
