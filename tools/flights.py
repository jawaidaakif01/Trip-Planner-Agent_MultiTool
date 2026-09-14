import os
import requests
from dotenv import load_dotenv

load_dotenv("../.env")

api_key = os.getenv("SERPAPI_API_KEY")


def flight_search(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: str,
    currency: str = "INR",
    adults: int = 1
) -> dict:
    """
    Searches for flights using Google Flights through SerpApi.

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
        "currency": currency,
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
        "currency": currency,
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