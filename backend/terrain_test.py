import os
import json
import math


# =========================================================
# PATH
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

LOOKUP_FILE = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "terrain_lookup.json"
)


# =========================================================
# LOAD TERRAIN LOOKUP
# =========================================================

print("")
print("==============================================")
print("NER TERRAIN LOOKUP")
print("==============================================")

print(
    f"Loading terrain lookup from: {LOOKUP_FILE}",
    flush=True
)

with open(
    LOOKUP_FILE,
    "r"
) as f:

    TERRAIN_DATA = json.load(f)


print(
    f"Terrain locations loaded: {len(TERRAIN_DATA)}",
    flush=True
)


# =========================================================
# FAST TERRAIN LOOKUP
# =========================================================

def get_terrain(lat, lon):

    print("")
    print("----------------------------------------------")
    print("TERRAIN LOOKUP START")
    print("----------------------------------------------")

    print(
        f"Requested location: {lat}, {lon}",
        flush=True
    )


    # -----------------------------------------------------
    # YOUR TERRAIN GRID USES 2 DECIMAL PLACES
    # -----------------------------------------------------

    base_lat = round(
        lat,
        2
    )

    base_lon = round(
        lon,
        2
    )


    print(
        f"Grid location: {base_lat}, {base_lon}",
        flush=True
    )


    # -----------------------------------------------------
    # CHECK SMALL 5 x 5 NEIGHBORHOOD
    #
    # This checks only 25 points instead of 602,000.
    # -----------------------------------------------------

    nearest = None

    nearest_distance = float(
        "inf"
    )


    grid_step = 0.01


    for lat_offset in range(
        -2,
        3
    ):

        for lon_offset in range(
            -2,
            3
        ):

            candidate_lat = round(
                base_lat
                +
                lat_offset * grid_step,
                2
            )

            candidate_lon = round(
                base_lon
                +
                lon_offset * grid_step,
                2
            )


            key = (
                f"{candidate_lat:.2f},"
                f"{candidate_lon:.2f}"
            )


            point = TERRAIN_DATA.get(
                key
            )


            if point is None:

                continue


            # -------------------------------------------------
            # DISTANCE
            # -------------------------------------------------

            d_lat = (
                lat
                -
                float(
                    point["latitude"]
                )
            )

            d_lon = (
                lon
                -
                float(
                    point["longitude"]
                )
            )

            distance = (
                d_lat * d_lat
                +
                d_lon * d_lon
            )


            if distance < nearest_distance:

                nearest_distance = distance

                nearest = point


    # =====================================================
    # FALLBACK
    # =====================================================

    if nearest is None:

        print(
            "Nearby terrain point not found.",
            flush=True
        )

        print(
            "Trying exact rounded coordinate...",
            flush=True
        )


        key = (
            f"{base_lat:.2f},"
            f"{base_lon:.2f}"
        )


        nearest = TERRAIN_DATA.get(
            key
        )


    # =====================================================
    # NO DATA
    # =====================================================

    if nearest is None:

        print(
            "WARNING: No terrain data available.",
            flush=True
        )

        return {

            "elevation": 0.0,

            "slope": 0.0,

            "aspect": 0.0

        }


    # =====================================================
    # RESULT
    # =====================================================

    elevation = float(
        nearest.get(
            "elevation",
            0.0
        )
    )

    slope = float(
        nearest.get(
            "slope",
            0.0
        )
    )

    aspect = float(
        nearest.get(
            "aspect",
            0.0
        )
    )


    print(
        f"Elevation: {elevation}",
        flush=True
    )

    print(
        f"Slope: {slope}",
        flush=True
    )

    print(
        f"Aspect: {aspect}",
        flush=True
    )

    print(
        "TERRAIN LOOKUP COMPLETE",
        flush=True
    )


    return {

        "elevation": elevation,

        "slope": slope,

        "aspect": aspect

    }


# =========================================================
# LOCAL TEST
# =========================================================

if __name__ == "__main__":

    result = get_terrain(
        25.5007,
        93.9854
    )

    print("")
    print("==============================================")
    print("TEST RESULT")
    print("==============================================")

    print(
        result
    )