from app.schemas.comparison import CompareOut, CompareScore


class ComparisonService:
    """
    AI-powered destination comparison.
    In production plug in real data; here we use AI or mock scoring.
    """

    # Rough heuristic scores per well-known destination (extend as needed)
    DESTINATION_DATA: dict = {
        "goa": {"budget": 7.5, "safety": 7.0, "weather": 8.0, "crowd": 6.0, "nightlife": 9.0},
        "gokarna": {"budget": 8.5, "safety": 8.0, "weather": 8.5, "crowd": 8.5, "nightlife": 5.0},
        "manali": {"budget": 7.0, "safety": 7.5, "weather": 7.0, "crowd": 6.5, "nightlife": 5.5},
        "bali": {"budget": 7.0, "safety": 7.5, "weather": 8.5, "crowd": 6.0, "nightlife": 8.5},
        "paris": {"budget": 4.0, "safety": 7.0, "weather": 6.5, "crowd": 5.0, "nightlife": 8.5},
        "switzerland": {"budget": 3.0, "safety": 9.5, "weather": 7.0, "crowd": 7.0, "nightlife": 6.0},
    }
    DEFAULT = {"budget": 6.0, "safety": 6.5, "weather": 7.0, "crowd": 6.5, "nightlife": 6.0}

    def compare(self, destination1: str, destination2: str) -> CompareOut:
        d1_key = destination1.lower().strip()
        d2_key = destination2.lower().strip()
        d1_data = self.DESTINATION_DATA.get(d1_key, self.DEFAULT)
        d2_data = self.DESTINATION_DATA.get(d2_key, self.DEFAULT)

        def make_score(name: str, data: dict) -> CompareScore:
            overall = round(sum(data.values()) / len(data), 2)
            return CompareScore(
                destination=name,
                budget_score=data["budget"],
                safety_score=data["safety"],
                weather_score=data["weather"],
                crowd_score=data["crowd"],
                nightlife_score=data["nightlife"],
                overall_score=overall,
            )

        s1 = make_score(destination1, d1_data)
        s2 = make_score(destination2, d2_data)
        winner = destination1 if s1.overall_score >= s2.overall_score else destination2
        recommendation = (
            f"Based on overall scores, **{winner}** is the better choice. "
            f"{destination1} scores {s1.overall_score}/10 and "
            f"{destination2} scores {s2.overall_score}/10."
        )
        return CompareOut(destination1=s1, destination2=s2, recommendation=recommendation, winner=winner)
