from fastapi import FastAPI
from pydantic import BaseModel
import requests
import psycopg2
import os

app = FastAPI()

class UrlItem(BaseModel):
    long_url: str

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

@app.post("/api/shorten")
def shorten(url_item: UrlItem):
    api_url = "https://cleanuri.com/api/v1/shorten"
    payload = {'url': url_item.long_url}
    try:
        response = requests.post(api_url, data=payload)
        response.raise_for_status()
        short_url = response.json().get('result_url')

        if short_url:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("INSERT INTO links (original_url, short_url) VALUES (%s, %s)",
                        (url_item.long_url, short_url))
            conn.commit()
            cur.close()
            conn.close()

        return {"short_url": short_url}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

@app.get("/api/history")
def history():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT original_url, short_url, created_at FROM links ORDER BY created_at DESC LIMIT 10;")
    links = cur.fetchall()
    cur.close()
    conn.close()
    return [{"original_url": row[0], "short_url": row[1], "created_at": row[2]} for row in links]
