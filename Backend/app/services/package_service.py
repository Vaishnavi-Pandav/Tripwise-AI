import json
import logging
import math
from dataclasses import dataclass
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.package import TravelPackage
from app.models.trip import Trip
from app.schemas.package import (
    PackageCompareItem,
    PackageCompareOut,
    PackageCreate,
    PackageListResponse,
    PackageRecommendationOut,
    PackageRecommendationsOut,
    PackageUpdate,
)

logger = logging.getLogger("tripwise")


# ── Scoring weights ────────────────────────────────────────────────────────────

WEIGHTS = {
    "budget_match":    0.40,
    "rating":          0.30,
    "duration_match":  0.20,
    "popularity":      0.10,
}

# Popularity proxy — packages with more inclusions are "more popular"
MAX_INCLUSIONS_FOR_SCORE = 8


@dataclass
class PackageScoreBreakdown:
    budget_match:   float
    rating:         float
    duration_match: float
    popularity:     float
    total:          float


# ── Service ────────────────────────────────────────────────────────────────────

class PackageService:

    # ── CRUD ──────────────────────────────────────────────────────────────────

    @staticmethod
    def create_package(db: Session, payload: PackageCreate) -> TravelPackage:
        data = payload.model_dump()
        for field in ("inclusions", "exclusions"):
            if data.get(field) is not None:
                data[field] = json.dumps(data[field])
        pkg = TravelPackage(**data)
        db.add(pkg)
        db.commit()
        db.refresh(pkg)
        logger.info(f"Package created: {pkg.id} — {pkg.package_name}")
        return pkg

    @staticmethod
    def update_package(db: Session, package_id: str, payload: PackageUpdate) -> TravelPackage:
        pkg = PackageService.get_package(db, package_id)
        data = payload.model_dump(exclude_unset=True)
        for field in ("inclusions", "exclusions"):
            if field in data and data[field] is not None:
                data[field] = json.dumps(data[field])
        for field, value in data.items():
            setattr(pkg, field, value)
        db.commit()
        db.refresh(pkg)
        logger.info(f"Package updated: {package_id}")
        return pkg

    @staticmethod
    def delete_package(db: Session, package_id: str) -> None:
        pkg = PackageService.get_package(db, package_id)
        db.delete(pkg)
        db.commit()
        logger.info(f"Package deleted: {package_id}")

    @staticmethod
    def get_package(db: Session, package_id: str) -> TravelPackage:
        pkg = db.query(TravelPackage).filter(TravelPackage.id == package_id).first()
        if not pkg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Package {package_id} not found",
            )
        return pkg

    @staticmethod
    def get_packages(
        db: Session,
        destination: Optional[str] = None,
        package_type: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        duration_days: Optional[int] = None,
        min_rating: Optional[float] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> PackageListResponse:
        q = db.query(TravelPackage)

        if destination:
            q = q.filter(TravelPackage.destination.ilike(f"%{destination}%"))
        if package_type:
            q = q.filter(TravelPackage.package_type == package_type.lower())
        if min_price is not None:
            q = q.filter(TravelPackage.price >= min_price)
        if max_price is not None:
            q = q.filter(TravelPackage.price <= max_price)
        if duration_days is not None:
            q = q.filter(TravelPackage.duration_days == duration_days)
        if min_rating is not None:
            q = q.filter(TravelPackage.rating >= min_rating)

        total       = q.count()
        total_pages = max(1, math.ceil(total / page_size))
        packages    = (
            q.order_by(TravelPackage.rating.desc().nulls_last(), TravelPackage.price)
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return PackageListResponse(
            packages=packages,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    # ── Recommendation engine ─────────────────────────────────────────────────

    @staticmethod
    def recommend_packages(
        db: Session,
        trip_id: str,
        top_n: int = 5,
    ) -> PackageRecommendationsOut:
        """
        Score all packages matching the trip destination and return top N.

        Scoring (out of 100):
          40% Budget Match   — how well package price fits trip budget
          30% Rating         — normalised 0–5 star rating
          20% Duration Match — how closely duration matches trip days
          10% Popularity     — proxy via number of inclusions
        """
        trip: Optional[Trip] = db.query(Trip).filter(Trip.id == trip_id).first()
        if not trip:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trip not found",
            )

        packages = db.query(TravelPackage).filter(
            TravelPackage.destination.ilike(f"%{trip.destination_location}%")
        ).all()

        if not packages:
            return PackageRecommendationsOut(
                trip_id=str(trip.id),
                destination=trip.destination_location,
                trip_budget=float(trip.budget),
                trip_days=trip.number_of_days,
                recommended_packages=[],
                total_found=0,
            )

        scored: list[tuple[TravelPackage, PackageScoreBreakdown]] = []
        for pkg in packages:
            bd = PackageService._score_package(pkg, float(trip.budget), trip.number_of_days)
            scored.append((pkg, bd))

        scored.sort(key=lambda x: x[1].total, reverse=True)
        top = scored[:top_n]

        results = []
        for pkg, bd in top:
            results.append(
                PackageRecommendationOut(
                    package_id=str(pkg.id),
                    package_name=pkg.package_name,
                    agency_name=pkg.agency_name,
                    destination=pkg.destination,
                    duration_days=pkg.duration_days,
                    price=float(pkg.price),
                    package_type=pkg.package_type,
                    rating=pkg.rating,
                    inclusions=pkg.inclusions_list(),
                    image_url=pkg.image_url,
                    recommendation_score=round(bd.total, 2),
                    score_breakdown={
                        "budget_match":   round(bd.budget_match, 2),
                        "rating":         round(bd.rating, 2),
                        "duration_match": round(bd.duration_match, 2),
                        "popularity":     round(bd.popularity, 2),
                    },
                )
            )

        return PackageRecommendationsOut(
            trip_id=str(trip.id),
            destination=trip.destination_location,
            trip_budget=float(trip.budget),
            trip_days=trip.number_of_days,
            recommended_packages=results,
            total_found=len(packages),
        )

    # ── Compare packages ──────────────────────────────────────────────────────

    @staticmethod
    def compare_packages(db: Session, package_ids: list[str]) -> PackageCompareOut:
        """Compare 2–5 packages side by side."""
        packages = []
        for pid in package_ids:
            packages.append(PackageService.get_package(db, pid))

        # Build compare items
        items: list[PackageCompareItem] = []
        for pkg in packages:
            incl = pkg.inclusions_list()
            excl = pkg.exclusions_list()
            rating = pkg.rating or 3.0
            # Value score = rating / log(price+1) * duration
            import math as m
            value = round((rating / m.log(float(pkg.price) + 1)) * pkg.duration_days, 4)
            items.append(PackageCompareItem(
                package_id=str(pkg.id),
                package_name=pkg.package_name,
                agency_name=pkg.agency_name,
                destination=pkg.destination,
                duration_days=pkg.duration_days,
                price=float(pkg.price),
                package_type=pkg.package_type,
                rating=pkg.rating,
                inclusions=incl,
                exclusions=excl,
                value_score=value,
            ))

        # Analysis
        cheapest      = min(items, key=lambda x: x.price).package_name
        highest_rated = max(items, key=lambda x: x.rating or 0).package_name
        best_duration = max(items, key=lambda x: x.duration_days).package_name
        best_value    = max(items, key=lambda x: x.value_score).package_name

        prices = [i.price for i in items]
        price_diff = round(max(prices) - min(prices), 2)

        # Common inclusions
        if items:
            sets = [set(i.inclusions) for i in items]
            common = list(sets[0].intersection(*sets[1:]))
            unique_to_each = {
                i.package_name: list(set(i.inclusions) - set(common))
                for i in items
            }
        else:
            common, unique_to_each = [], {}

        recommendation = (
            f"**Best Value:** {best_value} offers the best combination of price, "
            f"duration and rating. "
            f"**Cheapest:** {cheapest}. "
            f"**Highest Rated:** {highest_rated}. "
            f"Price difference between cheapest and most expensive: ₹{price_diff:,.0f}."
        )

        return PackageCompareOut(
            packages=items,
            cheapest=cheapest,
            highest_rated=highest_rated,
            best_duration_match=best_duration,
            best_value=best_value,
            recommendation=recommendation,
            price_difference=price_diff,
            common_inclusions=common,
            unique_to_each=unique_to_each,
        )

    # ── Scoring helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _score_package(
        pkg: TravelPackage,
        trip_budget: float,
        trip_days: int,
    ) -> PackageScoreBreakdown:
        price = float(pkg.price)

        # 1. Budget match (40%)
        if trip_budget <= 0:
            bm_raw = 0.5
        else:
            ratio = price / trip_budget
            if ratio <= 0.8:
                bm_raw = 0.9                   # slightly under budget — good
            elif ratio <= 1.0:
                bm_raw = 1.0                   # within budget — perfect
            elif ratio <= 1.2:
                bm_raw = 1.0 - (ratio - 1.0) * 2   # 0–20% over — linear penalty
            else:
                bm_raw = max(0.0, 1.5 - ratio)  # steep penalty beyond 20%
        budget_score = min(bm_raw, 1.0) * 100 * WEIGHTS["budget_match"]

        # 2. Rating (30%)
        rating = float(pkg.rating) if pkg.rating else 3.0
        rating_score = (rating / 5.0) * 100 * WEIGHTS["rating"]

        # 3. Duration match (20%) — prefer packages closest to trip_days
        if trip_days <= 0:
            dur_raw = 0.5
        else:
            diff_ratio = abs(pkg.duration_days - trip_days) / trip_days
            dur_raw = max(0.0, 1.0 - diff_ratio)
        duration_score = dur_raw * 100 * WEIGHTS["duration_match"]

        # 4. Popularity — proxy via inclusions count (10%)
        inclusion_count = len(pkg.inclusions_list())
        pop_raw = min(inclusion_count / MAX_INCLUSIONS_FOR_SCORE, 1.0)
        popularity_score = pop_raw * 100 * WEIGHTS["popularity"]

        total = round(
            budget_score + rating_score + duration_score + popularity_score, 2
        )
        return PackageScoreBreakdown(
            budget_match=budget_score,
            rating=rating_score,
            duration_match=duration_score,
            popularity=popularity_score,
            total=min(total, 100.0),
        )

    # ── Backwards compat aliases ──────────────────────────────────────────────
    create         = staticmethod(lambda *a, **kw: PackageService.create_package(*a, **kw))
    update         = staticmethod(lambda *a, **kw: PackageService.update_package(*a, **kw))
    delete         = staticmethod(lambda *a, **kw: PackageService.delete_package(*a, **kw))
    get_by_id      = staticmethod(lambda *a, **kw: PackageService.get_package(*a, **kw))
    get_all        = staticmethod(lambda *a, **kw: PackageService.get_packages(*a, **kw).packages)
    get_by_destination = staticmethod(
        lambda db, dest: PackageService.get_packages(db, destination=dest).packages
    )
