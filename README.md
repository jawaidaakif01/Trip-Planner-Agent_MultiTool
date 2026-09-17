# ✈️ Trip Planner Agent

An AI-powered multi-tool travel assistant built with **LangChain**, **Gemini**, and **Streamlit** (using **LangGraph** solely for conversation memory checkpointing). Plan complete trips in a single conversation — the agent autonomously searches real-time flights, hotels, weather forecasts, historical climate data, currency rates, and the web to build you a personalized itinerary.

---

## 🖥️ UI Preview

**LangSmith Tracing — Agent reasoning and tool call waterfall:**

![LangSmith Tracing](Images/Screenshot%202026-09-17%20193106.png)

**Streamlit Chat UI — Generative flight cards with real-time data:**

![Flight Cards UI](Images/Screenshot%202026-09-17%20202736.png)

**Streamlit Chat UI — Full trip plan with budget breakdown:**

![Trip Plan UI](Images/Screenshot%202026-09-17%20203036.png)

---

## 🧠 How It Works

The agent is built using **LangChain** (`create_agent`) with **Gemini 3.5 Flash Lite** as the LLM and is equipped with 6 specialized tools. It uses LangGraph's `InMemorySaver` checkpointer specifically for managing conversational memory across turns. When you describe your trip, the agent decides which tools to call, in what order, and synthesizes the results into a complete plan.

```
User Input
    │
    ▼
┌─────────────────────────────────────────┐
│            LangChain Agent              │
│  (Gemini 3.5 Flash Lite + ReAct loop)   │
│   Memory: LangGraph InMemorySaver       │
└─────────────────────────────────────────┘
    │
    ├── ✈️  flight_search        → SerpAPI (Google Flights)
    ├── 🏨  hotel_search         → StayAPI (Booking.com)
    ├── 🌤️  get_weather_forecast → Open-Meteo (16-day forecast)
    ├── 📊  get_historical_weather → Open-Meteo Archive API
    ├── 💱  currency_conversion  → ExchangeRate API
    └── 🔍  web_search           → Tavily Search
```

---

## 🛠️ Tools

| Tool | API | What it does |
|------|-----|-------------|
| `flight_search` | SerpAPI (Google Flights) | Searches round-trip flights with airline, timing, stops, price, and carbon emissions |
| `hotel_search` | StayAPI (Booking.com) | Finds available hotels with ratings, prices, cancellation policy, and booking link |
| `get_weather_forecast` | Open-Meteo | Returns up to 16-day daily forecast — temp, rain probability, sunshine, wind |
| `get_historical_weather` | Open-Meteo Archive | Averages past 5 years of weather for a date range to predict seasonal conditions |
| `currency_conversion` | ExchangeRate API | Converts any currency with live exchange rates |
| `web_search` | Tavily | Searches the web for real-time travel tips, visa info, local guides |

---

## 🎨 Generative UI

The Streamlit UI renders **rich inline cards** for each tool result instead of plain text — powered by `streamlit.components.v1.html()`:

- **✈️ Flight cards** — Airline, route, time, stops, duration, price badge, price level indicator
- **🏨 Hotel cards** — Star rating, guest score, price/night, free cancellation badge, Booking.com link  
- **🌤️ Weather strips** — Scrollable daily forecast with weather icons, max/min temp, rain %
- **📊 Historical summary** — Avg temp, rainfall, sunshine hours, wind speed stat grid
- **💱 Currency chip** — From → To with converted amount and live rate
- **🔍 Web source cards** — Title, domain, snippet, clickable link

---

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager

### 1. Clone the repository

```bash
git clone https://github.com/jawaidaakif01/Trip-Planner-Agent_MultiTool.git
cd Trip-Planner-Agent_MultiTool
```

### 2. Install dependencies

```bash
uv sync
```

### 3. Configure API keys

Copy `.env.example` to `.env` and fill in your keys:

```bash
cp .env.example .env
```

```env
GOOGLE_API_KEY=your_google_gemini_api_key
SERPAPI_API_KEY=your_serpapi_key
STAYAPI_KEY=your_stayapi_key
EXCHANGERATE_API_KEY=your_exchangerate_api_key
TAVILY_API_KEY=your_tavily_api_key
LANGSMITH_API_KEY=your_langsmith_key   # optional, for tracing
```

| Key | Get it from |
|-----|------------|
| `GOOGLE_API_KEY` | [Google AI Studio](https://aistudio.google.com/app/apikey) |
| `SERPAPI_API_KEY` | [SerpAPI](https://serpapi.com/) |
| `STAYAPI_KEY` | [StayAPI](https://stayapi.com/) |
| `EXCHANGERATE_API_KEY` | [ExchangeRate API](https://www.exchangerate-api.com/) |
| `TAVILY_API_KEY` | [Tavily](https://tavily.com/) |

### 4. Run

**Streamlit UI (recommended):**
```bash
streamlit run app.py
```
Open [http://localhost:8501](http://localhost:8501)

**CLI mode:**
```bash
python main.py
```

---

## 📁 Project Structure

```
Trip-Planner-Agent_MultiTool/
│
├── agent.py                  # LangChain agent setup (LLM, tools, prompt, LangGraph memory)
├── app.py                    # Streamlit chat UI with generative UI cards
├── main.py                   # CLI entrypoint
│
├── tools/
│   ├── flights.py            # flight_search tool (SerpAPI)
│   ├── hotels.py             # hotel_search tool (StayAPI)
│   ├── weather.py            # get_weather_forecast tool (Open-Meteo)
│   ├── historical_weather.py # get_historical_weather tool (Open-Meteo Archive)
│   ├── currency_conversion.py# currency_conversion tool (ExchangeRate API)
│   ├── currency_codes.py     # ISO 4217 currency code mapper
│   ├── web_search.py         # web_search tool (Tavily)
│   └── location_extractor.py # Nominatim geocoder (lat/lon from city name)
│
├── ui/
│   └── cards.py              # Generative UI card HTML renderers
│
├── Images/                   # UI and tracing screenshots
├── .env.example              # Environment variable template
├── pyproject.toml            # Project dependencies (uv)
└── requirements.txt          # pip-compatible dependency list
```

---

## 💬 Example Conversations

> **"Plan a 7-day trip to Tokyo from Delhi in December"**
> → Searches flights, hotels, fetches historical weather for December, converts JPY to INR

> **"Find flights from Mumbai to Dubai next month for 2 adults"**
> → Calls `flight_search` with correct IATA codes (BOM→DXB), renders flight cards

> **"What's the weather like in Paris in July?"**
> → Uses `get_historical_weather` to return avg temps, rainfall, sunshine over past 5 years

> **"Convert 50,000 INR to USD"**
> → Calls `currency_conversion`, renders a currency chip with the live rate

---

## 🔭 Tracing

The agent integrates with **LangSmith** for full observability — every tool call, model invocation, token count, and latency is traced. Set `LANGSMITH_API_KEY` in your `.env` to enable it.
