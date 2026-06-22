import logging
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.attraction import Attraction
from app.models.hidden_gem import HiddenGem, GemCategory
from app.models.trip import Trip
from app.schemas.attraction import (
    HiddenGemOut,
    HiddenGemRecommendationItem,
    HiddenGemRecommendResponse,
)

logger = logging.getLogger("tripwise")

# ── Built-in gem knowledge base ────────────────────────────────────────────────
# Used when DB has no seeded gems for the city

BUILT_IN_GEMS: dict[str, list[dict]] = {
    "goa": [
        {"name": "Butterfly Beach",       "category": "beach",     "cost": 500,
         "crowd": "low",  "best_time": "Oct–Apr, Morning",
         "types": "couples,solo,friends",
         "desc": "A secluded beach accessible only by boat or a short trek. Crystal-clear water and minimal crowds.",
         "tips": ["Hire a boat from Palolem for ₹400", "Carry snorkelling gear", "Best visited in morning"]},
        {"name": "Divar Island",           "category": "nature",    "cost": 200,
         "crowd": "low",  "best_time": "Nov–Feb",
         "types": "solo,couples,backpacker",
         "desc": "A quiet island connected by ferry, with old Portuguese houses and paddy fields.",
         "tips": ["Take the free government ferry from Old Goa", "Rent a cycle for ₹100", "Visit during Christmas week"]},
        {"name": "Chapora Fort Sunrise",   "category": "viewpoint", "cost": 0,
         "crowd": "medium", "best_time": "6–7 AM",
         "types": "solo,couples,friends",
         "desc": "The real Dil Chahta Hai fort. Sunrise views over Vagator beach are spectacular.",
         "tips": ["Go before 6:30 AM to avoid crowds", "Park at the base and walk up", "Bring a jacket in winter"]},
        {"name": "Netravali Bubble Lake",  "category": "nature",    "cost": 100,
         "crowd": "low",  "best_time": "Monsoon (Jul–Sep)",
         "types": "adventure,backpacker,solo",
         "desc": "A mysterious lake in South Goa where bubbles rise continuously from the ground.",
         "tips": ["Hire a local guide (₹200)", "Best during monsoon", "Combine with Netravali Wildlife Sanctuary"]},
        {"name": "Cabo de Rama Fort",      "category": "historical","cost": 0,
         "crowd": "low",  "best_time": "Oct–Feb, Sunset",
         "types": "solo,couples,backpacker",
         "desc": "An ancient coastal fort with panoramic ocean views. Far fewer tourists than Aguada.",
         "tips": ["Sunset is magical here", "Carry water — no shops nearby", "30 min from Benaulim"]},
    ],
    "manali": [
        {"name": "Chandrakhani Pass",     "category": "trek",      "cost": 1500,
         "crowd": "low",  "best_time": "Jun–Sep",
         "types": "adventure,solo,friends",
         "desc": "A stunning high-altitude pass (3660m) offering views of Deo Tibba. Much less crowded than Rohtang.",
         "tips": ["Start from Naggar village", "Hire a guide for ₹1000/day", "Carry warm layers even in summer"]},
        {"name": "Hamta Village",          "category": "nature",    "cost": 300,
         "crowd": "low",  "best_time": "May–Oct",
         "types": "backpacker,solo,couples",
         "desc": "A traditional Himachali village en route to Hamta Pass. Apple orchards and local homestays.",
         "tips": ["Stay in a homestay for authentic food", "15 km from Manali", "Trek to the Hamta waterfall nearby"]},
        {"name": "Jagatsukh Temple Trail", "category": "historical","cost": 0,
         "crowd": "low",  "best_time": "Year-round",
         "types": "solo,couples,family",
         "desc": "Ancient Shiva and Gauri Shankar temples in a quiet village 6 km from Manali.",
         "tips": ["Walk from Jagatsukh village", "Photography allowed outside", "Combine with Deo Tibba base camp trek"]},
    ],
    "kerala": [
        {"name": "Thenmala — Shenduruny Rope Bridge", "category": "adventure", "cost": 200,
         "crowd": "low",  "best_time": "Oct–Mar",
         "types": "adventure,friends,family",
         "desc": "India's first planned eco-tourism destination with a 100m rope bridge over a forest stream.",
         "tips": ["Buy tickets in advance on weekends", "Combine with butterfly safari", "Start early — closes at 5 PM"]},
        {"name": "Pookode Lake Sunrise",  "category": "nature",    "cost": 50,
         "crowd": "low",  "best_time": "6–8 AM, Nov–Feb",
         "types": "couples,solo,family",
         "desc": "A freshwater lake at 770m altitude near Wayanad. Misty mornings are magical.",
         "tips": ["Rowboats available for ₹100", "Go before 8 AM for mist", "Combine with Wayanad Wildlife Sanctuary"]},
    ],
    "rajasthan": [
        {"name": "Bhangarh Fort — Night",  "category": "historical","cost": 100,
         "crowd": "medium","best_time": "Oct–Feb, Dusk",
         "types": "friends,adventure,solo",
         "desc": "India's most haunted fort — government bans entry after sunset. Daytime visit is eerie and atmospheric.",
         "tips": ["Leave before sunset (mandatory)", "Best photography at golden hour", "130 km from Jaipur"]},
        {"name": "Kheechan Crane Village", "category": "nature",    "cost": 0,
         "crowd": "low",  "best_time": "Oct–Mar (migration season)",
         "types": "solo,couples,family",
         "desc": "Thousands of Demoiselle cranes land here every winter. One of India's best bird-watching spots.",
         "tips": ["Best at sunrise (6–8 AM)", "150 km from Jodhpur", "No entry fee — locals feed the cranes"]},
    ],
}

