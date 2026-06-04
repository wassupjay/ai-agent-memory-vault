# AI Agent Memory Vault

A complete, filesystem-based memory and coordination system for running multiple AI agents on a single VPS.

**Full writeup on Medium:** *(link coming soon)*

---

## What's in here

```
bin/
  board              — kanban CLI (add/move/update/list tasks, JSON output)
  sync-memory        — promotes agent short-term memory to shared vault on session end
  lock-watchdog.sh   — detects stale agent locks, sends Telegram alert

admin-panel/
  main.py            — FastAPI backend (board, graph, crons, log, state APIs)
  parser.py          — vault Markdown parser (tasks, wikilinks → D3 graph)
  static/index.html  — D3.js knowledge graph + kanban drag-drop UI
  requirements.txt

memory-vault/        — template vault structure (copy to ~/memory/ on your server)
  index.md           — dense entry point for agents (<500 chars)
  world/             — permanent facts (VPS map, secrets policy, architecture)
  identity/          — per-agent rules and behavior
  board/             — kanban task files (Obsidian-compatible Markdown)
  crons/             — master cron registry (prevents duplicate jobs)
  log/               — append-only event log (never overwrite)
  state/             — current reality (agent snapshots, coordination locks)

systemd/
  admin-panel.service  — systemd user service for the admin panel

nginx/
  admin-panel.conf     — nginx reverse proxy + HTTP basic auth config
```

---

## Core idea

All agents share one filesystem. `~/memory/` is the single source of truth.

Four layers, each with a distinct mutation rate:

| Layer | What | Changes |
|-------|------|---------|
| `world/` | VPS facts, architecture | Rarely |
| `identity/` | Per-agent rules, behavior | Occasionally |
| `state/` | Current tasks, agent memory | Frequently |
| `log/` | Append-only event history | Always |

Multi-agent coordination via lock files in `state/shared/locks/` — no Redis, no queues.

---

## Quick start

```bash
# 1. Clone
git clone https://github.com/YOUR_USERNAME/ai-agent-memory-vault
cd ai-agent-memory-vault

# 2. Copy vault template
cp -r memory-vault ~/memory

# 3. Set up secrets vault
mkdir -p ~/.secrets && chmod 700 ~/.secrets
# Add your keys to ~/.secrets/master.env, then:
chmod 600 ~/.secrets/master.env

# 4. Install board CLI
cp bin/board ~/bin/board && chmod +x ~/bin/board
cp bin/sync-memory ~/bin/sync-memory && chmod +x ~/bin/sync-memory
cp bin/lock-watchdog.sh ~/bin/lock-watchdog.sh && chmod +x ~/bin/lock-watchdog.sh

# 5. Run admin panel
cd admin-panel
pip install -r requirements.txt
uvicorn main:app --host 127.0.0.1 --port 8910

# 6. Set up nginx + SSL (edit nginx/admin-panel.conf with your domain first)
sudo cp nginx/admin-panel.conf /etc/nginx/sites-available/admin-panel
sudo ln -s /etc/nginx/sites-available/admin-panel /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
sudo certbot --nginx -d admin.yourdomain.com
```

---

## Board CLI

```bash
board add "Fix rate limiting" --priority high --agent myagent
board move TASK-001 in_progress
board update TASK-001 --log "found root cause"
board move TASK-001 done
board list
board next   # highest-priority unclaimed task
```

All output is JSON. Designed to be called by any agent via shell.

---

## Memory sync hook

Wire into your agent's session-end hook:

```yaml
# Example for Hermes (~/.hermes/config.yaml)
hooks:
  on_session_end:
    - command: /home/ubuntu/bin/sync-memory
```

Agent learns something → session ends → vault gets updated automatically.

---

## Obsidian

Mount the vault over SSHFS and open in Obsidian for a visual knowledge graph of everything your agents know:

```bash
sshfs ubuntu@your-vps:~/memory ~/memory-local
# Open ~/memory-local as an Obsidian vault
```

---

## License

MIT
