import logging
from typing import Optional

from sqlalchemy.orm import Session

from app.models.destination import Destination
from app.schemas.comparison import (
    CompareOut,
    CompareScore,
    DestinationCompareOut,
    DestinationCompareRequest,
    DestinationScoreDetail,
    FactorComparison,
)

logger = logging.getLogger("tripwise")


# ── Built-in destination knowledge base ───────────────────────────────────────
# Scores out of 10. Extend by adding rows to the DB or expanding this dict.

DESTINATION_DB: dict[str, dict] = {
    "goa": {
        "country": "India", "state": "Goa",
        "budget": 7.5, "safety": 7.0, "weather": 8.0, "crowd": 5.5,
        "nightlife": 9.5, "food": 8.5, "adventure": 7.0, "family": 6.5,
        "best_season": "Nov–Feb",
        "known_for": "Beaches, Nightlife, Water Sports, Seafood, Portuguese Heritage",
        "pros": {"solo": ["Vibrant nightlife", "Easy to meet travellers"],
                 "couple": ["Romantic beaches", "Luxury resorts"],
                 "family": ["Beach activities", "Safe for kids"],
                 "friends": ["Party scene", "Water sports"],
                 "backpacker": ["Budget hostels", "Cheap local food"]},
        "cons": ["Crowded in peak season", "Tourist-heavy prices", "Hot summers"],
    },
    "gokarna": {
        "country": "India", "state": "Karnataka",
        "budget": 8.5, "safety": 8.5, "weather": 8.0, "crowd": 8.5,
        "nightlife": 4.5, "food": 7.0, "adventure": 7.5, "family": 7.5,
        "best_season": "Oct–Mar",
        "known_for": "Secluded Beaches, Temples, Hippie Culture, Trekking",
        "pros": {"solo": ["Peaceful", "Temple town vibes"],
                 "couple": ["Quiet beaches", "Scenic sunsets"],
                 "family": ["Safe, calm environment"],
                 "friends": ["Beach camping", "Budget travel"],
                 "backpacker": ["Very budget-friendly", "Laid-back"]},
        "cons": ["Limited nightlife", "Less connectivity", "Few luxury options"],
    },
    "manali": {
        "country": "India", "state": "Himachal Pradesh",
        "budget": 7.0, "safety": 7.5, "weather": 6.5, "crowd": 6.0,
        "nightlife": 5.0, "food": 7.5, "adventure": 9.5, "family": 7.0,
        "best_season": "Mar–Jun, Oct–Nov",
        "known_for": "Trekking, Skiing, Himalayas, River Rafting, Snow",
        "pros": {"solo": ["Adventure activities", "Scenic trails"],
                 "couple": ["Romantic snow views", "Cosy cafes"],
                 "family": ["Snow activities", "Nature walks"],
                 "friends": ["Skiing, rafting", "Budget trips"],
                 "backpacker": ["Cheap homestays", "Hiking trails"]},
        "cons": ["Very cold in winter", "Crowded in summer", "Road closures"],
    },
    "kerala": {
        "country": "India", "state": "Kerala",
        "budget": 7.0, "safety": 8.5, "weather": 7.5, "crowd": 7.0,
        "nightlife": 4.0, "food": 9.5, "adventure": 7.0, "family": 9.0,
        "best_season": "Sep–Mar",
        "known_for": "Backwaters, Ayurveda, Cuisine, Wildlife, Houseboats",
        "pros": {"solo": ["Peaceful, spiritual", "Unique experiences"],
                 "couple": ["Houseboat stays", "Romantic backwaters"],
                 "family": ["Wildlife parks", "Safe culture"],
                 "friends": ["Budget group trips"],
                 "backpacker": ["Inexpensive food", "Scenic routes"]},
        "cons": ["Monsoons", "Limited nightlife", "Slow pace"],
    },
    "rajasthan": {
        "country": "India", "state": "Rajasthan",
        "budget": 7.5, "safety": 7.0, "weather": 6.0, "crowd": 6.5,
        "nightlife": 5.0, "food": 8.5, "adventure": 7.0, "family": 8.5,
        "best_season": "Oct–Mar",
        "known_for": "Forts, Palaces, Desert Safari, Rajputana Heritage, Cuisine",
        "pros": {"solo": ["Rich history", "Photography"],
                 "couple": ["Palace hotels", "Desert romance"],
                 "family": ["Forts, culture", "Camel rides"],
                 "friends": ["Group palace tours"],
                 "backpacker": ["Budget guesthouses"]},
        "cons": ["Very hot in summer", "Limited greenery", "Dry climate"],
    },
    "bali": {
        "country": "Indonesia", "state": "Bali",
        "budget": 7.0, "safety": 7.5, "weather": 8.5, "crowd": 6.0,
        "nightlife": 8.5, "food": 8.5, "adventure": 8.5, "family": 7.5,
        "best_season": "Apr–Oct",
        "known_for": "Temples, Rice Terraces, Surfing, Nightlife, Yoga",
        "pros": {"solo": ["Digital nomad hub", "Party scene"],
                 "couple": ["Romantic resorts", "Scenic beauty"],
                 "family": ["Cultural immersion", "Safe beaches"],
                 "friends": ["Water sports", "Parties"],
                 "backpacker": ["Cheap hostels", "Street food"]},
        "cons": ["Crowded tourist spots", "Rainy season (Nov–Mar)"],
    },
    "shimla": {
        "country": "India", "state": "Himachal Pradesh",
        "budget": 7.0, "safety": 8.0, "weather": 7.5, "crowd": 6.0,
        "nightlife": 4.0, "food": 7.0, "adventure": 7.0, "family": 8.5,
        "best_season": "Mar–Jun, Dec–Jan",
        "known_for": "Colonial Architecture, Snow, Toy Train, Mall Road",
        "pros": {"solo": ["Peaceful hill station"],
                 "couple": ["Snow views", "Cosy stays"],
                 "family": ["Safe, clean", "Snow activities"],
                 "friends": ["Group trips"],
                 "backpacker": ["Budget options"]},
        "cons": ["Crowded in peak", "Limited adventure"],
    },
}

