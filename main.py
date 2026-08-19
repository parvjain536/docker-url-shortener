import os
import string
import random
import psycopg2
import redis
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl

app = FastAPI(title="URL Shortener Microservice")

# Configurations from Environment
DB_HOST = os.getenv("DB_HOST", "postgres-db")
DB_NAME = os.getenv("POSTGRES_DB", "shortener_db")
DB_USER = os.getenv("POSTGRES_USER", "postgres_user")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "postgres_pass")
REDIS_HOST = os.getenv("REDIS_HOST", "redis-cache")

# Database Connection Helper
def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

# Cache Connection
cache = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)

# Startup Table Initialization
@app.on_event("startup")
def setup_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS urls (
            id SERIAL PRIMARY KEY,
            short_code VARCHAR(10) UNIQUE NOT NULL,
            original_url TEXT NOT NULL
        );
    """)
    conn.commit()
    cursor.close()
    conn.close()

class ShortenRequest(BaseModel):
    url: HttpUrl

def generate_short_code(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/shorten")
def shorten_url(payload: ShortenRequest):
    short_code = generate_short_code()
    original_url = str(payload.url)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO urls (short_code, original_url) VALUES (%s, %s);",
        (short_code, original_url)
    )
    conn.commit()
    cursor.close()
    conn.close()
    
    cache.set(f"url:{short_code}", original_url)
    cache.set(f"hits:{short_code}", 0)
    
    return {"short_code": short_code, "short_url": f"http://localhost/{short_code}"}

@app.get("/{short_code}")
def redirect_to_url(short_code: str):
    # Check cache first
    target_url = cache.get(f"url:{short_code}")
    
    if not target_url:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT original_url FROM urls WHERE short_code = %s;", (short_code,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not row:
            raise HTTPException(status_code=404, detail="Short URL not found")
        target_url = row[0]
        cache.set(f"url:{short_code}", target_url)
    
    cache.incr(f"hits:{short_code}")
    return RedirectResponse(url=target_url, status_code=307)

@app.get("/stats/{short_code}")
def get_stats(short_code: str):
    hits = cache.get(f"hits:{short_code}")
    if hits is None:
        raise HTTPException(status_code=404, detail="Code not found or inactive")
    return {"short_code": short_code, "total_clicks": int(hits)}