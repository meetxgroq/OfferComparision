from utils.location_registry import LOCATION_REGISTRY

MAJOR_US_CITIES = sorted(
    k for k, e in LOCATION_REGISTRY.items()
    if e.country == "United States" and k != "Remote"
)