# ── Traveler type weights — which factors matter most ─────────────────────────

TRAVELER_WEIGHTS: dict[str, dict[str, float]] = {
    "solo":       {"budget": 1.5, "safety": 1.5, "adventure": 1.3, "nightlife": 1.2,
                   "food": 1.0, "weather": 1.0, "crowd": 0.8, "family": 0.3},
    "couple":     {"budget": 1.0, "safety": 1.3, "weather": 1.5, "nightlife": 1.2,
                   "food": 1.3, "adventure": 0.8, "crowd": 1.0, "family": 0.5},
    "family":     {"budget": 1.2, "safety": 2.0, "family": 2.0, "food": 1.3,
                   "weather": 1.2, "crowd": 1.0, "adventure": 0.5, "nightlife": 0.2},
    "friends":    {"budget": 1.3, "nightlife": 1.8, "adventure": 1.5, "food": 1.2,
                   "weather": 1.0, "safety": 1.0, "crowd": 0.8, "family": 0.3},
    "backpacker": {"budget": 2.0, "adventure": 1.5, "crowd": 1.2, "food": 1.0,
                   "safety": 1.0, "weather": 0.8, "nightlife": 0.8, "family": 0.2},
}

DEFAULT_WEIGHTS = {k: 1.0 for k in ["budget","safety","weather","crowd","nightlife","food","adventure","family"]}

FACTOR_LABELS = {
    "budget":    "Budget Friendliness",
    "safety":    "Safety",
    "weather":   "Weather",
    "crowd":     "Low Crowd Level",
    "nightlife": "Nightlife",
    "food":      "Food & Cuisine",
    "adventure": "Adventure Activities",
    "family":    "Family Friendliness",
}


