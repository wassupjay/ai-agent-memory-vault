# Server Map

> Permanent facts about this machine. Update deliberately, not frequently.
> Works for: local machine, VPS, cloud VM, home server — any shared filesystem.

## Machine
- Host: YOUR_HOSTNAME_OR_IP
- OS: Ubuntu / macOS / etc.
- User: YOUR_USERNAME
- Location: local | vps | cloud

## Services
| Name | Port | Type | Status |
|------|------|------|--------|
| admin-panel | 8910 | FastAPI | active |
| your-service | PORT | type | status |

## Public Endpoints
| URL / Subdomain | Points To | Purpose |
|-----------------|-----------|---------|
| admin.yourdomain.com | :8910 via nginx | Admin panel |

## Key Paths
- Projects: ~/projects/
- Memory vault: ~/memory/
- Secrets: ~/.secrets/
- Agent configs: ~/.youragent/

## Notes
- Add permanent facts about this machine here
- Check disk usage: `du -sh ~/* | sort -rh`
