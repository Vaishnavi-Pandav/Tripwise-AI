from dataclasses import dataclass, field


@dataclass
class HotelSuggestion:
    name: str
    tier: str          # "budget" | "mid-range" | "luxury"
    price_per_night: float
    rating: float
    amenities: list[str] = field(default_factory=list)
    notes: str = ""


class HotelService:
    """
    Returns hotel suggestions based on destination and budget.
    In production, integrate with a real hotels API (e.g. Booking.com, Amadeus).
    """

    def get_suggestions(
        self,
        destination: str,
        budget_per_night: float,
    ) -> list[HotelSuggestion]:
        """
        Returns three tiered hotel suggestions.
        Placeholder logic — swap with real API data.
        """
        return [
            HotelSuggestion(
                name=f"Budget Inn {destination}",
                tier="budget",
                price_per_night=round(budget_per_night * 0.4, 2),
                rating=3.5,
                amenities=["Free WiFi", "Breakfast included"],
                notes="Great for solo or budget travelers.",
            ),
            HotelSuggestion(
                name=f"{destination} Comfort Suites",
                tier="mid-range",
                price_per_night=round(budget_per_night * 0.75, 2),
                rating=4.2,
                amenities=["Free WiFi", "Pool", "Gym", "Restaurant"],
                notes="Best value for families and couples.",
            ),
            HotelSuggestion(
                name=f"The Grand {destination}",
                tier="luxury",
                price_per_night=round(budget_per_night * 1.5, 2),
                rating=4.8,
                amenities=["Free WiFi", "Pool", "Spa", "Concierge", "Fine Dining"],
                notes="Premium experience with full amenities.",
            ),
        ]

    @staticmethod
    def budget_per_night(total_budget: float, days: int, accommodation_share: float = 0.28) -> float:
        """Derives recommended nightly hotel budget from total trip budget."""
        return round((total_budget * accommodation_share) / max(days, 1), 2)