class ComparisonService:

    def compare_destinations(
        self,
        db: Session,
        payload: DestinationCompareRequest,
    ) -> DestinationCompareOut:
        """Full comparison with AI insight."""
        d1_key = payload.destination1.lower().strip()
        d2_key = payload.destination2.lower().strip()

        # Try DB first, fall back to built-in knowledge base
        d1_data, d1_src = self._get_destination_data(db, d1_key, payload.destination1)
        d2_data, d2_src = self._get_destination_data(db, d2_key, payload.destination2)
        source = "database" if d1_src == "db" or d2_src == "db" else "heuristic"

        traveler = payload.traveler_type or "friends"
        weights  = TRAVELER_WEIGHTS.get(traveler, DEFAULT_WEIGHTS)

        s1 = self.calculate_scores(payload.destination1, d1_data, weights, traveler)
        s2 = self.calculate_scores(payload.destination2, d2_data, weights, traveler)

        factors    = self._build_factor_comparisons(payload.destination1, payload.destination2,
                                                     d1_data, d2_data)
        winner     = payload.destination1 if s1.overall_score >= s2.overall_score else payload.destination2
        rec        = self._generate_recommendation(s1, s2, winner, traveler)
        best_for   = self._best_for_traveler(s1, s2, traveler)
        ai_insight = self._ai_insight(payload.destination1, payload.destination2,
                                       d1_data, d2_data, traveler)

        return DestinationCompareOut(
            destination1=s1,
            destination2=s2,
            factor_comparisons=factors,
            winner=winner,
            recommendation=rec,
            best_for_traveler=best_for,
            ai_insight=ai_insight,
            source=source,
        )

    def calculate_scores(
        self,
        name: str,
        data: dict,
        weights: dict,
        traveler: str,
    ) -> DestinationScoreDetail:
        """Calculate weighted overall score and build pros/cons lists."""
        raw_scores = {
            "budget":    data.get("budget", 6.0),
            "safety":    data.get("safety", 6.5),
            "weather":   data.get("weather", 7.0),
            "crowd":     data.get("crowd", 6.5),
            "nightlife": data.get("nightlife", 6.0),
            "food":      data.get("food", 7.0),
            "adventure": data.get("adventure", 6.5),
            "family":    data.get("family", 7.0),
        }
        weighted_sum = sum(raw_scores[k] * weights.get(k, 1.0) for k in raw_scores)
        weight_total = sum(weights.get(k, 1.0) for k in raw_scores)
        overall = round(weighted_sum / weight_total, 2)

        pros = self._extract_pros(raw_scores, data, traveler)
        cons = list(data.get("cons", []))[:3]
        best_for = self._best_traveler_types(raw_scores)

        return DestinationScoreDetail(
            destination=name,
            country=data.get("country", "India"),
            avg_budget_score=raw_scores["budget"],
            safety_score=raw_scores["safety"],
            weather_score=raw_scores["weather"],
            crowd_score=raw_scores["crowd"],
            nightlife_score=raw_scores["nightlife"],
            food_score=raw_scores["food"],
            adventure_score=raw_scores["adventure"],
            family_friendly_score=raw_scores["family"],
            overall_score=overall,
            pros=pros,
            cons=cons,
            best_for=best_for,
            best_season=data.get("best_season"),
            known_for=data.get("known_for"),
        )

    def generate_recommendation(
        self,
        s1: DestinationScoreDetail,
        s2: DestinationScoreDetail,
        winner: str,
        traveler: str,
    ) -> str:
        return self._generate_recommendation(s1, s2, winner, traveler)

    # ── Private helpers ────────────────────────────────────────────────────────

    def _get_destination_data(
        self, db: Session, key: str, original_name: str
    ) -> tuple[dict, str]:
        """Try DB → built-in dict → default."""
        dest: Optional[Destination] = (
            db.query(Destination)
            .filter(Destination.city_name.ilike(f"%{key}%"))
            .first()
        )
        if dest:
            return {
                "country":    dest.country or "India",
                "state":      dest.state,
                "budget":     dest.avg_budget_score or 6.0,
                "safety":     dest.safety_score or 6.5,
                "weather":    dest.weather_score or 7.0,
                "crowd":      dest.crowd_score or 6.5,
                "nightlife":  dest.nightlife_score or 6.0,
                "food":       dest.food_score or 7.0,
                "adventure":  dest.adventure_score or 6.5,
                "family":     dest.family_friendly_score or 7.0,
                "best_season": dest.best_season,
                "known_for":  dest.known_for,
                "pros":       {},
                "cons":       [],
            }, "db"

        built_in = DESTINATION_DB.get(key)
        if built_in:
            return built_in, "heuristic"

        # Unknown destination — return defaults
        return {
            "country": "Unknown", "budget": 6.0, "safety": 6.5, "weather": 7.0,
            "crowd": 6.5, "nightlife": 6.0, "food": 7.0, "adventure": 6.5,
            "family": 7.0, "best_season": None, "known_for": None,
            "pros": {}, "cons": [],
        }, "heuristic"

    @staticmethod
    def _build_factor_comparisons(
        name1: str, name2: str, d1: dict, d2: dict
    ) -> list[FactorComparison]:
        factors = []
        factor_map = {
            "budget":    ("budget",    "Budget friendliness"),
            "safety":    ("safety",    "Safety for tourists"),
            "weather":   ("weather",   "Weather & climate"),
            "crowd":     ("crowd",     "Crowd levels"),
            "nightlife": ("nightlife", "Nightlife scene"),
            "food":      ("food",      "Food & cuisine"),
            "adventure": ("adventure", "Adventure activities"),
            "family":    ("family",    "Family friendliness"),
        }
        for key, (data_key, label) in factor_map.items():
            s1 = d1.get(data_key, 6.0)
            s2 = d2.get(data_key, 6.0)
            winner = name1 if s1 >= s2 else name2
            diff   = abs(s1 - s2)
            if diff < 0.5:
                insight = f"Both destinations are similar in {label.lower()}."
            elif winner == name1:
                insight = f"{name1} is {'significantly' if diff > 2 else 'slightly'} better for {label.lower()}."
            else:
                insight = f"{name2} is {'significantly' if diff > 2 else 'slightly'} better for {label.lower()}."
            factors.append(FactorComparison(
                factor=label, dest1_score=s1, dest2_score=s2,
                winner=winner, insight=insight,
            ))
        return factors

    @staticmethod
    def _generate_recommendation(
        s1: DestinationScoreDetail,
        s2: DestinationScoreDetail,
        winner: str,
        traveler: str,
    ) -> str:
        loser = s2.destination if winner == s1.destination else s1.destination
        winner_score = s1.overall_score if winner == s1.destination else s2.overall_score
        loser_score  = s2.overall_score if winner == s1.destination else s1.overall_score
        gap = round(winner_score - loser_score, 2)
        traveler_note = f" for {traveler} travelers" if traveler else ""
        strength = "significantly" if gap > 1.5 else "slightly"

        return (
            f"**{winner}** is the recommended destination{traveler_note}, "
            f"scoring {winner_score}/10 vs {loser}'s {loser_score}/10 "
            f"({strength} better overall). "
            f"{winner} excels in: {', '.join(s1.pros[:2] if winner == s1.destination else s2.pros[:2])}."
        )

    @staticmethod
    def _best_for_traveler(
        s1: DestinationScoreDetail, s2: DestinationScoreDetail, traveler: str
    ) -> str:
        winner = s1.destination if s1.overall_score >= s2.overall_score else s2.destination
        return f"{winner} is the best choice for {traveler} travelers."

    @staticmethod
    def _extract_pros(raw_scores: dict, data: dict, traveler: str) -> list[str]:
        pros: list[str] = []
        # Traveler-specific pros from DB
        traveler_pros = data.get("pros", {})
        if isinstance(traveler_pros, dict) and traveler in traveler_pros:
            pros.extend(traveler_pros[traveler][:2])
        # Score-based auto-pros
        if raw_scores["food"] >= 8.5:
            pros.append("Exceptional cuisine")
        if raw_scores["safety"] >= 8.5:
            pros.append("Very safe for tourists")
        if raw_scores["budget"] >= 8.0:
            pros.append("Very budget-friendly")
        if raw_scores["adventure"] >= 8.5:
            pros.append("Excellent adventure activities")
        if raw_scores["weather"] >= 8.5:
            pros.append("Ideal weather")
        if not pros:
            pros.append("Good overall experience")
        return pros[:5]

    @staticmethod
    def _best_traveler_types(scores: dict) -> list[str]:
        types = []
        if scores["nightlife"] >= 8.0 and scores["adventure"] >= 7.0:
            types.append("friends")
        if scores["safety"] >= 8.0 and scores["family"] >= 8.0:
            types.append("family")
        if scores["budget"] >= 8.0 and scores["adventure"] >= 7.5:
            types.append("backpacker")
        if scores["weather"] >= 8.0 and scores["food"] >= 8.0:
            types.append("couple")
        if scores["adventure"] >= 8.5:
            types.append("solo")
        return types or ["all travelers"]

    @staticmethod
    def _ai_insight(
        name1: str, name2: str, d1: dict, d2: dict, traveler: str
    ) -> str:
        """Generate a concise insight paragraph without calling Gemini (rule-based)."""
        better_budget   = name1 if d1.get("budget", 6) >= d2.get("budget", 6) else name2
        better_safety   = name1 if d1.get("safety", 6) >= d2.get("safety", 6) else name2
        better_nightlife= name1 if d1.get("nightlife", 6) >= d2.get("nightlife", 6) else name2
        better_food     = name1 if d1.get("food", 6) >= d2.get("food", 6) else name2

        lines = [
            f"**{better_budget}** offers better value for money.",
            f"**{better_safety}** is the safer option for tourists.",
        ]
        if traveler in ("friends", "solo"):
            lines.append(f"For nightlife, **{better_nightlife}** wins hands down.")
        if traveler in ("couple", "family"):
            lines.append(f"Food lovers will prefer **{better_food}** for its cuisine variety.")

        known1 = d1.get("known_for", "")
        known2 = d2.get("known_for", "")
        if known1:
            lines.append(f"{name1} is known for: {known1.split(',')[0].strip()}.")
        if known2:
            lines.append(f"{name2} is known for: {known2.split(',')[0].strip()}.")

        return " ".join(lines)

    # ── Backwards compat ──────────────────────────────────────────────────────

    def compare(self, destination1: str, destination2: str) -> CompareOut:
        """Legacy compare — no DB, no traveler type."""
        d1 = DESTINATION_DB.get(destination1.lower().strip(), {
            "budget": 6.0, "safety": 6.5, "weather": 7.0, "crowd": 6.5, "nightlife": 6.0,
        })
        d2 = DESTINATION_DB.get(destination2.lower().strip(), {
            "budget": 6.0, "safety": 6.5, "weather": 7.0, "crowd": 6.5, "nightlife": 6.0,
        })

        def make(name, data) -> CompareScore:
            keys = ["budget", "safety", "weather", "crowd", "nightlife"]
            vals = [data.get(k, 6.0) for k in keys]
            return CompareScore(
                destination=name,
                budget_score=data.get("budget", 6.0),
                safety_score=data.get("safety", 6.5),
                weather_score=data.get("weather", 7.0),
                crowd_score=data.get("crowd", 6.5),
                nightlife_score=data.get("nightlife", 6.0),
                overall_score=round(sum(vals) / len(vals), 2),
            )

        s1, s2 = make(destination1, d1), make(destination2, d2)
        winner = destination1 if s1.overall_score >= s2.overall_score else destination2
        return CompareOut(
            destination1=s1, destination2=s2, winner=winner,
            recommendation=f"**{winner}** scores higher overall.",
        )
