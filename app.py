from flask import Flask
import csv

app = Flask(__name__)

@app.route("/")
def home():

    # =========================
    # READ REALTIME STATUS
    # =========================

    try:

        with open("traffic_status.txt", "r") as file:

            data = file.read().split(",")

            vehicles = data[0]
            traffic = data[1]
            speed = data[2]
            prediction = data[3]

    except:

        vehicles = "0"
        traffic = "UNKNOWN"
        speed = "UNKNOWN"
        prediction = "NO DATA"

    # =========================
    # READ CSV DATA
    # =========================

    vehicle_history = []

    try:

        with open("traffic_data.csv", "r") as csvfile:

            reader = csv.reader(csvfile)

            next(reader)

            for row in reader:

                vehicle_history.append(int(row[1]))

    except:

        vehicle_history = [0]

    vehicle_history = vehicle_history[-10:]

    labels = list(range(1, len(vehicle_history) + 1))

    # =========================
    # TRAFFIC COLOR
    # =========================

    if traffic == "LOW":

        traffic_color = "green"

    elif traffic == "MEDIUM":

        traffic_color = "orange"

    else:

        traffic_color = "red"

    return f"""

    <html>

    <head>

    <meta name="viewport" content="width=device-width, initial-scale=1">

    <title>Traffic Intelligence System</title>

    <meta http-equiv="refresh" content="2">

    <!-- Leaflet -->

    <link
        rel="stylesheet"
        href="https://unpkg.com/leaflet/dist/leaflet.css"
    />

    <!-- Bootstrap -->

    <link
        href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css"
        rel="stylesheet"
    >

    <!-- Leaflet JS -->

    <script
        src="https://unpkg.com/leaflet/dist/leaflet.js">
    </script>

    <!-- Chart JS -->

    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

    <style>

    body{{
        background-color:#111827;
        color:white;
        font-family:Arial;
        padding:20px;
    }}

    h1{{
        color:#00ffcc;
        font-weight:bold;
    }}

    h2{{
        margin-top:10px;
        margin-bottom:20px;
    }}

    .dashboard{{
        display:grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap:20px;
        margin-top:20px;
    }}

    .card{{
        background:#1f2937;
        padding:20px;
        border-radius:20px;
        box-shadow:0 0 15px rgba(0,0,0,0.5);
        transition:0.3s;
    }}

    .card:hover{{
        transform:scale(1.03);
    }}

    .big{{
        font-size:42px;
        font-weight:bold;
        margin-top:10px;
    }}

    #map{{
        height:70vh;
        margin-top:30px;
        border-radius:20px;
        overflow:hidden;
    }}

    #chart-container{{
        background:#1f2937;
        margin-top:30px;
        padding:20px;
        border-radius:20px;
    }}

    canvas{{
        background:#111827;
        border-radius:10px;
        padding:10px;
    }}

    @media(max-width:768px){{

        h1{{
            font-size:32px;
        }}

        .big{{
            font-size:32px;
        }}

        #map{{
            height:60vh;
        }}
    }}

    </style>

    </head>

    <body class="container-fluid">

    <div class="mt-3 mb-4">

        <h1>🚦 Traffic Intelligence System</h1>

        <h2>Realtime AI Smart Traffic Monitoring</h2>

    </div>

    <!-- DASHBOARD -->

    <div class="dashboard">

        <div class="card">

            <h3>🚗 Vehicles</h3>

            <div class="big">{vehicles}</div>

        </div>

        <div class="card">

            <h3>🚦 Traffic</h3>

            <div class="big">{traffic}</div>

        </div>

        <div class="card">

            <h3>⚡ Speed</h3>

            <div class="big">{speed}</div>

        </div>

        <div class="card">

            <h3>🧠 Prediction</h3>

            <div class="big">{prediction}</div>

        </div>

    </div>

    <!-- MAP -->

    <div id="map"></div>

    <!-- CHART -->

    <div id="chart-container">

        <h2>📈 Realtime Traffic Analytics</h2>

        <canvas id="trafficChart"></canvas>

    </div>

    <script>

    // =========================
    // MAP
    // =========================

    var map = L.map('map').setView([10.7769, 106.7009], 13);

    L.tileLayer(
        'https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png',
        {{
            maxZoom: 19
        }}
    ).addTo(map);

    // MAIN ZONE

    var circle = L.circle(
        [10.7769, 106.7009],
        {{
            color: '{traffic_color}',
            fillColor: '{traffic_color}',
            fillOpacity: 0.5,
            radius: 500
        }}
    ).addTo(map);

    circle.bindPopup(
        "<b>Traffic:</b> {traffic}<br><b>Prediction:</b> {prediction}"
    );

    // EXTRA ZONES

    L.circle(
        [10.7820, 106.6800],
        {{
            color: 'green',
            fillColor: 'green',
            fillOpacity: 0.4,
            radius: 400
        }}
    ).addTo(map);

    L.circle(
        [10.7600, 106.7200],
        {{
            color: 'red',
            fillColor: 'red',
            fillOpacity: 0.4,
            radius: 400
        }}
    ).addTo(map);

    // =========================
    // CHART
    // =========================

    var ctx = document.getElementById('trafficChart');

    new Chart(ctx, {{
        type: 'line',

        data: {{
            labels: {labels},

            datasets: [{{
                label: 'Vehicle Count',

                data: {vehicle_history},

                borderColor: 'cyan',

                borderWidth: 3,

                tension: 0.3
            }}]
        }},

        options: {{
            responsive: true
        }}
    }});

    </script>

    </body>

    </html>

    """

if __name__ == "__main__":
    app.run(debug=True)