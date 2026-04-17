
import os
import time
import uuid
import httpx
from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.responses import PlainTextResponse
from duckduckgo_search import DDGS


GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
API_KEY      = "secret123"

RATE_LIMIT  = 5   # max requests
RATE_WINDOW = 60  # per 60 seconds

VALID_SECTORS = [
    "pharmaceuticals", "technology", "agriculture", "automobile",
    "banking", "finance", "textiles", "energy", "fmcg", "it",
    "real estate", "infrastructure", "healthcare", "retail", "defence"
]


# Rate limiting: { api_key: [timestamp, ...] }
request_log: dict[str, list[float]] = {}

# Session tracking: { session_id: { created_at, api_key, requests: [...] } }
sessions: dict[str, dict] = {}


app = FastAPI(
    title="Trade Opportunities API",
    description=(
        "Market analysis for Indian sectors using Groq + DuckDuckGo.\n\n"
        "## 🔑 Sample API Key\n\n"
        "Use this key in the **X-API-Key** header:\n\n"
        "`secret123`\n\n"
        "## 📋 Valid Sectors\n\n"
        + "\n".join(f"- `{s}`" for s in VALID_SECTORS)
    ),
    version="1.0.0"
)


def get_or_create_session(session_id: str | None, api_key: str) -> tuple[str, dict]:
    """
    If a valid session_id is provided and exists, return it.
    Otherwise create a new session and return its ID.
    """
    if session_id and session_id in sessions:
        return session_id, sessions[session_id]

    # Create new session
    new_id = str(uuid.uuid4())
    sessions[new_id] = {
        "created_at": time.time(),
        "api_key": api_key,
        "requests": []
    }
    return new_id, sessions[new_id]


def log_request_to_session(session: dict, sector: str):
    """Record each request inside the session."""
    session["requests"].append({
        "sector": sector,
        "timestamp": time.time()
    })



def check_auth(api_key: str):
    """Simple static API key check."""
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key.")


def check_rate_limit(client_id: str):
    """Max 5 requests per 60 seconds per API key."""
    now = time.time()
    recent = [t for t in request_log.get(client_id, []) if now - t < RATE_WINDOW]

    if len(recent) >= RATE_LIMIT:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Max {RATE_LIMIT} requests per {RATE_WINDOW}s."
        )

    recent.append(now)
    request_log[client_id] = recent


def validate_sector(sector: str) -> str:
    """Lowercase, strip, and check against whitelist."""
    sector = sector.strip().lower()
    if sector not in VALID_SECTORS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sector '{sector}'. Valid options: {', '.join(VALID_SECTORS)}"
        )
    return sector

def search_sector_news(sector: str) -> str:
    """Search DuckDuckGo for recent India trade news about the sector."""
    query = f"{sector} sector India trade opportunities 2024 2025 market"
    results = []

    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=5):
            results.append(f"- {r['title']}: {r['body']}")

    return "\n".join(results) if results else "No recent news found."


def analyze_with_groq(sector: str, news_data: str) -> str:
    """Send collected news to Groq and get a Markdown market report."""
    url = "https://api.groq.com/openai/v1/chat/completions"

    prompt = f"""
You are a market analyst specializing in Indian trade and commerce.

Sector: {sector.upper()}
Country: India

Recent news and data:
{news_data}

Write a structured market analysis report in Markdown. Include:
1. Sector Overview (India)
2. Current Trade Opportunities
3. Key Market Trends
4. Risks and Challenges
5. Recommendations for Traders/Investors

Keep it concise, factual, and India-focused.
"""

    response = httpx.post(
        url,
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2
        },
        timeout=30
    )

    if response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail=f"Groq API error: {response.status_code} - {response.text}"
        )

    try:
        return response.json()["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        raise HTTPException(status_code=502, detail="Unexpected response format from Groq.")


@app.get(
    "/analyze/{sector}",
    response_class=PlainTextResponse,
    summary="Get trade opportunity analysis for an Indian sector",
    tags=["Analysis"]
)
async def analyze_sector(
    sector: str,
    request: Request,
    x_api_key: str = Header(..., description="Your API key (secret123)"),
    x_session_id: str = Header(None, description="Optional: pass a previous session ID to continue a session")
):
    """
    Returns a Markdown market analysis report for the given Indian sector.

    **Flow:**
    1. Authenticate via X-API-Key header
    2. Check rate limit (5 req / 60s per key)
    3. Validate sector name
    4. Get/create session (X-Session-Id header, optional)
    5. Search DuckDuckGo for recent India market news
    6. Analyze with Groq (Llama-3.3-70b)
    7. Return Markdown report (downloadable as .md file)
    """

    # Step 1: Auth
    check_auth(x_api_key)

    # Step 2: Rate limit
    check_rate_limit(x_api_key)

    # Step 3: Validate sector
    clean_sector = validate_sector(sector)

    # Step 4: Session management
    session_id, session = get_or_create_session(x_session_id, x_api_key)
    log_request_to_session(session, clean_sector)

    # Step 5: Collect data
    try:
        news = search_sector_news(clean_sector)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Search failed: {str(e)}")

    # Step 6: AI analysis
    report = analyze_with_groq(clean_sector, news)

    # Step 7: Return as downloadable .md file
    filename = f"{clean_sector.replace(' ', '_')}_trade_report.md"

    return PlainTextResponse(
        content=report,
        media_type="text/plain",
        headers={
            "X-Session-Id": session_id   # Return session ID so client can reuse it
        }
    )


@app.get("/session/{session_id}", tags=["Session"])
def get_session_info(
    session_id: str,
    x_api_key: str = Header(..., description="Your API key")
):
    """View the request history for a session."""
    check_auth(x_api_key)

    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found.")

    return sessions[session_id]


@app.get("/", tags=["Health"])
def health():
    return {"status": "ok", "message": "Trade Opportunities API is running"}
