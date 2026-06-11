from dataclasses import dataclass, field


@dataclass
class RouteInfo:
    source: str
    destination: str
    estimated_flight_hours: float
    suggested_stopovers: list[str] = field(default_factory=list)
    transport_options: list[str] = field(default_factory=list)
    notes: str = ""


class RouteService:
    """
    Provides basic routing information between source and destination.
    In production, plug in a real flights/maps API (e.g. Google Maps, Amadeus).
    """

    def get_route_info(self, source: str, destination: str) -> RouteInfo:
        """
        Returns a RouteInfo object for the given source → destination pair.
        Currently returns a sensible placeholder; replace with real API call.
        """
        return RouteInfo(
            source=source,
            destination=destination,
            estimated_flight_hours=self._estimate_flight_hours(source, destination),
            suggested_stopovers=[],
            transport_options=["Direct Flight", "Connecting Flight", "Train + Flight"],
            notes=(
                f"Check live fares for {source} → {destination}. "
                "Book at least 6–8 weeks in advance for best prices."
            ),
        )

    @staticmethod
    def _estimate_flight_hours(source: str, destination: str) -> float:
        """
        Very rough estimate based on keyword matching.
        Replace with a real distance/duration API for accuracy.
        """
        intercontinental_pairs = [
            ("india", "usa"), ("india", "europe"), ("india", "australia"),
            ("india", "canada"), ("india", "uk"),
        ]
        src, dst = source.lower(), destination.lower()
        for a, b in intercontinental_pairs:
            if (a in src and b in dst) or (b in src and a in dst):
                return 14.0
        return 4.0  # regional default
