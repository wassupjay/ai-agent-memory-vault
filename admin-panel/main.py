from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import parser as vault_parser

app = FastAPI(title="Admin Panel")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def index():
    return FileResponse("static/index.html")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/board")
def get_board():
    return vault_parser.get_board()


@app.get("/api/board/{status}")
def get_board_by_status(status: str):
    board = vault_parser.get_board()
    if status not in board:
        raise HTTPException(status_code=404, detail="Unknown status")
    return board[status]


class MoveTask(BaseModel):
    status: str


@app.patch("/api/board/{task_id}")
def move_task(task_id: str, body: MoveTask):
    valid = {"backlog", "in_progress", "blocked", "done"}
    if body.status not in valid:
        raise HTTPException(status_code=400, detail=f"status must be one of {valid}")
    ok = vault_parser.move_task(task_id, body.status)
    if not ok:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return {"ok": True}


@app.get("/api/graph")
def get_graph():
    return vault_parser.get_graph()


@app.get("/api/crons")
def get_crons():
    return vault_parser.get_crons()


@app.get("/api/log")
def get_log(lines: int = 100):
    return vault_parser.get_log(lines)


@app.get("/api/state")
def get_state():
    return vault_parser.get_state()
