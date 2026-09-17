from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

from tools.currency_conversion import currency_conversion
from tools.flights import flight_search
from tools.historical_weather import get_historical_weather
from tools.weather import get_weather_forecast
from tools.hotels import hotel_search
from tools.web_search import web_search


llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite"
)

tools = [
    currency_conversion,
    flight_search,
    get_weather_forecast,
    get_historical_weather,
    hotel_search,
    web_search,
]


system_prompt = """
You are a smart Trip Planner Agent.

You help users plan complete trips using the tools provided to you.

When planning a trip, gather the necessary information from the user,
including the origin, destination, dates, number of travelers,
accommodation requirements, and relevant currency information.

If required information is missing, ask the user a follow-up question.

Remember information already provided in the current conversation and
do not ask for the same information again unnecessarily.

Use the available tools whenever current or external information is needed.

For weather information, follow these rules:
- Use `get_weather_forecast` for trips within the next 16 days.
- Use `get_historical_weather` for past dates or to understand typical
  seasonal conditions for a destination (e.g. "what's the weather like
  in Paris in July?").
"""

checkpointer = InMemorySaver()

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=system_prompt,
    checkpointer=checkpointer
)
