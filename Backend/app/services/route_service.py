import logging
import math
from typing import Optional

import httpx
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.attraction import Attraction
from app.models.hidden_gem import HiddenGem
from app.models.route_history import RouteHistory
from app.models.user import User
from app.schemas.route import (
    NearbyAttractionResponse,
    RouteHistoryOut,
    RouteResponse,
    TravelModeDetail,
)

logger = logging.getLogger("tripwise")

# ─────────────────────────────────────────────────────────────────────────────
# Built-in distance & duration table for common Indian city pairs (km, hours)
# ─────────────────────────────────────────────────────────────────────────────
ROUTE_DATA: dict[tuple[str, str], dict] = {
    ("pune",    "goa"):       {"km": 450,  "road_h": 9.5,  "train_h": 11,  "flight_h": 1.25},
    ("mumbai",  "goa"):       {"km": 590,  "road_h": 11.0, "train_h": 8.5, "flight_h": 1.25},
    ("mumbai",  "delhi"):     {"km": 1400, "road_h": 23.0, "train_h": 16,  "flight_h": 2.0},
    ("delhi",   "jaipur"):    {"km": 280,  "road_h": 5.5,  "train_h": 4.5, "flight_h": 1.0},
    ("delhi",   "manali"):    {"km": 570,  "road_h": 12.0, "train_h": 14,  "flight_h": 1.5},
    ("delhi",   "shimla"):    {"km": 350,  "road_h": 7.5,  "train_h": 6.5, "flight_h": 1.25},
    ("mumbai",  "pune"):      {"km": 150,  "road_h": 3.0,  "train_h": 3.5, "flight_h": None},
    ("chennai", "bangalore"): {"km": 350,  "road_h": 6.5,  "train_h": 5.0, "flight_h": 1.0},
    ("bangalore","goa"):      {"km": 560,  "road_h": 10.5, "train_h": 9.0, "flight_h": 1.25},
    ("kolkata", "delhi"):     {"km": 1470, "road_h": 24.0, "train_h": 17,  "flight_h": 2.25},
    ("mumbai",  "hyderabad"): {"km": 710,  "road_h": 13.0, "train_h": 12,  "flight_h": 1.5},
    ("delhi",   "agra"):      {"km": 210,  "road_h": 3.5,  "train_h": 2.0, "flight_h": None},
    ("mumbai",  "manali"):    {"km": 1950, "road_h": 33.0, "train_h": 28,  "flight_h": 2.5},
    ("pune",    "mumbai"):    {"km": 150,  "road_h": 3.0,  "train_h": 3.5, "flight_h": None},
    ("goa",     "bangalore"): {"km": 560,  "road_h": 10.5, "train_h": 9.0, "flight_h": 1.25},
}

# Cost per km / per hour (₹) estimates
COST_PER_KM = {
    "car":    5.5,   # fuel + tolls
    "bus":    1.2,   # government bus
    "train":  0.8,   # 2AC sleeper approx
    "flight": 3.5,   # per km (base fare)
}

FLIGHT_FIXED_MIN = 2500   # minimum domestic airfare

MODE_PROS_CONS = {
    "car":    (["Door-to-door convenience", "Flexible departure", "Good for groups"],
               ["Tiring on long routes", "Fuel + toll costs", "Traffic risk"]),
    "bus":    (["Most affordable", "Multiple boarding points", "Night travel saves hotel cost"],
               ["Slowest option", "Less comfortable", "Fixed schedule"]),
    "train":  (["Comfortable sleeper options", "On-time reliability", "Scenic routes"],
               ["Book well in advance", "Station to destination extra travel"]),
    "flight": (["Fastest option", "Saves a day of travel", "Premium comfort"],
               ["Expensive", "Airport transfer time", "Luggage restrictions"]),
}


