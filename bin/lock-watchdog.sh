#!/bin/bash
# Checks ~/memory/state/shared/locks/ for stale locks (>30min)
# Alerts via Telegram if found. Run via cron every 5 minutes:
#   */5 * * * * /path/to/lock-watchdog.sh
#
# Required env vars (load from ~/.secrets/master.env or set in crontab):
#   TELEGRAM_BOT_TOKEN  — your bot token
#   TELEGRAM_CHAT_ID    — your chat ID

LOCKS_DIR="$HOME/memory/state/shared/locks"
STALE_THRESHOLD=1800  # 30 minutes in seconds

BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-$(grep TELEGRAM_BOT_TOKEN ~/.secrets/master.env 2>/dev/null | cut -d= -f2)}"
CHAT_ID="${TELEGRAM_CHAT_ID}"

[ ! -d "$LOCKS_DIR" ] && exit 0
[ -z "$BOT_TOKEN" ] && echo "TELEGRAM_BOT_TOKEN not set" && exit 1
[ -z "$CHAT_ID" ] && echo "TELEGRAM_CHAT_ID not set" && exit 1

NOW=$(date +%s)

for lockfile in "$LOCKS_DIR"/*.lock 2>/dev/null; do
    [ -f "$lockfile" ] || continue
    MTIME=$(stat -c %Y "$lockfile")
    AGE=$((NOW - MTIME))
    if [ "$AGE" -gt "$STALE_THRESHOLD" ]; then
        AGENT=$(basename "$lockfile" .lock)
        CONTENT=$(cat "$lockfile" 2>/dev/null)
        MSG="Stale lock detected: agent=$AGENT age=${AGE}s content=$CONTENT"
        curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
            -d chat_id="$CHAT_ID" \
            -d text="$MSG" > /dev/null
    fi
done

exit 0
