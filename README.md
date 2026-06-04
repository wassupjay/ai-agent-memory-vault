# AI Agent Memory Vault

A filesystem-based memory and coordination system for running multiple AI agents on any machine — local, VPS, or cloud server.

**Full writeup on Medium:** *(link coming soon)*

---

## The problem

Most AI agent frameworks give each agent its own isolated memory file. When you run multiple agents — or the same agent across sessions — they forget everything, repeat work, and have no shared context.

This repo is a complete, working pattern to fix that: one shared vault, structured by how fast facts change, readable by any agent in any language.

---

## What's in here

```
bin/
  board              — kanban CLI: add/move/update/list tasks, all output JSON
  sync-memory        — promotes agent short-term memory to vault on session end
  lock-watchdog.sh   — alerts when an agent lock goes stale (crash detection)

admin-panel/
  main.py            — FastAPI backend (board, graph, crons, log, state APIs)
  parser.py          — vault Markdown parser + wikilinks → D3 graph
  static/index.html  — D3.js knowledge graph + drag-drop kanban UI
  requirements.txt

memory-vault/        — copy this to ~/memory/ (or any path you prefer)
  index.md           — dense agent entry point, keep under 500 chars
  world/             — permanent facts (server map, secrets policy, architecture)
  identity/          — per-agent rules and behavior
  board/             — Obsidian-compatible kanban task files
  crons/             — master cron/job registry
  log/               — append-only event log
  state/             — current reality: agent snapshots + coordination locks

systemd/
  admin-panel.service  — Linux systemd user service template

nginx/
  admin-panel.conf     — nginx reverse proxy + HTTP basic auth template
```

---

## Core idea

All agents share one filesystem. `~/memory/` (or any shared path) is the single source of truth.

**Four layers, separated by how fast they change:**

| Layer | What lives here | Mutation rate |
|-------|----------------|---------------|
| `world/` | Machine facts, architecture, access policy | Rarely |
| `identity/` | Per-agent rules, tools, behavior | Occasionally |
| `state/` | Current tasks, agent snapshots, locks | Frequently |
| `log/` | Append-only event history | Always (never overwrite) |

**Multi-agent coordination** via lock files in `state/shared/locks/` — no Redis, no message queues, just files.

**Works anywhere:**
- Single machine (local dev, home server)
- Remote server (VPS, cloud VM)
- Any agent framework — anything that can run a shell command or read a file

---

## Quick start

```bash
# 1. Clone
git clone https://github.com/wassupjay/ai-agent-memory-vault
cd ai-agent-memory-vault

# 2. Copy vault template to your preferred location
cp -r memory-vault ~/memory
# Edit ~/memory/index.md, world/server_map.md etc. for your setup

# 3. Set up secrets vault
mkdir -p ~/.secrets && chmod 700 ~/.secrets
# Create ~/.secrets/master.env with your keys, then:
chmod 600 ~/.secrets/master.env

# 4. Install board CLI (requires Python 3.9+, no dependencies)
mkdir -p ~/bin
cp bin/board ~/bin/board && chmod +x ~/bin/board
cp bin/sync-memory ~/bin/sync-memory && chmod +x ~/bin/sync-memory
cp bin/lock-watchdog.sh ~/bin/lock-watchdog.sh && chmod +x ~/bin/lock-watchdog.sh
# Make sure ~/bin is in your PATH

# 5. Run admin panel
cd admin-panel
pip install -r requirements.txt
uvicorn main:app --host 127.0.0.1 --port 8910
# Open http://localhost:8910

# 6. (Optional) nginx + SSL for remote access
# Edit nginx/admin-panel.conf with your domain, then:
sudo cp nginx/admin-panel.conf /etc/nginx/sites-available/admin-panel
sudo ln -s /etc/nginx/sites-available/admin-panel /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
sudo certbot --nginx -d admin.yourdomain.com
```

---

## Board CLI

No dependencies. Any agent calls it via shell. All output is JSON.

```bash
board add "Fix rate limiting" --priority high --agent myagent
board move TASK-001 in_progress
board update TASK-001 --log "found root cause: config missing"
board move TASK-001 done
board list
board list blocked
board next       # highest-priority unclaimed task
board show TASK-001
```

Tasks are stored as plain Markdown in `~/memory/board/` — human-readable and Obsidian-compatible.

---

## Memory sync hook

Wire `sync-memory` into your agent's session-end event so short-term memory automatically promotes to the shared vault:

```bash
# Configure these before running:
export AGENT_NAME="myagent"
export AGENT_MEMORY_FILE="$HOME/.myagent/memory.md"
export VAULT_DIR="$HOME/memory"
```

```yaml
# Example: Hermes agent (config.yaml)
hooks:
  on_session_end:
    - command: /path/to/bin/sync-memory

# Example: any agent that supports post-session shell hooks
# Just call: ~/bin/sync-memory
```

Agent learns something → session ends → vault updated → next agent picks it up.

---

## Multi-agent coordination

Before starting a task, drop a lock file:

```bash
echo '{"task": "TASK-003", "started": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"}' \
  > ~/memory/state/shared/locks/myagent.lock

# After done:
rm ~/memory/state/shared/locks/myagent.lock
```

`lock-watchdog.sh` runs every 5 minutes via cron and alerts if any lock is older than 30 minutes (agent likely crashed).

---

## Obsidian

The vault is plain Markdown with `[[wikilinks]]` — open `~/memory/` directly in Obsidian for a visual knowledge graph of everything your agents know.

For a remote machine:
```bash
# Mount over SSHFS, then open in Obsidian
sshfs user@yourserver:~/memory ~/memory-remote
```

---

## Adapting for your agent

1. Copy `memory-vault/identity/_agent_template.md` → `memory-vault/identity/youragent.md`
2. Edit `memory-vault/identity/rules.md` with your shared behavior rules
3. Point your agent at `~/memory/index.md` as its first read
4. Wire `sync-memory` into your agent's session-end hook
5. Set `AGENT_NAME` and `AGENT_MEMORY_FILE` env vars for the sync script

---

## Requirements

- Python 3.9+ (board CLI + sync-memory, zero extra deps)
- Python 3.9+ + pip (admin panel: FastAPI, uvicorn)
- bash (lock-watchdog.sh)
- nginx + certbot (optional, for remote HTTPS access)
- Obsidian (optional, for visual graph)

---

## License

MIT
