from utils.col_calculator import COST_OF_LIVING_DATA
from utils.tax_calculator import TAX_RATES, CITY_TO_STATE_MAPPING
from utils.market_data import LOCATION_SALARY_MULTIPLIERS
from utils.us_cities import MAJOR_US_CITIES

def get_all_locations():
    """
    Aggregate all unique locations from various data sources.
    Returns a sorted list of location strings.
    """
    locations = set()
    
    # Collect from static US city list
    locations.update(MAJOR_US_CITIES)
    
    # Collect from COL data
    locations.update(COST_OF_LIVING_DATA.keys())
    
    # Collect from Tax data (already handles states like 'San Francisco, CA')
    locations.update(TAX_RATES.keys())
    
    # Collect from Market Data
    locations.update(LOCATION_SALARY_MULTIPLIERS.keys())
    
    # Collect from CITY_TO_STATE_MAPPING values (this is the state-qualified string)
    locations.update(CITY_TO_STATE_MAPPING.values())
    
    # Collect raw city names from CITY_TO_STATE_MAPPING keys, using the mapped state
    for city_key, mapped_value in CITY_TO_STATE_MAPPING.items():
        # Avoid short aliases like "sf", "la", "nyc", "dc"
        if len(city_key) > 3 or city_key in ["ny"]: 
            # E.g., city_key="sunnyvale", mapped_value="San Jose, CA" -> "Sunnyvale, CA"
            try:
                state_abbr = mapped_value.split(',')[1].strip()
                proper_city = city_key.title()
                new_loc = f"{proper_city}, {state_abbr}"
                locations.add(new_loc)
            except IndexError:
                # If mapped value doesn't have a state comma (e.g., international)
                pass

    return sorted(list(locations))

if __name__ == "__main__":
    locs = get_all_locations()
    print(f"Found {len(locs)} locations")
    print(locs)