# Traveler type to preferred categories
TYPE_CATEGORY_PREFERENCE: dict[str, list[str]] = {
    "solo":       ["trek", "viewpoint", "historical", "nature", "adventure"],
    "couple":     ["beach", "viewpoint", "cafe", "nature", "waterfall"],
    "family":     ["nature", "historical", "waterfall", "cafe"],
    "friends":    ["beach", "adventure", "viewpoint", "trek", "cafe"],
    "backpacker": ["trek", "nature", "historical", "adventure", "waterfall"],
}

# Budget thresholds
BUDGET_TIERS = {"low": 500, "mid": 2000, "high": float("inf")}


class HiddenGemService:

    # ── Get all gems for a city ───────────────────────────────────────────────

    def get_hidden_gems(
        self,
        db: Session,
        city: str,
        category: Optional[str] = None,
        crowd_level: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> list[HiddenGemOut]:
        """Return DB gems + built-in gems for a city."""
        q = db.query(HiddenGem).filter(HiddenGem.city.ilike(f"%{city}%"))
        if category:
            q = q.filter(HiddenGem.category == category.lower())
        if crowd_level:
            q = q.filter(HiddenGem.crowd_level == crowd_level.lower())

        db_gems = q.offset((page - 1) * page_size).limit(page_size).all()
        results = [HiddenGemOut.model_validate(g) for g in db_gems]

        # Supplement with built-in knowledge if DB is sparse
        if len(results) < 3:
            built_in = self._get_built_in(city, category)
            results.extend(built_in[:max(0, page_size - len(results))])

        return results

    # ── Recommend gems for a trip ─────────────────────────────────────────────

    def recommend_hidden_gems(
        self,
        db: Session,
        trip_id: str,
    ) -> HiddenGemRecommendResponse:
        """
        Score and rank hidden gems based on:
        - Traveler type preference
        - Budget per day
        - Crowd preference (inferred from traveler type)
        """
        trip: Optional[Trip] = db.query(Trip).filter(Trip.id == trip_id).first()
        if not trip:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")

        city            = trip.destination_location
        budget_per_day  = float(trip.budget) / max(trip.number_of_days, 1)
        traveler_type   = self._infer_traveler_type(trip)

        # Get candidates from DB + built-in
        db_gems = db.query(HiddenGem).filter(HiddenGem.city.ilike(f"%{city}%")).all()
        candidates = [self._db_gem_to_dict(g) for g in db_gems]
        if len(candidates) < 3:
            candidates.extend(self._get_built_in_raw(city))

        if not candidates:
            return HiddenGemRecommendResponse(
                trip_id=trip_id, destination=city,
                traveler_type=traveler_type,
                recommendations=[], total_found=0,
            )

        scored = self._score_candidates(candidates, traveler_type, budget_per_day)
        top    = scored[:6]

        recommendations = [
            HiddenGemRecommendationItem(
                id=c.get("id", "builtin"),
                name=c["name"],
                city=city,
                category=c.get("category"),
                estimated_cost=c.get("cost"),
                crowd_level=c.get("crowd"),
                best_time=c.get("best_time"),
                image_url=c.get("image_url"),
                reason=self.generate_reasoning(c, traveler_type, budget_per_day),
                best_for=self._best_for_label(c, traveler_type),
                travel_tips=c.get("tips", [])[:3],
            )
            for c in top
        ]

        logger.info(f"Hidden gems recommended: trip={trip_id} city={city} count={len(recommendations)}")
        return HiddenGemRecommendResponse(
            trip_id=trip_id,
            destination=city,
            traveler_type=traveler_type,
            recommendations=recommendations,
            total_found=len(candidates),
        )

    # ── Reasoning engine ──────────────────────────────────────────────────────

    def generate_reasoning(
        self, gem: dict, traveler_type: str, budget_per_day: float
    ) -> str:
        """Generate a natural-language reason for this recommendation."""
        name     = gem.get("name", "This place")
        category = gem.get("category", "spot")
        crowd    = gem.get("crowd", "low")
        cost     = gem.get("cost", 0)
        types    = gem.get("types", "")

        reasons = []

        if crowd == "low":
            reasons.append("off the tourist trail with very few crowds")
        elif crowd == "medium":
            reasons.append("moderately visited — not overly crowded")

        if traveler_type in types:
            reasons.append(f"ideal for {traveler_type} travelers")

        if cost == 0:
            reasons.append("completely free to visit")
        elif cost and budget_per_day > 0 and cost <= budget_per_day * 0.2:
            reasons.append(f"very affordable at just ₹{int(cost)}")

        cat_reason = {
            "beach":     "a secluded beach experience away from tourist hordes",
            "trek":      "a rewarding trek with stunning views",
            "viewpoint": "panoramic views that most tourists miss",
            "cafe":      "a charming local cafe loved by residents",
            "waterfall": "a hidden waterfall worth the journey",
            "historical":"rich history that most guidebooks overlook",
            "adventure": "a thrilling adventure activity",
            "nature":    "an immersive nature experience",
        }.get(category, "a unique local experience")
        reasons.append(cat_reason)

        return f"{name} is {', '.join(reasons[:3])}."

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _infer_traveler_type(trip: Trip) -> str:
        n = trip.number_of_travelers
        if n == 1:
            return "solo"
        if n == 2:
            return "couple"
        if n >= 4:
            return "friends"
        return "friends"

    @staticmethod
    def _score_candidates(
        candidates: list[dict],
        traveler_type: str,
        budget_per_day: float,
    ) -> list[dict]:
        preferred_cats = TYPE_CATEGORY_PREFERENCE.get(traveler_type, [])
        prefer_low_crowd = traveler_type in ("solo", "couple", "backpacker")

        def score(c: dict) -> float:
            s = 0.0
            # Category match (40 pts)
            cat = c.get("category", "")
            if cat in preferred_cats:
                s += 40 - (preferred_cats.index(cat) * 5)
            # Budget fit (30 pts)
            cost = float(c.get("cost", 0) or 0)
            if budget_per_day > 0:
                ratio = cost / budget_per_day
                if ratio <= 0.1:
                    s += 30
                elif ratio <= 0.25:
                    s += 20
                elif ratio <= 0.5:
                    s += 10
            else:
                s += 15
            # Crowd preference (20 pts)
            crowd = c.get("crowd", "low")
            if prefer_low_crowd and crowd == "low":
                s += 20
            elif not prefer_low_crowd and crowd == "medium":
                s += 15
            elif crowd == "low":
                s += 10
            # Traveler type match (10 pts)
            types = c.get("types", "")
            if traveler_type in types:
                s += 10
            c["_score"] = round(s, 2)
            return s

        candidates.sort(key=score, reverse=True)
        return candidates

    @staticmethod
    def _best_for_label(gem: dict, traveler_type: str) -> str:
        types = gem.get("types", traveler_type)
        if traveler_type in types:
            return f"Perfect for {traveler_type} travelers"
        return f"Suits {types.split(',')[0].strip() if types else 'all'} travelers"

    def _get_built_in(self, city: str, category: Optional[str] = None) -> list[HiddenGemOut]:
        city_key = city.lower().strip().split(",")[0].strip()
        gems = BUILT_IN_GEMS.get(city_key, [])
        results = []
        for g in gems:
            if category and g.get("category") != category.lower():
                continue
            results.append(HiddenGemOut(
                id="builtin", city=city,
                place_name=g["name"],
                category=g.get("category"),
                description=g.get("desc"),
                estimated_cost=g.get("cost"),
                crowd_level=g.get("crowd"),
                best_time_to_visit=g.get("best_time"),
                traveler_type=g.get("types"),
                recommended_for=g.get("types"),
                image_url=None,
                latitude=None, longitude=None,
                created_at=None, updated_at=None,
            ))
        return results

    @staticmethod
    def _get_built_in_raw(city: str) -> list[dict]:
        city_key = city.lower().strip().split(",")[0].strip()
        gems = BUILT_IN_GEMS.get(city_key, [])
        return [
            {
                "id": "builtin", "name": g["name"], "category": g.get("category"),
                "cost": g.get("cost", 0), "crowd": g.get("crowd", "low"),
                "best_time": g.get("best_time"), "desc": g.get("desc"),
                "types": g.get("types", ""), "tips": g.get("tips", []),
                "image_url": None,
            }
            for g in gems
        ]

    @staticmethod
    def _db_gem_to_dict(g: HiddenGem) -> dict:
        return {
            "id": str(g.id), "name": g.place_name, "category": g.category,
            "cost": float(g.estimated_cost) if g.estimated_cost else 0,
            "crowd": g.crowd_level or "low",
            "best_time": g.best_time_to_visit,
            "desc": g.description,
            "types": g.traveler_type or "",
            "tips": [], "image_url": g.image_url,
        }
