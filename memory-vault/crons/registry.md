# Cron Registry

> Master list of ALL scheduled jobs. Check here before adding any cron or heartbeat.
> Prevents duplicate jobs when multiple agents can each add crons independently.

## Format
| ID | Name | Schedule | Owner | Command |
|----|------|----------|-------|---------|
| SYS-001 | example-job | `*/5 * * * *` | system | /path/to/script.sh |

## Adding a New Job
1. Check this file for duplicates
2. Add entry with next available ID (SYS-NNN for system, AGT-NNN for agent-owned)
3. Add the actual crontab entry
4. Log it: `[timestamp][agent] added cron SYS-NNN: description`
