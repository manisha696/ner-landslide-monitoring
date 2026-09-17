// =====================================================
// NER LANDSLIDE RISK MONITORING
// HISTORICAL XGBOOST + LIVE AI RISK ENGINE
// =====================================================


// =====================================================
// 1. CREATE MAP
// =====================================================

const map = L.map("map").setView([25.5, 93.9], 7);


// =====================================================
// 2. OPENSTREETMAP
// =====================================================

L.tileLayer(
    "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    {
        maxZoom: 19,
        attribution: "© OpenStreetMap contributors"
    }
).addTo(map);


// =====================================================
// 3. VARIABLES
// =====================================================

let allLocations = [];
let markers = [];

let liveMarker = null;
let liveRequestInProgress = false;


// Flask API
const LIVE_API = "https://ner-landslide-monitoring-1.onrender.com";


// =====================================================
// 4. RISK COLOR
// =====================================================

function getColor(level) {

    level = level.toUpperCase();

    if (level.includes("VERY HIGH")) {
        return "#b91c1c";
    }

    if (level.includes("HIGH")) {
        return "#ea580c";
    }

    if (level.includes("MODERATE")) {
        return "#eab308";
    }

    if (level.includes("LOW")) {
        return "#16a34a";
    }

    return "#64748b";
}


// =====================================================
// 5. LOAD HISTORICAL MODEL DATA
// =====================================================

fetch("risk_data.json")

    .then(function(response) {

        if (!response.ok) {

            throw new Error(
                "risk_data.json could not be loaded"
            );

        }

        return response.json();

    })

    .then(function(data) {

        console.log(
            "Actual model data loaded:",
            data.length,
            "locations"
        );

        allLocations = data;

        showMarkers(allLocations);

        updateStatistics(allLocations);

    })

    .catch(function(error) {

        console.error(
            "ERROR:",
            error
        );

        alert(
            "Risk data could not be loaded.\n\n" +
            "Make sure risk_data.json is inside the same folder as index.html."
        );

    });


// =====================================================
// 6. SHOW HISTORICAL MARKERS
// =====================================================

function showMarkers(data) {

    // Remove previous historical markers

    markers.forEach(function(marker) {

        map.removeLayer(marker);

    });

    markers = [];


    // Add historical markers

    data.forEach(function(item) {

        const color =
            getColor(item.level);


        const marker =
            L.circleMarker(

                [item.lat, item.lng],

                {
                    radius: 7,

                    color: "#ffffff",

                    weight: 1.5,

                    fillColor: color,

                    fillOpacity: 0.85
                }

            );


        // ---------------------------------------------
        // TERRAIN VALUES
        // ---------------------------------------------

        const elevation =
            item.elevation !== null
                ? item.elevation.toFixed(1) + " m"
                : "Not available";


        const slope =
            item.slope !== null
                ? item.slope.toFixed(2) + "°"
                : "Not available";


        const aspect =
            item.aspect !== null
                ? item.aspect.toFixed(1) + "°"
                : "Not available";


        // ---------------------------------------------
        // HISTORICAL POPUP
        // ---------------------------------------------

        marker.bindPopup(`

            <div style="width:250px">

                <h3 style="
                    margin-top:0;
                    margin-bottom:10px;
                ">
                    Landslide Risk Prediction
                </h3>


                <div style="
                    background:${color};
                    color:white;
                    padding:9px;
                    border-radius:6px;
                    text-align:center;
                    font-weight:bold;
                    margin-bottom:12px;
                ">

                    ${item.level}

                </div>


                <p>
                    <b>Risk Score:</b>
                    ${item.risk}
                </p>


                <p>
                    <b>Latitude:</b>
                    ${item.lat.toFixed(5)}
                </p>


                <p>
                    <b>Longitude:</b>
                    ${item.lng.toFixed(5)}
                </p>


                <hr>


                <p>
                    <b>7-Day Rainfall:</b>
                    ${item.rain7} mm
                </p>


                <p>
                    <b>30-Day Rainfall:</b>
                    ${item.rain30} mm
                </p>


                <p>
                    <b>Elevation:</b>
                    ${elevation}
                </p>


                <p>
                    <b>Slope:</b>
                    ${slope}
                </p>


                <p>
                    <b>Aspect:</b>
                    ${aspect}
                </p>


                <hr>


                <small>
                    Historical prediction generated using
                    the XGBoost landslide-risk model.
                </small>

            </div>

        `);


        marker.addTo(map);

        markers.push(marker);

    });


    // ---------------------------------------------
    // FIT MAP TO DATA
    // ---------------------------------------------

    if (data.length > 0) {

        const bounds =
            L.latLngBounds(

                data.map(function(item) {

                    return [
                        item.lat,
                        item.lng
                    ];

                })

            );


        map.fitBounds(
            bounds,
            {
                padding: [30, 30]
            }
        );

    }

}


