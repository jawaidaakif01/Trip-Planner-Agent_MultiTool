import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("STAYAPI_KEY")

from langchain_core.tools import tool

@tool
def hotel_search(
    location: str,
    check_in: str,
    check_out: str,
    adults: int,
    rooms: int = 1,
    children: int = 0,
    currency: str = "EUR",
    rows_per_page: int = 10
) -> dict:
    """
    Searches for available hotels using StayAPI.

    The function first converts the given location into a Booking.com
    destination ID. It then uses that destination ID to search for
    available hotels for the given dates and number of guests.

    It returns useful hotel information such as ratings, prices,
    room names, cancellation policy and booking URLs.
    """

    headers = {
        "x-api-key": api_key
    }

    destination_url = (
        "https://api.stayapi.com/v1/booking/destinations/lookup"
    )

    destination_params = {
        "query": location
    }

    destination_response = requests.get(
        url=destination_url,
        headers=headers,
        params=destination_params
    )

    if destination_response.status_code != 200:
        raise ValueError(
            f"Could not find destination: "
            f"{destination_response.status_code} "
            f"{destination_response.text}"
        )

    destination_data = destination_response.json()

    dest_id = destination_data.get("dest_id")
    dest_type = destination_data.get("dest_type")

    if not dest_id:
        raise ValueError(
            f"Could not find a Booking.com destination for "
            f"'{location}'"
        )

    hotel_url = "https://api.stayapi.com/v1/booking/search"

    hotel_params = {
        "dest_id": dest_id,
        "dest_type": dest_type,
        "checkin": check_in,
        "checkout": check_out,
        "adults": adults,
        "rooms": rooms,
        "children": children,
        "currency": currency,
        "rows_per_page": rows_per_page
    }

    hotel_response = requests.get(
        url=hotel_url,
        headers=headers,
        params=hotel_params
    )

    if hotel_response.status_code != 200:
        raise ValueError(
            f"Could not fetch hotel data: "
            f"{hotel_response.status_code} "
            f"{hotel_response.text}"
        )

    data = hotel_response.json()

    hotels = []

    for hotel in data.get("data", {}).get("hotels", []):

        price = hotel.get("price") or {}
        rating = hotel.get("rating") or {}

        hotels.append({
            "hotel_id": hotel.get("hotel_id"),
            "name": hotel.get("name"),
            "address": hotel.get("address"),
            "city": hotel.get("city"),
            "distance": hotel.get("distance"),

            "star_rating": hotel.get("star_rating"),
            "guest_rating": rating.get("score"),
            "review_count": rating.get("review_count"),

            "price": round(price.get("amount"), 2) if price.get("amount") is not None else None,
            "currency": price.get("currency"),

            "room_name": hotel.get("room_name"),

            "free_cancellation": hotel.get("free_cancellation"),
            "no_prepayment": hotel.get("no_prepayment"),
            "is_sold_out": hotel.get("is_sold_out"),

            "image_url": hotel.get("image_url")
    })

    return {
        "location": location,
        "check_in": check_in,
        "check_out": check_out,
        "adults": adults,
        "children": children,
        "rooms": rooms,
        "hotels_found": len(hotels),
        "search_url": data.get("data", {}).get("search_url"),
        "hotels": hotels
    }