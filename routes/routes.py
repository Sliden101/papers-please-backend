from fastapi import FastAPI
from db import create_db_and_tables, Paper, Author, Subject

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.post("/v1/add_paper")
def add_paper(paper: Paper):


@app.get("/")
def read_root():
    return { "message": "Hello from Nix + FastAPI!"}