// =====================================================
// 7. FILTER FUNCTIONS
// =====================================================

function showAll() {

    showMarkers(allLocations);

    updateStatistics(allLocations);

}


function showLow() {

    const filtered =
        allLocations.filter(

            function(item) {

                return item.level
                    .toUpperCase()
                    .includes("LOW");

            }

        );


    showMarkers(filtered);

    updateStatistics(filtered);

}


function showModerate() {

    const filtered =
        allLocations.filter(

            function(item) {

                return item.level
                    .toUpperCase()
                    .includes("MODERATE");

            }

        );


    showMarkers(filtered);

    updateStatistics(filtered);

}


function showHigh() {

    const filtered =
        allLocations.filter(

            function(item) {

                return item.level
                    .toUpperCase() === "HIGH";

            }

        );


    showMarkers(filtered);

    updateStatistics(filtered);

}


function showVeryHigh() {

    const filtered =
        allLocations.filter(

            function(item) {

                return item.level
                    .toUpperCase()
                    .includes("VERY HIGH");

            }

        );


    showMarkers(filtered);

    updateStatistics(filtered);

}


// =====================================================
// 8. STATISTICS
// =====================================================

function updateStatistics(data) {

    const total =
        data.length;


    const low =
        data.filter(function(item) {

            return item.level
                .toUpperCase()
                .includes("LOW");

        }).length;


    const moderate =
        data.filter(function(item) {

            return item.level
                .toUpperCase()
                .includes("MODERATE");

        }).length;


    const high =
        data.filter(function(item) {

            return item.level
                .toUpperCase() === "HIGH";

        }).length;


    const veryHigh =
        data.filter(function(item) {

            return item.level
                .toUpperCase()
                .includes("VERY HIGH");

        }).length;


    document.getElementById("totalCount")
        .textContent = total;


    document.getElementById("lowCount")
        .textContent = low;


    document.getElementById("moderateCount")
        .textContent = moderate;


    document.getElementById("highCount")
        .textContent = high;


    document.getElementById("veryHighCount")
        .textContent = veryHigh;


    console.log(
        "Risk Summary:",
        {
            total,
            low,
            moderate,
            high,
            veryHigh
        }
    );

}


// =====================================================
// 9. LEGEND
// =====================================================

const legend =
    L.control({
        position: "bottomright"
    });


legend.onAdd =
    function() {

        const div =
            L.DomUtil.create(
                "div",
                "legend"
            );


        div.innerHTML = `

            <div class="legend-title">
                Landslide Risk
            </div>


            <div class="legend-item">

                <span
                    class="legend-dot low">
                </span>

                Low

            </div>


            <div class="legend-item">

                <span
                    class="legend-dot moderate">
                </span>

                Moderate

            </div>


            <div class="legend-item">

                <span
                    class="legend-dot high">
                </span>

                High

            </div>


            <div class="legend-item">

                <span
                    class="legend-dot very-high">
                </span>

                Very High

            </div>


            <div style="
                margin-top:8px;
                padding-top:8px;
                border-top:1px solid #ddd;
                font-size:11px;
            ">

                Click map for LIVE AI risk

            </div>

        `;


        return div;

    };


legend.addTo(map);


// =====================================================
// 10. LIVE RISK FUNCTION
// =====================================================

