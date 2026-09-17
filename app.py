"""
app.py — Streamlit chat UI for the Trip Planner Agent.

Run with:  streamlit run app.py
"""
from __future__ import annotations

import json
import uuid

import streamlit as st
import streamlit.components.v1 as components
from langchain_core.messages import ToolMessage

# ── Page config (must be first Streamlit call) ──────────────────────────────
st.set_page_config(
    page_title="Trip Planner Agent",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ── Load agent once (cached across reruns) ──────────────────────────────────
@st.cache_resource(show_spinner="Loading agent…")
def load_agent():
    from agent import agent
    return agent


# ── CSS — dark theme + chat bubble overrides ────────────────────────────────
DARK_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

/* ── Background with subtle grid ── */
[data-testid="stAppViewContainer"] {
    background-color: #080812;
    background-image:
        linear-gradient(rgba(99,102,241,0.035) 1px, transparent 1px),
        linear-gradient(90deg, rgba(99,102,241,0.035) 1px, transparent 1px);
    background-size: 32px 32px;
}

/* ── Hide Streamlit chrome ── */
[data-testid="stHeader"]  { display: none !important; }
[data-testid="stToolbar"] { display: none !important; }
footer                    { display: none !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0b0b1a !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label { color: #9090b8 !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #d0d0f0 !important; }
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.07) !important; }

/* Sidebar buttons */
[data-testid="stSidebar"] .stButton > button {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    color: #a0a0c8 !important;
    border-radius: 10px !important;
    font-size: 12px !important;
    text-align: left !important;
    transition: all 0.2s ease !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(99,102,241,0.15) !important;
    border-color: rgba(99,102,241,0.3) !important;
    color: #c0c8ff !important;
}

/* ── Main content area ── */
.main .block-container {
    max-width: 860px;
    padding-top: 1.5rem;
    padding-bottom: 0.5rem;
}

/* ── Chat messages ── */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    padding: 4px 0 !important;
}

/* User bubble */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    flex-direction: row-reverse !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stMarkdownContainer"] p {
    background: linear-gradient(135deg, #5254cc 0%, #7c3aed 100%) !important;
    border-radius: 18px 18px 4px 18px !important;
    padding: 10px 16px !important;
    color: #fff !important;
    display: inline-block !important;
    max-width: 80% !important;
    box-shadow: 0 4px 20px rgba(99,102,241,0.25) !important;
}

/* Assistant bubble */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) [data-testid="stMarkdownContainer"] p {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 18px 18px 18px 4px !important;
    padding: 10px 16px !important;
    color: #d0d0e8 !important;
    display: inline-block !important;
    max-width: 90% !important;
    backdrop-filter: blur(10px) !important;
}