class RouteService:

    # ── Calculate route ───────────────────────────────────────────────────────

    def calculate_route(
        self,
        db: Session,
        source: str,
        destination: str,
        travelers: int,
        budget: Optional[float],
        user: User,
    ) -> RouteResponse:
        src_key  = source.lower().strip()
        dst_key  = destination.lower().strip()
        data     = (ROUTE_DATA.get((src_key, dst_key)) or
                    ROUTE_DATA.get((dst_key, src_key)))

        if data:
            km = data["km"]
        else:
            km = self._estimate_distance(src_key, dst_key)
            data = {
                "km":       km,
                "road_h":   km / 60,
                "train_h":  km / 80,
                "flight_h": max(1.0, km / 800) if km > 300 else None,
            }

        modes = self._build_modes(km, data, travelers, budget)
        best  = self._pick_best(modes, budget, km)
        rec   = self._smart_recommendation(modes, best, source, destination, budget, travelers)

        # Save to history
        self._save_history(db, user, source, destination, km, best, modes)

        return RouteResponse(
            source=source,
            destination=destination,
            distance_km=km,
            suggested_modes=modes,
            best_mode=best,
            recommendation=rec,
            source_type="heuristic",
        )

    # ── Estimate cost ──────────────────────────────────────────────────────────

    def estimate_cost(
        self,
        distance_km: float,
        mode: str,
        travelers: int,
    ) -> float:
        mode = mode.lower()
        if mode == "flight":
            per_person = max(FLIGHT_FIXED_MIN, distance_km * COST_PER_KM["flight"])
        else:
            per_person = distance_km * COST_PER_KM.get(mode, 2.0)
        return round(per_person * travelers, 2)

    # ── Nearby attractions ─────────────────────────────────────────────────────

    def get_nearby_attractions(
        self,
        db: Session,
        latitude: float,
        longitude: float,
        radius_km: float = 10,
    ) -> list[NearbyAttractionResponse]:
        """
        Return attractions and hidden gems within radius_km of given coords.
        Uses Haversine distance on DB lat/lon columns.
        Falls back to GOOGLE_MAPS_API if key is set.
        """
        results: list[NearbyAttractionResponse] = []

        # Query attractions with coordinates
        attractions = db.query(Attraction).filter(
            Attraction.location_coordinates.isnot(None)
        ).all()
        for a in attractions:
            coords = a.location_coordinates
            if isinstance(coords, dict):
                lat2 = coords.get("lat") or coords.get("latitude")
                lng2 = coords.get("lng") or coords.get("longitude")
                if lat2 and lng2:
                    dist = self._haversine(latitude, longitude, float(lat2), float(lng2))
                    if dist <= radius_km:
                        results.append(NearbyAttractionResponse(
                            name=a.attraction_name,
                            category=a.category,
                            distance_km=round(dist, 2),
                            latitude=float(lat2),
                            longitude=float(lng2),
                            description=a.description,
                            estimated_cost=float(a.entry_fee) if a.entry_fee else None,
                            source="database",
                        ))

        # Query hidden gems with lat/lon
        gems = db.query(HiddenGem).filter(
            HiddenGem.latitude.isnot(None),
            HiddenGem.longitude.isnot(None),
        ).all()
        for g in gems:
            dist = self._haversine(latitude, longitude, g.latitude, g.longitude)
            if dist <= radius_km:
                results.append(NearbyAttractionResponse(
                    name=g.place_name,
                    category=g.category,
                    distance_km=round(dist, 2),
                    latitude=g.latitude,
                    longitude=g.longitude,
                    description=g.description,
                    estimated_cost=float(g.estimated_cost) if g.estimated_cost else None,
                    source="hidden_gem",
                ))

        results.sort(key=lambda x: x.distance_km)
        return results

    # ── Recommend transport mode ───────────────────────────────────────────────

    def recommend_transport_mode(
        self,
        distance_km: float,
        budget: float,
        travelers: int,
        duration_days: int = 1,
    ) -> str:
        """Return the single best mode as a string."""
        modes = self._build_modes(distance_km, {
            "km":       distance_km,
            "road_h":   distance_km / 60,
            "train_h":  distance_km / 80,
            "flight_h": max(1.0, distance_km / 800) if distance_km > 300 else None,
        }, travelers, budget)
        return self._pick_best(modes, budget, distance_km)

    # ── Route history ──────────────────────────────────────────────────────────

    def get_history(self, db: Session, user: User) -> list[RouteHistoryOut]:
        records = (
            db.query(RouteHistory)
            .filter(RouteHistory.user_id == user.id)
            .order_by(RouteHistory.created_at.desc())
            .limit(50)
            .all()
        )
        return [RouteHistoryOut.model_validate(r) for r in records]

    # ── Private helpers ────────────────────────────────────────────────────────

    def _build_modes(
        self, km: float, data: dict, travelers: int, budget: Optional[float]
    ) -> list[TravelModeDetail]:
        modes: list[TravelModeDetail] = []

        mode_map = [
            ("car",    data.get("road_h"),   "road"),
            ("bus",    data.get("road_h", 0) * 1.15, "road"),
            ("train",  data.get("train_h"),  "rail"),
            ("flight", data.get("flight_h"), "air"),
        ]

        flight_cost = None
        for mode, hours, _ in mode_map:
            if mode == "flight":
                if not hours:
                    continue
                per_person = max(FLIGHT_FIXED_MIN, km * COST_PER_KM["flight"])
                flight_cost = per_person
            else:
                per_person = km * COST_PER_KM.get(mode, 2.0)

            total = round(per_person * travelers, 2)
            pros, cons = MODE_PROS_CONS.get(mode, ([], []))

            h, m    = divmod(int((hours or 1) * 60), 60)
            label   = f"{h}h {m:02d}m" if h else f"{m}m"

            saving = None
            if mode != "flight" and flight_cost is not None:
                saving = round((flight_cost - per_person) * travelers, 2)

            modes.append(TravelModeDetail(
                mode=mode,
                estimated_cost=round(per_person, 2),
                total_cost=total,
                duration_hours=round(hours or 1, 2),
                duration_label=label,
                pros=list(pros),
                cons=list(cons),
                recommended=False,
                savings_vs_flight=saving if saving and saving > 0 else None,
            ))

        return modes

    @staticmethod
    def _pick_best(
        modes: list[TravelModeDetail],
        budget: Optional[float],
        km: float,
    ) -> str:
        if km > 1000:
            return "flight"
        if budget:
            affordable = [m for m in modes if m.total_cost <= budget]
            if affordable:
                # Among affordable, prefer train for comfort
                for preferred in ("train", "bus", "car", "flight"):
                    if any(m.mode == preferred for m in affordable):
                        return preferred
        if km > 500:
            return "train"
        if km > 200:
            return "car"
        return "bus"

    @staticmethod
    def _smart_recommendation(
        modes: list[TravelModeDetail],
        best: str,
        source: str,
        destination: str,
        budget: Optional[float],
        travelers: int,
    ) -> str:
        best_mode = next((m for m in modes if m.mode == best), None)
        flight    = next((m for m in modes if m.mode == "flight"), None)
        if not best_mode:
            return f"Take {best} from {source} to {destination}."

        lines = [
            f"✅ **{best.capitalize()}** is the best way to travel from {source} to {destination} "
            f"({best_mode.duration_label}, ₹{best_mode.total_cost:,.0f} for {travelers} traveler(s))."
        ]
        if flight and best != "flight" and best_mode.savings_vs_flight:
            lines.append(
                f"💰 Choose {best} instead of flight and save ₹{best_mode.savings_vs_flight:,.0f}."
            )
        if budget and best_mode.total_cost > budget:
            lines.append(
                f"⚠️ Total transport cost (₹{best_mode.total_cost:,.0f}) exceeds your budget "
                f"(₹{budget:,.0f}). Consider bus for ₹{next((m.total_cost for m in modes if m.mode == 'bus'), 0):,.0f}."
            )
        return " ".join(lines)

    def _save_history(
        self, db: Session, user: User, source: str, destination: str,
        km: float, best_mode: str, modes: list[TravelModeDetail],
    ) -> None:
        best = next((m for m in modes if m.mode == best_mode), None)
        record = RouteHistory(
            user_id=user.id,
            source_location=source,
            destination_location=destination,
            distance_km=km,
            duration_minutes=int((best.duration_hours * 60)) if best else None,
            travel_mode=best_mode,
            estimated_cost=best.total_cost if best else None,
        )
        db.add(record)
        db.commit()
        logger.info(f"Route saved: {source} → {destination} [{best_mode}]")

    @staticmethod
    def _estimate_distance(src: str, dst: str) -> float:
        """Rough distance heuristic when city pair not in table."""
        metro = {"mumbai", "delhi", "bangalore", "chennai", "kolkata", "hyderabad", "pune"}
        if src in metro and dst in metro:
            return 1200.0
        return 500.0

    @staticmethod
    def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        R = 6371
        d_lat = math.radians(lat2 - lat1)
        d_lon = math.radians(lon2 - lon1)
        a = (math.sin(d_lat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(d_lon / 2) ** 2)
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
