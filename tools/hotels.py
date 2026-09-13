import os
import requests

from dotenv import load_dotenv
load_dotenv("../.env")

API_KEY = os.getenv("STAYINGAPI_KEY")


def hotel_search(location: str, check_in: str, check_out: str, adults: int, children: int, platforms: str = "booking", limit: int = 10) -> dict:
    """
    Searches for available accommodations using StayingAPI.

    The function takes the destination, check-in and check-out dates,
    number of adults and children, and the platform to search.
    It then fetches accommodation results and returns the useful
    hotel information such as ratings, amenities, occupancy and prices.
    """

    url = "https://api.stayingapi.com/v1/search"
    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }

    params = {
        "location": location,
        "checkIn": check_in,
        "checkOut": check_out,
        "adults": adults,
        "children": children,
        "platforms": platforms,
        "limit": 10
    }

    response = requests.get(
        url,
        headers=headers,
        params=params,
    )

    if response.status_code!=200:
        raise ValueError(
            f"Could not fetch hotel data: {response.status_code}"
            f"{response.text}"
        )
    data = response.json()

    hotels = []

    for hotel in data.get("data", []):
        price = hotel.get("price", {})
        hotel_location = hotel.get("location", {})

        hotels.append({
            "name": hotel.get("name"),
            "platform": hotel.get("platform"),
            "property_type": hotel.get("propertyType"),

            "location": hotel_location.get("address"),

            "star_rating": hotel.get("starRating"),
            "guest_rating": hotel.get("guestRating"),
            "review_count": hotel.get("reviewCount"),

            "max_occupancy": hotel.get("maxOccupancy"),
            "bedrooms": hotel.get("bedrooms"),
            "bathrooms": hotel.get("bathrooms"),

            "amenities": hotel.get("amenities", []),

            "nightly_price": price.get("nightlyPrice"),
            "total_price": price.get("totalPrice"),
            "currency": price.get("currency"),
            "nights": price.get("nights"),

            "url": price.get("url") or hotel.get("url")
        })

        return{
            "location": location,
            "check_in": check_in,
            "check_out": check_out,
            "adults": adults,
            "children": children,
            "platforms": platforms,
            "hotels": hotels
        }

result = hotel_search(
    location="Paris, FR",
    check_in="2026-10-15",
    check_out="2026-10-18",
    adults=2,
    children=0,
    platforms="booking",
    limit=10
)

print(result)