/* Avatar colours */
[data-testid="chatAvatarIcon-user"]      { background: linear-gradient(135deg,#6366f1,#7c3aed) !important; }
[data-testid="chatAvatarIcon-assistant"] { background: linear-gradient(135deg,#0ea5e9,#6366f1) !important; }

/* ── Bottom input bar ── */
[data-testid="stBottom"] {
    background: rgba(8,8,18,0.95) !important;
    border-top: 1px solid rgba(255,255,255,0.06) !important;
    backdrop-filter: blur(16px) !important;
}
[data-testid="stChatInput"] textarea {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 24px !important;
    color: #e5e5f0 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: rgba(255,255,255,0.25) !important;
}
[data-testid="stChatInput"] textarea:focus {
    border-color: rgba(99,102,241,0.5) !important;
    box-shadow: 0 0 0 2px rgba(99,102,241,0.15) !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar             { width: 4px; height: 4px; }
::-webkit-scrollbar-track       { background: transparent; }
::-webkit-scrollbar-thumb       { background: rgba(255,255,255,0.1); border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.2); }

/* ── Tool status chip ── */
.tool-chip {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    background: rgba(99,102,241,0.1);
    border: 1px solid rgba(99,102,241,0.22);
    border-radius: 20px;
    padding: 5px 14px;
    font-size: 12px;
    color: #a5b4fc;
    margin: 4px 0;
    animation: chip-pulse 1.6s ease-in-out infinite;
}
@keyframes chip-pulse {
    0%,100% { opacity:1; }
    50%      { opacity:0.45; }
}

/* ── Welcome card ── */
.welcome-card {
    background: rgba(99,102,241,0.06);
    border: 1px solid rgba(99,102,241,0.15);
    border-radius: 16px;
    padding: 24px 28px;
    margin-bottom: 20px;
    font-family: 'Inter', sans-serif;
}

/* Streamlit divider */
hr { border-color: rgba(255,255,255,0.07) !important; }
</style>
"""

# ── Tool metadata ────────────────────────────────────────────────────────────
TOOL_META: dict[str, tuple[str, str]] = {
    "flight_search":          ("✈️", "Searching flights…"),
    "hotel_search":           ("🏨", "Finding hotels…"),
    "get_weather_forecast":   ("🌤️", "Fetching weather forecast…"),
    "get_historical_weather": ("📊", "Retrieving historical weather…"),
    "currency_conversion":    ("💱", "Converting currency…"),
    "web_search":             ("🔍", "Searching the web…"),
}

# ── Card dispatcher ──────────────────────────────────────────────────────────

# Estimated iframe heights per card type (px)
_CARD_HEIGHTS: dict[str, int] = {
    "flight_search":          420,
    "hotel_search":           620,
    "get_weather_forecast":   240,
    "get_historical_weather": 220,
    "currency_conversion":    140,
    "web_search":             450,
}

_CARD_WRAPPER = (
    "<!DOCTYPE html><html><head>"
    "<link href='https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap' rel='stylesheet'>"
    "<style>html,body{{margin:0;padding:0;background:transparent;font-family:Inter,sans-serif;}}*{{box-sizing:border-box;}}</style>"
    "</head><body>{card}</body></html>"
)


def _show_card(tool_name: str, card_html: str) -> None:
    """Render a card HTML string using components.html to avoid markdown parser issues."""
    height = _CARD_HEIGHTS.get(tool_name, 350)
    full = _CARD_WRAPPER.format(card=card_html)
    components.html(full, height=height, scrolling=False)


def render_card(tool_name: str, content: str, args: dict) -> str | None:
    """Parse tool output and return HTML card string, or None."""
    from ui.cards import (
        flight_card, hotel_card, weather_card,
        historical_weather_card, currency_card, web_search_card,
    )

    # currency_conversion returns a plain float string
    if tool_name == "currency_conversion":
        try:
            result = float(content)
            return currency_card({
                "amount":          args.get("amount", "?"),
                "base_currency":   args.get("base_currency", "?"),
                "target_currency": args.get("target_currency", "?"),
                "result":          result,
            })
        except (ValueError, TypeError):
            return None

    # All other tools return JSON dicts
    try:
        data = json.loads(content) if isinstance(content, str) else content
    except (json.JSONDecodeError, TypeError):
        return None

    card_map = {
        "flight_search":          flight_card,
        "hotel_search":           hotel_card,
        "get_weather_forecast":   weather_card,
        "get_historical_weather": historical_weather_card,
        "web_search":             web_search_card,
    }
    fn = card_map.get(tool_name)
    if fn is None:
        return None
    try:
        return fn(data)
    except Exception:
        return None


# ── Agent streaming ──────────────────────────────────────────────────────────
def stream_response(user_input: str, thread_id: str):
    """
    Yields events as (type, payload):
      ("tool_start",  {"name": str, "args": dict})
      ("tool_result", {"name": str, "content": str, "args": dict})
      ("text",        str chunk)
    """
    agent = load_agent()
    config = {"configurable": {"thread_id": thread_id}}

    pending_args: dict[str, dict] = {}  # tool_call_id → args

    for chunk, metadata in agent.stream(
        {"messages": [{"role": "user", "content": user_input}]},
        config=config,
        stream_mode="messages",
    ):
        node = metadata.get("langgraph_node", "")

        # ── Tool call being prepared by the AI ──
        if hasattr(chunk, "tool_calls") and chunk.tool_calls:
            for tc in chunk.tool_calls:
                call_id = tc.get("id", "")
                name    = tc.get("name", "")
                args    = tc.get("args") or {}
                if call_id and name:
                    pending_args[call_id] = args
                    yield ("tool_start", {"name": name, "args": args})

        # ── Tool result ──
        elif isinstance(chunk, ToolMessage):
            args = pending_args.pop(chunk.tool_call_id, {})
            yield ("tool_result", {
                "name":    chunk.name or "",
                "content": chunk.content or "",
                "args":    args,
            })

        # ── AI text chunk ── (exclude ToolMessages and pure tool-call chunks)
        elif (
            hasattr(chunk, "content") and chunk.content
            and not isinstance(chunk, ToolMessage)
            and not (hasattr(chunk, "tool_calls") and chunk.tool_calls)
        ):
            text = chunk.content
            if isinstance(text, list):
                text = " ".join(
                    b.get("text", "") for b in text
                    if isinstance(b, dict) and b.get("type") == "text"
                )
            if text:
                yield ("text", text)


# ── Sidebar ──────────────────────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown("## ✈️ Trip Planner")
        st.caption("Your AI-powered travel companion")
        st.divider()

        st.markdown("**🛠️ Capabilities**")
        for icon, name, desc in [
            ("✈️", "Flights",           "Google Flights via SerpAPI"),
            ("🏨", "Hotels",            "Booking.com via StayAPI"),
            ("🌤️", "Weather Forecast", "Up to 16 days ahead"),
            ("📊", "Historical Weather","Seasonal climate data"),
            ("💱", "Currency",          "Live exchange rates"),
            ("🔍", "Web Search",        "Real-time Tavily results"),
        ]:
            st.markdown(
                f"<div style='font-size:13px;padding:3px 0;color:#9090b8;'>"
                f"{icon} <b style='color:#c0c0e0;'>{name}</b> — {desc}</div>",
                unsafe_allow_html=True,
            )

        st.divider()
        st.markdown("**💡 Try asking…**")
        starters = [
            "Plan a 7-day trip to Tokyo from Delhi ✈️",
            "What's the weather like in Paris in October? 🌤️",
            "Find flights from Mumbai to Dubai next month",
            "Budget hotels in Bangkok for 2 adults 🏨",
            "Convert 50,000 INR to USD 💱",
        ]
        for s in starters:
            if st.button(s, use_container_width=True, key=f"starter_{s}"):
                st.session_state["_starter"] = s

        st.divider()
        if st.button("🗑️ Clear conversation", use_container_width=True, key="clear_btn"):
            st.session_state["messages"] = []
            st.session_state["thread_id"] = str(uuid.uuid4())
            st.rerun()


# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    st.markdown(DARK_CSS, unsafe_allow_html=True)

    # ── Session state init ──
    if "messages"  not in st.session_state:
        st.session_state["messages"]  = []
    if "thread_id" not in st.session_state:
        st.session_state["thread_id"] = str(uuid.uuid4())

    render_sidebar()

    # ── Header ──
    st.markdown(
        "<h2 style='color:#e5e5f0;margin-bottom:4px;'>🗺️ Trip Planner Agent</h2>"
        "<p style='color:#7070a0;font-size:13px;margin-top:0;'>Powered by Gemini · "
        "Ask me anything about your trip</p>",
        unsafe_allow_html=True,
    )
    st.divider()

    # ── Welcome card (only on empty conversation) ──
    if not st.session_state["messages"]:
        st.markdown(
            "<div class='welcome-card'>"
            "<div style='font-size:32px;margin-bottom:10px;'>👋</div>"
            "<div style='font-size:18px;font-weight:700;color:#d0d0f0;margin-bottom:6px;'>Where are you headed?</div>"
            "<div style='font-size:13px;color:#8888a8;line-height:1.6;'>"
            "Tell me your destination and travel dates, and I'll handle flights, hotels, "
            "weather, currency, and more — all in one conversation."
            "</div>"
            "</div>",
            unsafe_allow_html=True,
        )

    # ── Render chat history ──
    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            for card in msg.get("cards", []):
                _show_card(card["tool"], card["html"])
            if msg.get("content"):
                st.markdown(msg["content"])

    # ── Handle sidebar starter buttons ──
    user_input = st.chat_input("Where do you want to go?")
    starter = st.session_state.pop("_starter", None)
    user_input = user_input or starter

    if not user_input:
        return

    # ── Show user message ──
    st.session_state["messages"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # ── Stream agent response ──
    with st.chat_message("assistant"):
        status_placeholder = st.empty()
        text_placeholder   = st.empty()

        accumulated_text = ""
        collected_cards: list[dict] = []  # [{"tool": str, "html": str}]

        active_tool: str | None = None

        for event_type, payload in stream_response(user_input, st.session_state["thread_id"]):

            if event_type == "tool_start":
                active_tool = payload["name"]
                icon, label = TOOL_META.get(active_tool, ("⚙️", f"Running {active_tool}…"))
                status_placeholder.markdown(
                    f'<div class="tool-chip"><span>{icon}</span><span>{label}</span></div>',
                    unsafe_allow_html=True,
                )

            elif event_type == "tool_result":
                tool_name = payload["name"]
                active_tool = None
                status_placeholder.empty()

                card_html = render_card(
                    tool_name,
                    payload["content"],
                    payload["args"],
                )
                if card_html:
                    collected_cards.append({"tool": tool_name, "html": card_html})
                    _show_card(tool_name, card_html)

            elif event_type == "text":
                accumulated_text += payload
                text_placeholder.markdown(accumulated_text)

        status_placeholder.empty()

        # Save full turn to history
        st.session_state["messages"].append({
            "role":    "assistant",
            "content": accumulated_text,
            "cards":   collected_cards,
        })


if __name__ == "__main__":
    main()
