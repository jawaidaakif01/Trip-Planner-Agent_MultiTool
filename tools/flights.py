import os
import requests
from dotenv import load_dotenv

load_dotenv()

from langchain_core.tools import tool

api_key = os.getenv("SERPAPI_API_KEY")

@tool
def flight_search(
    origin: str, # Must be a 3-letter IATA airport code, e.g. "DEL" for New Delhi
    destination: str, # Must be a 3-letter IATA airport code, e.g. "CDG" for Paris
    departure_date: str,
    return_date: str,
    flight_currency: str = "INR",
    adults: int = 1
) -> dict:
    """
    Searches for flights using Google Flights through SerpApi.

    IMPORTANT: 'origin' and 'destination' MUST be 3-letter IATA airport codes.
    Never pass city names. Always convert city names to IATA codes first.
    Examples: New Delhi -> DEL, Paris -> CDG, Istanbul -> IST, Dubai -> DXB,
    London -> LHR, New York -> JFK, Mumbai -> BOM, Bangkok -> BKK,
    Guwahati -> GAU, Shillong -> SHL, Kolkata -> CCU.

    IMPORTANT: 'departure_date' and 'return_date' MUST be in 'YYYY-MM-DD' format.
    Example: October 15, 2026 -> '2026-10-15'. Never use any other date format.
    Always ensure dates are in the future relative to today.

    Returns flight options with airline, flight number, departure and
    arrival details, duration, stops, price, baggage information,
    and price insights.
    """

    url = "https://serpapi.com/search"

    params = {
        "engine": "google_flights",
        "departure_id": origin,
        "arrival_id": destination,
        "outbound_date": departure_date,
        "return_date": return_date,
        "currency": flight_currency,
        "adults": adults,
        "hl": "en",
        "api_key": api_key
    }

    response = requests.get(
        url=url,
        params=params
    )

    if response.status_code != 200:
        raise ValueError(
            f"Could not fetch flight data: "
            f"{response.status_code} {response.text}"
        )

    data = response.json()

    flights = []

    for flight_option in data.get("best_flights", []) + data.get("other_flights", []):

        segments = []

        for flight in flight_option.get("flights", []):

            departure = flight.get("departure_airport", {})
            arrival = flight.get("arrival_airport", {})

            segments.append({
                "airline": flight.get("airline"),
                "flight_number": flight.get("flight_number"),
                "departure_airport": departure.get("name"),
                "departure_code": departure.get("id"),
                "departure_time": departure.get("time"),
                "arrival_airport": arrival.get("name"),
                "arrival_code": arrival.get("id"),
                "arrival_time": arrival.get("time"),
                "duration_minutes": flight.get("duration"),
                "aircraft": flight.get("airplane"),
                "travel_class": flight.get("travel_class"),
                "legroom": flight.get("legroom"),
            })

        flights.append({
            "price": flight_option.get("price"),
            "type": flight_option.get("type"),
            "total_duration_minutes": flight_option.get("total_duration"),
            "stops": len(flight_option.get("layovers", [])),
            "layovers": [
                {
                    "airport": layover.get("name"),
                    "airport_code": layover.get("id"),
                    "duration_minutes": layover.get("duration")
                }
                for layover in flight_option.get("layovers", [])
            ],
            "segments": segments,
            "carbon_emissions_grams": (
                flight_option.get("carbon_emissions", {})
                .get("this_flight")
            ),
            "fare_conditions": flight_option.get("extensions", [])
        })

    return {
        "origin": origin,
        "destination": destination,
        "departure_date": departure_date,
        "return_date": return_date,
        "currency": flight_currency,
        "adults": adults,
        "flights_found": len(flights),
        "lowest_price": (
            data.get("price_insights", {})
            .get("lowest_price")
        ),
        "price_level": (
            data.get("price_insights", {})
            .get("price_level")
        ),
        "typical_price_range": (
            data.get("price_insights", {})
            .get("typical_price_range")
        ),
        "flights": flights
    }