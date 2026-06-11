from dataclasses import dataclass


@dataclass
class BudgetBreakdown:
    transport_cost: float
    hotel_cost: float
    food_cost: float
    activity_cost: float
    miscellaneous_cost: float
    total: float
    per_person: float
    daily_per_person: float


class BudgetService:
    WEIGHTS = {
        "flight":  {"transport": 0.32, "hotel": 0.28, "food": 0.18, "activity": 0.12, "misc": 0.10},
        "train":   {"transport": 0.18, "hotel": 0.30, "food": 0.22, "activity": 0.18, "misc": 0.12},
        "road":    {"transport": 0.15, "hotel": 0.30, "food": 0.25, "activity": 0.20, "misc": 0.10},
        "mixed":   {"transport": 0.25, "hotel": 0.29, "food": 0.20, "activity": 0.16, "misc": 0.10},
        "default": {"transport": 0.30, "hotel": 0.28, "food": 0.20, "activity": 0.14, "misc": 0.08},
    }

    def calculate_breakdown(
        self,
        total_budget: float,
        days: int,
        travelers: int,
        travel_mode: str = "default",
    ) -> BudgetBreakdown:
        w = self.WEIGHTS.get(travel_mode.lower(), self.WEIGHTS["default"])
        transport     = round(total_budget * w["transport"], 2)
        hotel         = round(total_budget * w["hotel"], 2)
        food          = round(total_budget * w["food"], 2)
        activity      = round(total_budget * w["activity"], 2)
        misc          = round(total_budget * w["misc"], 2)
        total         = round(transport + hotel + food + activity + misc, 2)
        per_person    = round(total / max(travelers, 1), 2)
        daily_pp      = round(per_person / max(days, 1), 2)
        return BudgetBreakdown(
            transport_cost=transport,
            hotel_cost=hotel,
            food_cost=food,
            activity_cost=activity,
            miscellaneous_cost=misc,
            total=total,
            per_person=per_person,
            daily_per_person=daily_pp,
        )
