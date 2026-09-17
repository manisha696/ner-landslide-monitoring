import os
import json
import math


# ============================================================
# PATH
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

LOOKUP_FILE = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "terrain_lookup.json"
)


# ============================================================
# LOAD TERRAIN DATA
# ============================================================

print()
print("==============================================")
print(" NER TERRAIN LOOKUP")
print("==============================================")
print()

if not os.path.exists(LOOKUP_FILE):
    raise FileNotFoundError(
        f"Terrain lookup not found:\n{LOOKUP_FILE}"
    )

with open(
    LOOKUP_FILE,
    "r",
    encoding="utf-8"
) as f:
    TERRAIN_DATA = json.load(f)

print(
    "Terrain locations loaded:",
    len(TERRAIN_DATA)
)

print()


# ============================================================
# FIND NEAREST TERRAIN LOCATION
# ============================================================

def find_nearest_terrain(lat, lon):

    nearest = None
    nearest_distance = float("inf")

    for point in TERRAIN_DATA.values():

        point_lat = point["latitude"]
        point_lon = point["longitude"]

        # Simple geographic distance
        distance = (
            (point_lat - lat) ** 2
            +
            (point_lon - lon) ** 2
        )

        if distance < nearest_distance:

            nearest_distance = distance
            nearest = point

    return nearest


# ============================================================
# GET TERRAIN
# ============================================================

def get_terrain(lat, lon):

    point = find_nearest_terrain(
        lat,
        lon
    )

    if point is None:

        raise ValueError(
            "No terrain data available "
            "for this location."
        )

    return {
        "elevation": float(
            point["elevation"]
        ),

        "slope": float(
            point["slope"]
        ),

        "aspect": float(
            point["aspect"]
        )
    }


# ============================================================
# FIND DEM TILE
# ============================================================
# Kept for compatibility with the existing project.
# The cloud backend will use the compact lookup instead.

def find_dem_tile(lat, lon):

    point = find_nearest_terrain(
        lat,
        lon
    )

    if point is None:
        return None

    return "terrain_lookup"


# ============================================================
# LOCAL TEST
# ============================================================

if __name__ == "__main__":

    test_lat = 25.5007
    test_lon = 93.9854

    print(
        "Testing location:",
        test_lat,
        test_lon
    )

    terrain = get_terrain(
        test_lat,
        test_lon
    )

    print()
    print("Terrain result:")
    print(
        json.dumps(
            terrain,
            indent=2
        )
    )

    print()
    print("Terrain lookup working.")