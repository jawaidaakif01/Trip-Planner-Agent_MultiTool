"""
ui/cards.py — Generative UI card renderers for each tool output.

Each function takes the tool's output dict and returns an HTML string
that can be injected via st.markdown(..., unsafe_allow_html=True).
"""

from __future__ import annotations

# ── Shared style constants ──────────────────────────────────────────────────
_BASE = (
    "background:rgba(15,15,28,0.85);"
    "border:1px solid rgba(255,255,255,0.08);"
    "border-radius:14px;"
    "padding:18px 20px;"
    "margin:10px 0;"
    "font-family:'Inter',sans-serif;"
    "color:#e5e5f0;"
    "backdrop-filter:blur(12px);"
)
_HEADER = (
    "font-size:13px;font-weight:600;color:#a0a0c8;text-transform:uppercase;"
    "letter-spacing:0.08em;margin-bottom:14px;"
)
_DIVIDER = "<hr style='border:none;border-top:1px solid rgba(255,255,255,0.06);margin:12px 0;'>"
_BADGE_GREEN = "background:rgba(16,185,129,0.15);color:#10b981;border:1px solid rgba(16,185,129,0.25);border-radius:20px;padding:2px 10px;font-size:11px;font-weight:600;"
_BADGE_INDIGO = "background:rgba(99,102,241,0.15);color:#a5b4fc;border:1px solid rgba(99,102,241,0.25);border-radius:20px;padding:2px 10px;font-size:11px;font-weight:600;"
_BADGE_AMBER = "background:rgba(245,158,11,0.15);color:#fbbf24;border:1px solid rgba(245,158,11,0.25);border-radius:20px;padding:2px 10px;font-size:11px;font-weight:600;"


# ── Weather helpers ─────────────────────────────────────────────────────────
def _weather_icon(code: int) -> str:
    if code == 0:
        return "☀️"
    if code in (1, 2):
        return "⛅"
    if code == 3:
        return "☁️"
    if code in (45, 48):
        return "🌫️"
    if code in (51, 53, 55):
        return "🌦️"
    if code in (61, 63, 65):
        return "🌧️"
    if code in (71, 73, 75, 77):
        return "❄️"
    if code in (80, 81, 82):
        return "🌦️"
    if code in (85, 86):
        return "🌨️"
    if code in (95, 96, 99):
        return "⛈️"
    return "🌡️"


def _short_date(date_str: str) -> str:
    """'2026-10-15' → 'Oct 15'"""
    try:
        from datetime import datetime
        return datetime.strptime(date_str[:10], "%Y-%m-%d").strftime("%b %d")
    except Exception:
        return date_str[:10]


def _short_day(date_str: str) -> str:
    """'2026-10-15' → 'Thu'"""
    try:
        from datetime import datetime
        return datetime.strptime(date_str[:10], "%Y-%m-%d").strftime("%a")
    except Exception:
        return ""


def _fmt_duration(minutes: int | None) -> str:
    if minutes is None:
        return "—"
    h, m = divmod(int(minutes), 60)
    return f"{h}h {m}m" if m else f"{h}h"


