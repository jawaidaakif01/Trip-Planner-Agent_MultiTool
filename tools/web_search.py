from langchain_tavily import TavilySearch
from dotenv import load_dotenv

load_dotenv()

web_search = TavilySearch(
    max_results=5
)