async function getLiveRisk(lat, lon) {

    if (liveRequestInProgress) {

        console.log(
            "Live risk request already running."
        );

        return;

    }


    liveRequestInProgress = true;


    // Remove previous live marker

    if (liveMarker !== null) {

        map.removeLayer(liveMarker);

        liveMarker = null;

    }


    // Temporary loading marker

    const loadingMarker =
        L.circleMarker(

            [lat, lon],

            {
                radius: 10,
                color: "#2563eb",
                fillColor: "#60a5fa",
                fillOpacity: 0.8,
                weight: 3
            }

        ).addTo(map);


    loadingMarker
        .bindPopup(`
            <div style="
                width:240px;
                text-align:center;
                padding:8px;
            ">

                <h3 style="
                    margin-top:0;
                ">
                    Checking Live Risk
                </h3>

                <p>
                    Fetching current weather,
                    terrain and XGBoost prediction...
                </p>

            </div>
        `)
        .openPopup();


    try {

        const url =
            LIVE_API +
            "/live-risk" +
            "?lat=" +
            encodeURIComponent(lat) +
            "&lon=" +
            encodeURIComponent(lon);


        console.log(
            "Requesting live risk:",
            url
        );


        const response =
            await fetch(url);


        const result =
            await response.json();


        if (!response.ok) {

            throw new Error(
                result.error ||
                "Live risk API failed."
            );

        }


        console.log(
            "LIVE RISK RESULT:",
            result
        );


        // Remove loading marker

        map.removeLayer(
            loadingMarker
        );


        // ---------------------------------------------
        // RESULT VALUES
        // ---------------------------------------------

        const risk =
            Number(result.risk_percent);


        const level =
            result.risk_level ||
            "UNKNOWN";


        const color =
            getColor(level);


        const weather =
            result.weather || {};


        const terrain =
            result.terrain || {};


        // ---------------------------------------------
        // CREATE LIVE MARKER
        // ---------------------------------------------

        liveMarker =
            L.circleMarker(

                [lat, lon],

                {
                    radius: 12,

                    color: "#ffffff",

                    weight: 4,

                    fillColor: color,

                    fillOpacity: 0.95
                }

            );


        // ---------------------------------------------
        // LIVE POPUP
        // ---------------------------------------------

        liveMarker.bindPopup(`

            <div style="
                width:290px;
                font-family:Arial,sans-serif;
            ">

                <div style="
                    background:#0f766e;
                    color:white;
                    padding:8px 10px;
                    border-radius:7px;
                    margin-bottom:12px;
                    font-size:12px;
                    font-weight:bold;
                    text-align:center;
                ">

                    LIVE AI RISK ANALYSIS

                </div>


                <h3 style="
                    margin:0 0 10px 0;
                ">

                    Current Landslide Risk

                </h3>


                <div style="
                    background:${color};
                    color:white;
                    padding:12px;
                    border-radius:8px;
                    text-align:center;
                    margin-bottom:12px;
                ">

                    <div style="
                        font-size:24px;
                        font-weight:bold;
                    ">

                        ${risk.toFixed(2)}%

                    </div>


                    <div style="
                        font-size:13px;
                        margin-top:3px;
                    ">

                        ${level}

                    </div>

                </div>


                <p>
                    <b>Latitude:</b>
                    ${lat.toFixed(5)}
                </p>


                <p>
                    <b>Longitude:</b>
                    ${lon.toFixed(5)}
                </p>


                <hr>


                <h4 style="
                    margin-bottom:7px;
                ">
                    LIVE WEATHER
                </h4>


                <p>
                    <b>Rainfall 1 Day:</b>
                    ${Number(weather.rain_1d_mm || 0).toFixed(2)} mm
                </p>


                <p>
                    <b>Rainfall 3 Days:</b>
                    ${Number(weather.rain_3d_mm || 0).toFixed(2)} mm
                </p>


                <p>
                    <b>Rainfall 7 Days:</b>
                    ${Number(weather.rain_7d_mm || 0).toFixed(2)} mm
                </p>


                <p>
                    <b>Rainfall 14 Days:</b>
                    ${Number(weather.rain_14d_mm || 0).toFixed(2)} mm
                </p>


                <p>
                    <b>Rainfall 30 Days:</b>
                    ${Number(weather.rain_30d_mm || 0).toFixed(2)} mm
                </p>


                <p>
                    <b>Temperature:</b>
                    ${Number(weather.temperature_C || 0).toFixed(1)} °C
                </p>


                <p>
                    <b>Humidity:</b>
                    ${Number(weather.humidity_percent || 0).toFixed(1)}%
                </p>


                <p>
                    <b>Wind:</b>
                    ${Number(weather.wind_speed_mps || 0).toFixed(2)} m/s
                </p>


                <hr>


                <h4 style="
                    margin-bottom:7px;
                ">
                    REAL TERRAIN
                </h4>


                <p>
                    <b>Elevation:</b>
                    ${Number(terrain.elevation || 0).toFixed(1)} m
                </p>


                <p>
                    <b>Slope:</b>
                    ${Number(terrain.slope || 0).toFixed(2)}°
                </p>


                <p>
                    <b>Aspect:</b>
                    ${Number(terrain.aspect || 0).toFixed(2)}°
                </p>


                <hr>


                <div style="
                    background:#f0fdfa;
                    border-left:4px solid #0f766e;
                    padding:8px;
                    font-size:12px;
                    line-height:1.5;
                ">

                    <b>AI Risk Estimate</b>

                    <br>

                    This score combines live weather,
                    SRTM terrain and the trained
                    XGBoost landslide-risk model.

                </div>


                <p style="
                    font-size:10px;
                    color:#64748b;
                    margin-bottom:0;
                ">

                    Prototype decision-support system.
                    Not an official evacuation warning.

                </p>

            </div>

        `);


        liveMarker.addTo(map);


        liveMarker.openPopup();


    }

    catch (error) {

        console.error(
            "LIVE RISK ERROR:",
            error
        );


        map.removeLayer(
            loadingMarker
        );


        L.popup()
            .setLatLng([lat, lon])
            .setContent(`

                <div style="
                    width:230px;
                ">

                    <h3 style="
                        color:#b91c1c;
                    ">
                        Live Risk Error
                    </h3>

                    <p>
                        Unable to calculate live
                        landslide risk.
                    </p>

                    <small>
                        ${error.message}
                    </small>

                </div>

            `)
            .openOn(map);

    }


    finally {

        liveRequestInProgress =
            false;

    }

}


