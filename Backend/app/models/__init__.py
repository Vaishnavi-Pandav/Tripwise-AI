# Import all models here so SQLAlchemy and Alembic can discover them.
from app.models.user import User
from app.models.trip import Trip
from app.models.hotel import Hotel
from app.models.hotel_recommendation import HotelRecommendation
from app.models.package import TravelPackage
from app.models.expenses import TripExpenses
from app.models.itinerary import Itinerary
from app.models.attraction import Attraction
from app.models.hidden_gem import HiddenGem
from app.models.destination_comparison import DestinationComparison
from app.models.saved_trip import SavedTrip
from app.models.ai_chat import AIChatHistory
from app.models.review import Review
from app.models.weather import WeatherDataCache
from app.models.user_preferences import UserPreferences
from app.models.ai_suggestion import AITripSuggestion

__all__ = [
    "User",
    "Trip",
    "Hotel",
    "HotelRecommendation",
    "TravelPackage",
    "TripExpenses",
    "Itinerary",
    "Attraction",
    "HiddenGem",
    "DestinationComparison",
    "SavedTrip",
    "AIChatHistory",
    "Review",
    "WeatherDataCache",
    "UserPreferences",
    "AITripSuggestion",
]
