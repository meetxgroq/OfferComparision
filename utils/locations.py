from utils.location_registry import get_all_locations

if __name__ == "__main__":
    locs = get_all_locations()
    print(f"Found {len(locs)} locations")