# ── Flight Card ─────────────────────────────────────────────────────────────
def flight_card(data: dict) -> str:
    origin = data.get("origin", "—")
    dest = data.get("destination", "—")
    dep = _short_date(data.get("departure_date", ""))
    ret = _short_date(data.get("return_date", ""))
    currency = data.get("currency", "")
    adults = data.get("adults", 1)
    found = data.get("flights_found", 0)
    lowest = data.get("lowest_price")
    price_level = data.get("price_level", "")
    price_range = data.get("typical_price_range") or []
    flights = data.get("flights", [])[:4]  # Show top 4

    level_badge = {
        "low": f"<span style='{_BADGE_GREEN}'>🟢 Low prices</span>",
        "typical": f"<span style='{_BADGE_INDIGO}'>🔵 Typical prices</span>",
        "high": f"<span style='{_BADGE_AMBER}'>🟡 High prices</span>",
    }.get(price_level, "")

    rows = ""
    for f in flights:
        segs = f.get("segments", [])
        airline = segs[0].get("airline", "—") if segs else "—"
        dep_time = segs[0].get("departure_time", "")[:5] if segs else "—"
        arr_time = segs[-1].get("arrival_time", "")[:5] if segs else "—"
        duration = _fmt_duration(f.get("total_duration_minutes"))
        stops = f.get("stops", 0)
        stop_label = "Direct" if stops == 0 else f"{stops} stop{'s' if stops > 1 else ''}"
        price = f.get("price")
        price_str = f"{currency} {price:,}" if price else "—"

        rows += f"""
        <div style="display:flex;align-items:center;justify-content:space-between;
                    padding:12px 14px;border-radius:10px;
                    background:rgba(255,255,255,0.03);margin-bottom:8px;
                    border:1px solid rgba(255,255,255,0.05);">
          <div style="flex:1;min-width:0;">
            <div style="font-weight:600;color:#e5e5f0;font-size:14px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{airline}</div>
            <div style="font-size:12px;color:#8888a8;margin-top:2px;">{dep_time} → {arr_time} · {duration}</div>
          </div>
          <div style="text-align:center;padding:0 16px;">
            <span style="{_BADGE_INDIGO if stops == 0 else _BADGE_AMBER}">{stop_label}</span>
          </div>
          <div style="text-align:right;white-space:nowrap;">
            <div style="font-size:16px;font-weight:700;color:#a5b4fc;">{price_str}</div>
          </div>
        </div>"""

    range_str = ""
    if price_range and len(price_range) == 2:
        range_str = f" · Typical: {currency} {price_range[0]:,}–{price_range[1]:,}"

    lowest_str = f"<b style='color:#10b981;'>{currency} {lowest:,}</b>" if lowest else "—"

    return f"""
<div style="{_BASE}">
  <div style="{_HEADER}">✈️ Flights</div>
  <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;margin-bottom:12px;">
    <div>
      <span style="font-size:20px;font-weight:700;color:#e5e5f0;">{origin}</span>
      <span style="color:#6366f1;font-size:18px;margin:0 10px;">→</span>
      <span style="font-size:20px;font-weight:700;color:#e5e5f0;">{dest}</span>
      <span style="font-size:13px;color:#8888a8;margin-left:10px;">{dep} → {ret} · {adults} adult{'s' if adults > 1 else ''}</span>
    </div>
    <span style="{_BADGE_INDIGO}">{found} found</span>
  </div>
  <div style="font-size:12px;color:#8888a8;margin-bottom:14px;">
    💡 Lowest price: {lowest_str}{range_str} &nbsp; {level_badge}
  </div>
  {_DIVIDER}
  {rows if rows else '<div style="color:#8888a8;font-size:13px;">No flight results found.</div>'}
</div>"""


# ── Hotel Card ──────────────────────────────────────────────────────────────
def hotel_card(data: dict) -> str:
    location = data.get("location", "—")
    check_in = _short_date(data.get("check_in", ""))
    check_out = _short_date(data.get("check_out", ""))
    adults = data.get("adults", 1)
    found = data.get("hotels_found", 0)
    search_url = data.get("search_url", "")
    hotels = data.get("hotels", [])[:5]

    rows = ""
    for h in hotels:
        name = h.get("name", "—")
        stars = "★" * int(h.get("star_rating") or 0)
        guest = h.get("guest_rating")
        guest_str = f"{guest:.1f}" if guest else "—"
        reviews = h.get("review_count")
        review_str = f"({reviews:,} reviews)" if reviews else ""
        price = h.get("price")
        curr = h.get("currency", "")
        price_str = f"{curr} {price:,.0f}/night" if price else "—"
        room = h.get("room_name", "")
        free_cancel = h.get("free_cancellation", False)
        cancel_badge = f"<span style='{_BADGE_GREEN}'>✓ Free cancellation</span>" if free_cancel else ""

        rows += f"""
        <div style="display:flex;align-items:flex-start;justify-content:space-between;
                    padding:14px;border-radius:10px;
                    background:rgba(255,255,255,0.03);margin-bottom:8px;
                    border:1px solid rgba(255,255,255,0.05);gap:12px;">
          <div style="flex:1;min-width:0;">
            <div style="font-weight:600;color:#e5e5f0;font-size:14px;
                        white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{name}</div>
            <div style="font-size:12px;color:#f59e0b;margin:2px 0;">{stars}</div>
            <div style="font-size:12px;color:#8888a8;">{room}</div>
            <div style="margin-top:6px;display:flex;gap:6px;flex-wrap:wrap;">
              {cancel_badge}
              {"<span style='" + _BADGE_INDIGO + "'>⭐ " + guest_str + " " + review_str + "</span>" if guest else ""}
            </div>
          </div>
          <div style="text-align:right;white-space:nowrap;flex-shrink:0;">
            <div style="font-size:16px;font-weight:700;color:#a5b4fc;">{price_str}</div>
          </div>
        </div>"""

    search_link = f'<a href="{search_url}" target="_blank" style="color:#6366f1;font-size:12px;text-decoration:none;">View all on Booking.com →</a>' if search_url else ""

    return f"""
<div style="{_BASE}">
  <div style="{_HEADER}">🏨 Hotels</div>
  <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;margin-bottom:14px;">
    <div>
      <span style="font-size:18px;font-weight:700;color:#e5e5f0;">{location}</span>
      <span style="font-size:13px;color:#8888a8;margin-left:10px;">{check_in} – {check_out} · {adults} adult{'s' if adults > 1 else ''}</span>
    </div>
    <span style="{_BADGE_INDIGO}">{found} found</span>
  </div>
  {_DIVIDER}
  {rows if rows else '<div style="color:#8888a8;font-size:13px;">No hotels found.</div>'}
  <div style="margin-top:8px;">{search_link}</div>
</div>"""


