import os
import re
from pathlib import Path
from datetime import datetime

VAULT = Path.home() / "memory"


def parse_tasks(filepath: Path) -> list[dict]:
    if not filepath.exists():
        return []
    tasks = []
    current = None
    with open(filepath) as f:
        for line in f:
            line = line.rstrip()
            m = re.match(r"^## \[(TASK-\d+)\] (.+)$", line)
            if m:
                if current:
                    tasks.append(current)
                current = {"id": m.group(1), "title": m.group(2), "log": []}
                continue
            if current:
                kv = re.match(r"^(\w+): (.+)$", line)
                if kv:
                    current[kv.group(1)] = kv.group(2)
                elif line.startswith("- "):
                    current["log"].append(line[2:])
    if current:
        tasks.append(current)
    return tasks


def get_board() -> dict:
    board = {"backlog": [], "in_progress": [], "blocked": [], "done": []}
    board["backlog"] = parse_tasks(VAULT / "board" / "backlog.md")
    board["in_progress"] = parse_tasks(VAULT / "board" / "in_progress.md")
    board["blocked"] = parse_tasks(VAULT / "board" / "blocked.md")
    done_dir = VAULT / "board" / "done"
    if done_dir.exists():
        for f in sorted(done_dir.glob("*.md")):
            board["done"].extend(parse_tasks(f))
    return board


def move_task(task_id: str, new_status: str) -> bool:
    status_files = {
        "backlog": VAULT / "board" / "backlog.md",
        "in_progress": VAULT / "board" / "in_progress.md",
        "blocked": VAULT / "board" / "blocked.md",
        "done": VAULT / "board" / "done" / f"{datetime.now().strftime('%Y-%m')}.md",
    }
    task_block = None
    source_file = None
    for status, fpath in status_files.items():
        if not fpath.exists():
            continue
        content = fpath.read_text()
        pattern = rf"(## \[{re.escape(task_id)}\].*?)(?=\n## \[|\Z)"
        m = re.search(pattern, content, re.DOTALL)
        if m:
            task_block = m.group(1).strip()
            source_file = fpath
            new_content = re.sub(pattern, "", content, flags=re.DOTALL).strip()
            fpath.write_text(new_content + "\n")
            break
    if not task_block or not source_file:
        return False
    task_block = re.sub(r"^status: \w+", f"status: {new_status}", task_block, flags=re.MULTILINE)
    dest = status_files[new_status]
    dest.parent.mkdir(parents=True, exist_ok=True)
    with open(dest, "a") as f:
        f.write(f"\n{task_block}\n")
    return True


def get_graph() -> dict:
    nodes = []
    edges = []
    node_ids = {}
    idx = 0
    md_files = list(VAULT.rglob("*.md"))
    for fpath in md_files:
        rel = str(fpath.relative_to(VAULT))
        folder = rel.split("/")[0] if "/" in rel else "root"
        node_ids[fpath.stem] = idx
        nodes.append({"id": idx, "name": fpath.stem, "path": rel, "folder": folder})
        idx += 1
    for fpath in md_files:
        if fpath.stem not in node_ids:
            continue
        src = node_ids[fpath.stem]
        try:
            content = fpath.read_text()
        except Exception:
            continue
        for link in re.findall(r"\[\[([^\]]+)\]\]", content):
            link_name = link.split("/")[-1].split("|")[0].strip()
            if link_name in node_ids:
                edges.append({"source": src, "target": node_ids[link_name]})
    return {"nodes": nodes, "edges": edges}


def get_crons() -> list[dict]:
    registry = VAULT / "crons" / "registry.md"
    if not registry.exists():
        return []
    crons = []
    with open(registry) as f:
        for line in f:
            m = re.match(r"^\| ((?:SYS|HRM|SVC)-\d+) \| (.+?) \| `?(.+?)`? \| (.+?) \| (.+?) \|", line)
            if m:
                crons.append({
                    "id": m.group(1).strip(),
                    "name": m.group(2).strip(),
                    "schedule": m.group(3).strip(),
                    "owner": m.group(4).strip(),
                    "command": m.group(5).strip(),
                })
    return crons


def get_log(lines: int = 100) -> list[str]:
    now = datetime.now()
    logfile = VAULT / "log" / f"{now.strftime('%Y-%m')}.md"
    if not logfile.exists():
        return []
    entries = []
    with open(logfile) as f:
        for line in f:
            line = line.strip()
            if line.startswith("[20") and line:
                entries.append(line)
    return list(reversed(entries[-lines:]))


def get_state() -> dict:
    state = {}
    agents_dir = VAULT / "state" / "agents"
    if agents_dir.exists():
        for f in agents_dir.glob("*.md"):
            state[f.stem] = f.read_text()
    locks_dir = VAULT / "state" / "shared" / "locks"
    locks = []
    if locks_dir.exists():
        for lf in locks_dir.glob("*.lock"):
            locks.append({"agent": lf.stem, "content": lf.read_text(), "age_seconds": int(datetime.now().timestamp() - lf.stat().st_mtime)})
    state["locks"] = locks
    return state
