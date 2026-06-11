from dataclasses import dataclass


@dataclass
class BudgetBreakdown:
    flights: float
    accommodation: float
    food: float
    activities: float
    local_transport: float
    miscellaneous: float
    total: float


class BudgetService:
    """Estimates budget split across categories based on destination and duration."""

    # Approximate daily cost weights per category (percentage of total)
    WEIGHTS = {
        "flights": 0.30,
        "accommodation": 0.28,
        "food": 0.18,
        "activities": 0.12,
        "local_transport": 0.07,
        "miscellaneous": 0.05,
    }

    def calculate_breakdown(
        self,
        total_budget: float,
        days: int,
        travelers: int,
    ) -> BudgetBreakdown:
        """Returns a BudgetBreakdown split from the total budget."""
        flights = round(total_budget * self.WEIGHTS["flights"], 2)
        accommodation = round(total_budget * self.WEIGHTS["accommodation"], 2)
        food = round(total_budget * self.WEIGHTS["food"], 2)
        activities = round(total_budget * self.WEIGHTS["activities"], 2)
        local_transport = round(total_budget * self.WEIGHTS["local_transport"], 2)
        miscellaneous = round(total_budget * self.WEIGHTS["miscellaneous"], 2)
        total = round(flights + accommodation + food + activities + local_transport + miscellaneous, 2)

        return BudgetBreakdown(
            flights=flights,
            accommodation=accommodation,
            food=food,
            activities=activities,
            local_transport=local_transport,
            miscellaneous=miscellaneous,
            total=total,
        )

    def per_person_budget(self, total_budget: float, travelers: int) -> float:
        """Returns per-person budget."""
        return round(total_budget / max(travelers, 1), 2)

    def daily_budget(self, total_budget: float, days: int, travelers: int) -> float:
        """Returns per-person per-day budget."""
        return round(total_budget / max(days, 1) / max(travelers, 1), 2)