# ── Weather Forecast Card ───────────────────────────────────────────────────
def weather_card(data: dict) -> str:
    location = data.get("location", "—")
    forecast = data.get("daily_forecast", [])

    day_cells = ""
    for day in forecast[:10]:
        icon = _weather_icon(day.get("weather_code", 0))
        label = _short_day(day.get("date", ""))
        date = _short_date(day.get("date", ""))
        t_max = day.get("temperature_max")
        t_min = day.get("temperature_min")
        rain = day.get("precipitation_probability", 0)

        t_max_str = f"{t_max:.0f}°" if t_max is not None else "—"
        t_min_str = f"{t_min:.0f}°" if t_min is not None else "—"
        rain_str = f"{rain:.0f}%" if rain else "0%"

        day_cells += f"""
        <div style="text-align:center;padding:12px 10px;border-radius:10px;
                    background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.05);
                    min-width:72px;flex:1;">
          <div style="font-size:10px;color:#8888a8;font-weight:600;text-transform:uppercase;">{label}</div>
          <div style="font-size:10px;color:#8888a8;margin-bottom:6px;">{date}</div>
          <div style="font-size:22px;margin-bottom:6px;">{icon}</div>
          <div style="font-size:13px;font-weight:700;color:#e5e5f0;">{t_max_str}</div>
          <div style="font-size:11px;color:#8888a8;">{t_min_str}</div>
          <div style="font-size:10px;color:#60a5fa;margin-top:4px;">💧 {rain_str}</div>
        </div>"""

    return f"""
<div style="{_BASE}">
  <div style="{_HEADER}">🌤️ Weather Forecast</div>
  <div style="font-size:16px;font-weight:700;color:#e5e5f0;margin-bottom:14px;">{location}</div>
  <div style="display:flex;gap:8px;overflow-x:auto;padding-bottom:4px;">
    {day_cells if day_cells else '<div style="color:#8888a8;font-size:13px;">No forecast data.</div>'}
  </div>
</div>"""


# ── Historical Weather Card ─────────────────────────────────────────────────
def historical_weather_card(data: dict) -> str:
    location = data.get("location", "—")
    start = _short_date(data.get("trip_start_date", ""))
    end = _short_date(data.get("trip_end_date", ""))
    years = data.get("historical_years_used", 5)
    avg = data.get("average_weather", {})

    icon = _weather_icon(avg.get("most_common_weather_code", 0))
    t_max = avg.get("temperature_max")
    t_min = avg.get("temperature_min")
    rain = avg.get("rain_sum_mm")
    sun = avg.get("sunshine_duration_hours")
    wind = avg.get("wind_speed_max_kmh")
    sunrise = avg.get("average_sunrise", "—")[:5]
    sunset = avg.get("average_sunset", "—")[:5]

    def _stat(label: str, value: str, unit: str = "") -> str:
        return f"""
        <div style="text-align:center;padding:12px;border-radius:10px;
                    background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.05);flex:1;min-width:80px;">
          <div style="font-size:11px;color:#8888a8;margin-bottom:4px;">{label}</div>
          <div style="font-size:18px;font-weight:700;color:#e5e5f0;">{value}<span style="font-size:11px;color:#8888a8;">{unit}</span></div>
        </div>"""

    stats = "".join([
        _stat("Max Temp", f"{t_max:.0f}" if t_max is not None else "—", "°C"),
        _stat("Min Temp", f"{t_min:.0f}" if t_min is not None else "—", "°C"),
        _stat("Avg Rain", f"{rain:.1f}" if rain is not None else "—", "mm"),
        _stat("Sunshine", f"{sun:.1f}" if sun is not None else "—", "h"),
        _stat("Wind", f"{wind:.0f}" if wind is not None else "—", " km/h"),
    ])

    return f"""
<div style="{_BASE}">
  <div style="{_HEADER}">📊 Historical Weather</div>
  <div style="display:flex;align-items:center;gap:12px;margin-bottom:14px;">
    <span style="font-size:32px;">{icon}</span>
    <div>
      <div style="font-size:18px;font-weight:700;color:#e5e5f0;">{location}</div>
      <div style="font-size:12px;color:#8888a8;">Avg over {years} years · {start} to {end} &nbsp;·&nbsp; 🌅 {sunrise} &nbsp;🌇 {sunset}</div>
    </div>
  </div>
  {_DIVIDER}
  <div style="display:flex;gap:8px;flex-wrap:wrap;">
    {stats}
  </div>
</div>"""


