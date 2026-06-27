from fastapi import FastAPI
from bigquery import sim_query

app = FastAPI()


@app.get("/")
def read_root():
    sim_query()
    return {"status": "ok"}