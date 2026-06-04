# Agent Architecture

> How agents are wired together on this machine. Update when the stack changes.

## Stack Diagram

```
User (any interface: Telegram, CLI, API, web)
        ↓
  [Your Agent]  ←── reads/writes ──→  ~/memory/ vault
        ↓                                     ↓
  Shell + Tools                      admin panel (optional)
```

## Agents
| Agent | Model | Interface | Status |
|-------|-------|-----------|--------|
| your-agent | model-name | Telegram / CLI / API | active |

## Memory Flow
1. Agent reads `~/memory/index.md` on startup
2. Follows pointers to relevant layer (world / identity / state)
3. Acts, writes results to `state/` or appends to `log/`
4. On session end → sync-memory promotes changes to vault
5. Next agent reads updated vault

## Key Design Decisions
- Filesystem = shared API (no external memory service required)
- 4 layers by mutation rate: world / identity / state / log
- Lock files for multi-agent task coordination (no Redis needed)
- Append-only log — never overwrite
- Plain Markdown + wikilinks = Obsidian-compatible out of the box
