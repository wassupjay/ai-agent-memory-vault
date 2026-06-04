# Agent Architecture

> How agents are wired together on this VPS.

## Stack Diagram

```
User (Telegram / CLI)
        ↓
  [Your Agent]  ←── reads/writes ──→  ~/memory/ vault
        ↓                                     ↓
  Shell + Tools                      admin.yourdomain.com
```

## Agent Types
| Agent | Model | Interface | Purpose |
|-------|-------|-----------|---------|
| your-agent | claude-opus-4-8 | Telegram | Primary assistant |
| add more agents here | | | |

## Memory Flow
1. Agent reads `~/memory/index.md` on startup
2. Follows pointers to relevant layer (world/identity/state)
3. Acts, writes results to `state/` or `log/`
4. On session end → sync-memory hook promotes changes to vault

## Key Design Decisions
- Filesystem = shared API (no external memory service)
- 4 layers by mutation rate: world / identity / state / log
- Lock files for multi-agent coordination (no Redis needed)
- Append-only log — never overwrite
