from ultralytics import YOLO
import cv2
import csv
from datetime import datetime

# =========================
# LOAD MODEL
# =========================

model = YOLO("yolov8n.pt")

# =========================
# VIDEO PATH
# =========================

video_path = r"C:\Users\TrongTin-Computer\Documents\traffic.mp4"

cap = cv2.VideoCapture(video_path)

# =========================
# VARIABLES
# =========================

previous_centers = []

traffic_history = []

# =========================
# CSV FILE
# =========================

csv_file = open("traffic_data.csv", mode="a", newline="")

csv_writer = csv.writer(csv_file)

csv_writer.writerow([
    "time",
    "vehicles",
    "speed",
    "traffic"
])

# =========================
# MAIN LOOP
# =========================

while True:

    ret, frame = cap.read()

    if not ret:
        break

    # Resize frame
    frame = cv2.resize(frame, (1200, 700))

    # =========================
    # YOLO TRACKING
    # =========================

    results = model.track(frame, persist=True)

    annotated_frame = results[0].plot()

    boxes = results[0].boxes

    vehicle_count = 0

    current_centers = []

    # =========================
    # VEHICLE DETECTION
    # =========================

    if boxes is not None:

        for box in boxes:

            cls = int(box.cls[0])

            # Vehicle classes
            if cls in [2, 3, 5, 7]:

                vehicle_count += 1

                x1, y1, x2, y2 = box.xyxy[0]

                center_x = int((x1 + x2) / 2)
                center_y = int((y1 + y2) / 2)

                current_centers.append((center_x, center_y))

    # =========================
    # SPEED ESTIMATION
    # =========================

    motion_total = 0

    if len(previous_centers) == len(current_centers):

        for i in range(len(current_centers)):

            old_x, old_y = previous_centers[i]
            new_x, new_y = current_centers[i]

            distance = abs(new_x - old_x) + abs(new_y - old_y)

            motion_total += distance

    if motion_total < 50:

        speed_status = "SLOW"

    elif motion_total < 150:

        speed_status = "MEDIUM"

    else:

        speed_status = "FAST"

    previous_centers = current_centers

    # =========================
    # TRAFFIC LEVEL
    # =========================

    if vehicle_count < 5:

        traffic_status = "LOW"
        traffic_color = (0, 255, 0)

    elif vehicle_count < 15:

        traffic_status = "MEDIUM"
        traffic_color = (0, 165, 255)

    else:

        traffic_status = "HIGH"
        traffic_color = (0, 0, 255)

    # =========================
    # CONGESTION LOGIC
    # =========================

    if traffic_status == "HIGH" and speed_status == "SLOW":

        congestion_status = "TRAFFIC JAM"
        congestion_color = (0, 0, 255)

    else:

        congestion_status = "FLOWING"
        congestion_color = (0, 255, 0)

    # =========================
    # PREDICTION SYSTEM
    # =========================

    traffic_history.append((traffic_status, speed_status))

    # Keep last 20 states
    if len(traffic_history) > 20:
        traffic_history.pop(0)

    high_slow_count = 0

    for t_status, s_status in traffic_history:

        if t_status == "HIGH" and s_status == "SLOW":

            high_slow_count += 1

    if high_slow_count > 10:

        prediction_status = "JAM LIKELY NEXT 5 MIN"
        prediction_color = (0, 0, 255)

    else:

        prediction_status = "TRAFFIC STABLE"
        prediction_color = (0, 255, 0)

    # =========================
    # DASHBOARD PANEL
    # =========================

    cv2.rectangle(
        annotated_frame,
        (0, 0),
        (500, 330),
        (40, 40, 40),
        -1
    )

    cv2.putText(
        annotated_frame,
        "TRAFFIC AI CONTROL CENTER",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (255, 255, 255),
        2
    )

    cv2.putText(
        annotated_frame,
        f"Vehicles: {vehicle_count}",
        (20, 90),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2
    )

    cv2.putText(
        annotated_frame,
        f"Traffic: {traffic_status}",
        (20, 130),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        traffic_color,
        2
    )

    cv2.putText(
        annotated_frame,
        f"Speed: {speed_status}",
        (20, 170),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 0),
        2
    )

    cv2.putText(
        annotated_frame,
        f"Status: {congestion_status}",
        (20, 210),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        congestion_color,
        2
    )

    cv2.putText(
        annotated_frame,
        f"Prediction: {prediction_status}",
        (20, 250),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        prediction_color,
        2
    )

    # =========================
    # ROAD STATUS PANEL
    # =========================

    cv2.rectangle(
        annotated_frame,
        (900, 0),
        (1200, 260),
        (30, 30, 30),
        -1
    )

    cv2.putText(
        annotated_frame,
        "ROAD STATUS",
        (960, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (255, 255, 255),
        2
    )

    roads = [
        ("Road A", traffic_status, traffic_color),
        ("Road B", "MEDIUM", (0, 165, 255)),
        ("Road C", "LOW", (0, 255, 0))
    ]

    y = 90

    for road_name, status, color in roads:

        cv2.putText(
            annotated_frame,
            road_name,
            (930, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )

        cv2.circle(
            annotated_frame,
            (1120, y - 10),
            12,
            color,
            -1
        )

        cv2.putText(
            annotated_frame,
            status,
            (1140, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            color,
            2
        )

        y += 60

    # =========================
    # SAVE CSV DATA
    # =========================

    current_time = datetime.now().strftime("%H:%M:%S")

    csv_writer.writerow([
        current_time,
        vehicle_count,
        speed_status,
        traffic_status
    ])

    # =========================
    # SAVE REALTIME STATUS
    # =========================

    with open("traffic_status.txt", "w") as status_file:

        status_file.write(
            f"{vehicle_count},{traffic_status},{speed_status},{prediction_status}"
        )

    # =========================
    # SHOW WINDOW
    # =========================

    cv2.imshow("Traffic Intelligence System", annotated_frame)

    # Quit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# =========================
# CLEANUP
# =========================

cap.release()

cv2.destroyAllWindows()

csv_file.close()