// =====================================================
// 11. MAP CLICK → LIVE AI RISK
// =====================================================

map.on(
    "click",
    function(event) {

        const lat =
            event.latlng.lat;

        const lon =
            event.latlng.lng;


        console.log(
            "Map clicked:",
            lat,
            lon
        );


        getLiveRisk(
            lat,
            lon
        );

    }
);


// =====================================================
// 12. DANGER ZONE
// =====================================================

const dangerZone =
    L.polygon(

        [
            [25.70, 93.70],
            [25.70, 94.30],
            [25.25, 94.30],
            [25.25, 93.70]
        ],

        {
            color: "#b91c1c",
            fillColor: "#ef4444",
            fillOpacity: 0.08,
            weight: 2
        }

    ).addTo(map);


dangerZone.bindPopup(`

    <div style="width:220px">

        <h3 style="color:#b91c1c">
            High-Risk Monitoring Zone
        </h3>

        <p>
            Area highlighted for prototype
            landslide-risk monitoring.
        </p>

        <small>
            This is a demonstration boundary
            and is not an official evacuation zone.
        </small>

    </div>

`);


// =====================================================
// 13. SAFE ZONE
// =====================================================

const safeZone =
    L.polygon(

        [
            [26.15, 91.65],
            [26.15, 91.80],
            [26.05, 91.80],
            [26.05, 91.65]
        ],

        {
            color: "#15803d",
            fillColor: "#22c55e",
            fillOpacity: 0.15,
            weight: 2
        }

    ).addTo(map);


safeZone.bindPopup(`

    <div style="width:220px">

        <h3 style="color:#15803d">
            Prototype Safe Zone
        </h3>

        <p>
            Demonstration area for
            evacuation planning.
        </p>

        <small>
            Verify official shelters and
            evacuation routes before real-world use.
        </small>

    </div>

`);


// =====================================================
// 14. LOCATION SEARCH
// =====================================================

async function searchLocation() {

    const input =
        document.getElementById(
            "locationSearch"
        );


    const locationName =
        input.value.trim();


    if (locationName === "") {

        alert(
            "Please enter a location."
        );

        return;

    }


    try {

        const url =
            "https://nominatim.openstreetmap.org/search" +
            "?format=json" +
            "&limit=1" +
            "&q=" +
            encodeURIComponent(
                locationName
            );


        const response =
            await fetch(
                url,
                {
                    headers: {
                        "Accept":
                            "application/json"
                    }
                }
            );


        const results =
            await response.json();


        if (results.length === 0) {

            alert(
                "Location not found."
            );

            return;

        }


        const latitude =
            parseFloat(
                results[0].lat
            );


        const longitude =
            parseFloat(
                results[0].lon
            );


        map.setView(
            [
                latitude,
                longitude
            ],
            12
        );


        L.marker(
            [
                latitude,
                longitude
            ]
        )
        .addTo(map)
        .bindPopup(
            `<b>${locationName}</b><br><br>
             Click this location on the map
             to calculate LIVE AI risk.`
        )
        .openPopup();


    }

    catch (error) {

        console.error(
            "Location search error:",
            error
        );


        alert(
            "Unable to search location."
        );

    }

}


// =====================================================
// 15. MAKE FILTER BUTTONS AVAILABLE
// =====================================================

window.showAll =
    showAll;

window.showLow =
    showLow;

window.showModerate =
    showModerate;

window.showHigh =
    showHigh;

window.showVeryHigh =
    showVeryHigh;


// =====================================================
// 16. INITIALIZATION
// =====================================================

console.log(
    "NER Landslide GIS initialized."
);

console.log(
    "LIVE AI Risk Engine:",
    LIVE_API
);