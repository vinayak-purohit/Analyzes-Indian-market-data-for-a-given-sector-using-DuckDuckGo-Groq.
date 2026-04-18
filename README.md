🇮🇳 Trade Opportunities API
A FastAPI service that analyzes Indian market data for any sector and returns a structured trade opportunity report powered by AI.

🔗 Live Demo
Base URL: https://analyzes-indian-market-data-for-a-given.onrender.com
API Docs (Swagger UI): https://analyzes-indian-market-data-for-a-given.onrender.com/docs

 Hosted on Render free tier — first request may take ~30 seconds to wake up.


Features

 GET /analyze/{sector} — Main endpoint, returns a Markdown trade report
 AI Analysis — Groq (Llama-3.3-70b) generates structured market insights
 Web Search — DuckDuckGo fetches real-time Indian market news
 Authentication — Static API key via request header
 Rate Limiting — Max 5 requests per 60 seconds per API key
 Session Management — UUID-based in-memory session tracking
 Input Validation — Sector name validated against a whitelist
 Downloadable Report — Response returns as a .md file


 Quick Start
1. Clone the repo
bashgit clone https://github.com/vinayak-purohit/Analyzes-Indian-market-data-for-a-given-sector-using-DuckDuckGo-Groq.git
cd Analyzes-Indian-market-data-for-a-given-sector-using-DuckDuckGo-Groq
2. Install dependencies
bashpip install -r requirements.txt
3. Add your API keys
Open main.py and update:
pythonGROQ_API_KEY = "your_groq_api_key"   # https://console.groq.com/keys
API_KEY      = "secret123"            # Your chosen auth key
4. Run the server
bashuvicorn main:app --reload
5. Open API docs
http://localhost:8000/docs

 Authentication
Pass your API key in every request header:
x-api-key: secret123

📡 API Endpoints
GET /analyze/{sector}
Returns a structured Markdown market analysis report for the given Indian sector.
Example Request:
bashcurl -X GET "https://analyzes-indian-market-data-for-a-given.onrender.com/analyze/pharmaceuticals" \
     -H "x-api-key: secret123"
     
Example Response: A downloadable .md file containing:


Pharmaceuticals Sector — India Trade Opportunities Report

## 1. Sector Overview
...
## 2. Current Trade Opportunities
...
## 3. Key Market Trends
...
## 4. Risks and Challenges
...
## 5. Recommendations for Traders/Investors
...

GET /session/{session_id}
View request history for a session.
bashcurl -X GET "https://.../session/{your-session-id}" \
     -H "x-api-key: secret123"

GET /
Health check.
json{"status": "ok", "message": "Trade Opportunities API is running"}

📦 Valid Sectors
SectorSectorSectorpharmaceuticalstechnologyagricultureautomobilebankingfinancetextilesenergyfmcgitreal estateinfrastructurehealthcareretaildefence

🏗️ Project Structure
├── main.py            # Full FastAPI application
├── requirements.txt   # Dependencies
└── README.md          # This file

⚙️ How It Works
Request
  │
  ├── 1. Auth check (x-api-key header)
  ├── 2. Rate limit check (5 req / 60s per key)
  ├── 3. Input validation (sector whitelist)
  ├── 4. Session management (UUID-based, in-memory)
  ├── 5. DuckDuckGo search (5 recent India market news results)
  ├── 6. Groq AI analysis (Llama-3.3-70b generates markdown report)
  └── 7. Return .md file response

🛠️ Tech Stack

FastAPI — Web framework
Groq + Llama-3.3-70b — AI analysis
DuckDuckGo Search — Real-time news collection
httpx — Async HTTP client
Uvicorn — ASGI server
Render — Free cloud hosting


📄 Dependencies
fastapi
uvicorn
httpx
duckduckgo-search

👤 Author
Vinayak Purohit
B.Tech CSE (Data Science & ML) | LPU
LinkedIn · GitHub
