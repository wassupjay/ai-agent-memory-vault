# Agent Rules (All Agents)

> Shared behavioral rules. Every agent reads this. Customize for your stack.

## Autonomy
- User may not be able to run commands. Agent has shell access.
- Failed command → diagnose → retry with fix
- Verify success after every fix
- Only give up after 3+ attempts. Report what was tried + exact blocker.

## Secrets
- Never hardcode keys in source files
- Keys live in ~/.secrets/master.env
- See [[secrets]] for full access policy

## Memory
- Vault entry point: ~/memory/index.md
- Read world/ files for machine facts
- Append to log/YYYY-MM.md after significant actions: `[timestamp][agent] what happened`
- Before creating cron/heartbeat: check ~/memory/crons/registry.md for duplicates

## Task Claiming (multi-agent)
- Before starting task: create ~/memory/state/shared/locks/<agentname>.lock
- Lock content: {"task": "TASK-NNN", "started": "ISO timestamp"}
- After done: delete lock, update board
- Stale lock (>30min): safe to assume agent crashed

## Task Board
- Before starting non-trivial task: `board move TASK-NNN in_progress`
- After finishing: `board move TASK-NNN done`
- When blocked: `board move TASK-NNN blocked` + `board update TASK-NNN --log "blocked by: X"`
- CLI: `~/bin/board` — works for all agents

## New Projects
- Keep all new projects under a consistent root (e.g. ~/projects/)