# ── Currency Card ───────────────────────────────────────────────────────────
def currency_card(data: dict) -> str:
    """
    data = {
        "amount": 1000,
        "base_currency": "INR",
        "target_currency": "EUR",
        "result": 11.23
    }
    """
    amount = data.get("amount", "—")
    base = data.get("base_currency", "—")
    target = data.get("target_currency", "—")
    result = data.get("result")
    result_str = f"{result:,.4f}" if isinstance(result, (int, float)) else str(result)

    rate = None
    if isinstance(result, (int, float)) and isinstance(amount, (int, float)) and amount != 0:
        rate = result / amount

    rate_str = f"1 {base} = {rate:.4f} {target}" if rate else ""

    return f"""
<div style="{_BASE}max-width:420px;">
  <div style="{_HEADER}">💱 Currency Conversion</div>
  <div style="display:flex;align-items:center;gap:16px;flex-wrap:wrap;">
    <div style="text-align:center;">
      <div style="font-size:28px;font-weight:800;color:#e5e5f0;">{amount:,}<span style="font-size:14px;color:#8888a8;margin-left:4px;">{base}</span></div>
    </div>
    <div style="font-size:24px;color:#6366f1;">→</div>
    <div style="text-align:center;">
      <div style="font-size:28px;font-weight:800;color:#a5b4fc;">{result_str}<span style="font-size:14px;color:#8888a8;margin-left:4px;">{target}</span></div>
    </div>
  </div>
  {f'<div style="font-size:12px;color:#8888a8;margin-top:10px;">📈 {rate_str}</div>' if rate_str else ""}
</div>"""


# ── Web Search Card ─────────────────────────────────────────────────────────
def web_search_card(data: dict | list | str) -> str:
    """Handle Tavily's various output formats."""
    import json as _json

    results = []

    if isinstance(data, list):
        results = data
    elif isinstance(data, dict):
        results = data.get("results", [data])
    elif isinstance(data, str):
        try:
            parsed = _json.loads(data)
            if isinstance(parsed, list):
                results = parsed
            elif isinstance(parsed, dict):
                results = parsed.get("results", [])
        except Exception:
            return ""  # Can't parse, skip card

    if not results:
        return ""

    rows = ""
    for r in results[:4]:
        title = r.get("title", "—")
        url = r.get("url", "#")
        snippet = r.get("content", "")[:160].strip()
        if len(r.get("content", "")) > 160:
            snippet += "…"
        domain = url.split("/")[2] if "//" in url else url[:30]

        rows += f"""
        <div style="padding:12px 14px;border-radius:10px;
                    background:rgba(255,255,255,0.03);margin-bottom:8px;
                    border:1px solid rgba(255,255,255,0.05);">
          <a href="{url}" target="_blank"
             style="font-weight:600;color:#a5b4fc;font-size:14px;text-decoration:none;">{title}</a>
          <div style="font-size:11px;color:#10b981;margin:2px 0;">{domain}</div>
          <div style="font-size:12px;color:#8888a8;line-height:1.5;">{snippet}</div>
        </div>"""

    return f"""
<div style="{_BASE}">
  <div style="{_HEADER}">🔍 Web Results</div>
  {rows}
</div>"""
