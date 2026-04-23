import cv2
import mediapipe as mp
from collections import deque
import numpy as np

mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# Landmarks
LEFT_EAR = 234
RIGHT_EAR = 454
NOSE_TIP = 1
CHIN = 152
UPPER_LIP = 13
LOWER_LIP = 14

# Thresholds
TILT_THRESHOLD = 12
NOD_THRESHOLD = 8
MOUTH_OPEN_THRESHOLD = 0.04
SMOOTH_FRAMES = 3

COMMAND_FILE = "/tmp/claw_command.txt"

cap = cv2.VideoCapture(0)
command_buffer = deque(maxlen=SMOOTH_FRAMES)
confirmed_command = "ST"

def write_command(cmd):
    with open(COMMAND_FILE, "w") as f:
        f.write(cmd)

def get_angle(p1, p2):
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    return np.degrees(np.arctan2(dy, dx))

def draw_label(frame, text, x, y, active):
    font = cv2.FONT_HERSHEY_DUPLEX
    scale = 0.75
    thickness = 2
    text_color = (0, 255, 180) if active else (160, 160, 160)
    box_color = (0, 80, 50) if active else (40, 40, 40)
    (tw, th), baseline = cv2.getTextSize(text, font, scale, thickness)
    pad = 6
    cv2.rectangle(frame, (x - pad, y - th - pad), (x + tw + pad, y + baseline + pad), box_color, -1)
    cv2.rectangle(frame, (x - pad, y - th - pad), (x + tw + pad, y + baseline + pad), text_color, 1)
    cv2.putText(frame, text, (x, y), font, scale, text_color, thickness)

def draw_hud(frame, command, cx, cy, tilt_angle, nod_angle):
    active_arrow = (0, 255, 180)
    inactive_arrow = (80, 80, 80)
    grab_color = (0, 140, 255)
    circle_inactive = (80, 80, 80)
    circle_active = (0, 255, 180)

    radius = 85
    arrow_length = 100
    arrow_gap = radius + 20
    thickness = 6
    tip = 0.4

    ring_color = grab_color if command == "GO" else (circle_active if command != "ST" else circle_inactive)
    cv2.circle(frame, (cx, cy), radius + 4, ring_color, 1)
    cv2.circle(frame, (cx, cy), radius, ring_color, 3)
    cv2.circle(frame, (cx, cy), 8, ring_color, -1)

    if command != "ST":
        overlay = frame.copy()
        glow = grab_color if command == "GO" else active_arrow
        cv2.circle(overlay, (cx, cy), radius - 2, glow, -1)
        cv2.addWeighted(overlay, 0.15, frame, 0.85, 0, frame)

    # Tilt bar (horizontal)
    bar_w = 160
    bar_h = 12
    bar_x = cx - bar_w // 2
    bar_y = cy + radius + 35
    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (50, 50, 50), -1)
    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (100, 100, 100), 1)
    tilt_norm = np.clip(tilt_angle / 30.0, -1, 1)
    dot_x = int(cx + tilt_norm * (bar_w // 2))
    dot_color = active_arrow if abs(tilt_angle) > TILT_THRESHOLD else (180, 180, 180)
    cv2.circle(frame, (dot_x, bar_y + bar_h // 2), 8, dot_color, -1)
    thresh_x_r = int(cx + (TILT_THRESHOLD / 30.0) * (bar_w // 2))
    thresh_x_l = int(cx - (TILT_THRESHOLD / 30.0) * (bar_w // 2))
    cv2.line(frame, (thresh_x_r, bar_y), (thresh_x_r, bar_y + bar_h), (0, 200, 100), 1)
    cv2.line(frame, (thresh_x_l, bar_y), (thresh_x_l, bar_y + bar_h), (0, 200, 100), 1)

    # Nod bar (vertical)
    nbar_h = 160
    nbar_w = 12
    nbar_x = cx + radius + 35
    nbar_y = cy - nbar_h // 2
    cv2.rectangle(frame, (nbar_x, nbar_y), (nbar_x + nbar_w, nbar_y + nbar_h), (50, 50, 50), -1)
    cv2.rectangle(frame, (nbar_x, nbar_y), (nbar_x + nbar_w, nbar_y + nbar_h), (100, 100, 100), 1)
    nod_norm = np.clip(nod_angle / 20.0, -1, 1)
    dot_y = int(cy - nod_norm * (nbar_h // 2))
    ndot_color = active_arrow if abs(nod_angle) > NOD_THRESHOLD else (180, 180, 180)
    cv2.circle(frame, (nbar_x + nbar_w // 2, dot_y), 8, ndot_color, -1)
    thresh_y_d = int(cy + (NOD_THRESHOLD / 20.0) * (nbar_h // 2))
    thresh_y_u = int(cy - (NOD_THRESHOLD / 20.0) * (nbar_h // 2))
    cv2.line(frame, (nbar_x, thresh_y_d), (nbar_x + nbar_w, thresh_y_d), (0, 200, 100), 1)
    cv2.line(frame, (nbar_x, thresh_y_u), (nbar_x + nbar_w, thresh_y_u), (0, 200, 100), 1)

    # Arrows
    is_up = command == "Y-"
    color = active_arrow if is_up else inactive_arrow
    cv2.arrowedLine(frame, (cx, cy - arrow_gap), (cx, cy - arrow_gap - arrow_length), color, thickness + (2 if is_up else 0), tipLength=tip)
    draw_label(frame, "FORWARD", cx - 48, cy - arrow_gap - arrow_length - 16, is_up)

    is_down = command == "Y+"
    color = active_arrow if is_down else inactive_arrow
    cv2.arrowedLine(frame, (cx, cy + arrow_gap), (cx, cy + arrow_gap + arrow_length), color, thickness + (2 if is_down else 0), tipLength=tip)
    draw_label(frame, "BACK", cx - 28, cy + arrow_gap + arrow_length + 50, is_down)

    is_left = command == "X-"
    color = active_arrow if is_left else inactive_arrow
    cv2.arrowedLine(frame, (cx - arrow_gap, cy), (cx - arrow_gap - arrow_length, cy), color, thickness + (2 if is_left else 0), tipLength=tip)
    draw_label(frame, "LEFT", cx - arrow_gap - arrow_length - 68, cy + 8, is_left)

    is_right = command == "X+"
    color = active_arrow if is_right else inactive_arrow
    cv2.arrowedLine(frame, (cx + arrow_gap, cy), (cx + arrow_gap + arrow_length, cy), color, thickness + (2 if is_right else 0), tipLength=tip)
    draw_label(frame, "RIGHT", cx + arrow_gap + arrow_length + 10, cy + 8, is_right)

    if command == "GO":
        cv2.circle(frame, (cx, cy), radius, grab_color, 5)
        draw_label(frame, "GRABBING", cx - 58, cy + arrow_gap + arrow_length + 65, True)

    cv2.putText(frame, f"Tilt: {tilt_angle:.1f}deg", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 180, 180), 1)
    cv2.putText(frame, f"Nod:  {nod_angle:.1f}", (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 180, 180), 1)

write_command("ST")

with mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.8, min_tracking_confidence=0.8) as face_mesh:
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break
        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb)

        raw_command = "ST"
        tilt_angle = 0.0
        nod_angle = 0.0
        face_cx, face_cy = w // 2, h // 2

        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0].landmark

            left_ear  = (int(landmarks[LEFT_EAR].x * w),  int(landmarks[LEFT_EAR].y * h))
            right_ear = (int(landmarks[RIGHT_EAR].x * w), int(landmarks[RIGHT_EAR].y * h))
            nose      = (int(landmarks[NOSE_TIP].x * w),  int(landmarks[NOSE_TIP].y * h))
            chin      = (int(landmarks[CHIN].x * w),      int(landmarks[CHIN].y * h))
            upper_lip = landmarks[UPPER_LIP]
            lower_lip = landmarks[LOWER_LIP]

            face_cx = (left_ear[0] + right_ear[0]) // 2
            face_cy = (left_ear[1] + right_ear[1]) // 2

            # Tilt: ear-to-ear angle from horizontal
            tilt_angle = get_angle(left_ear, right_ear)

            # Nod: how far nose is ABOVE the ear midpoint
            # Positive = nose above ears = looking up = FORWARD
            # Negative = nose below ears = looking down = BACK
            ear_mid_y = (left_ear[1] + right_ear[1]) / 2
            ear_dist = abs(right_ear[0] - left_ear[0]) + 1
            nod_angle = (ear_mid_y - nose[1]) / ear_dist * 50

            mouth_dist = abs(lower_lip.y - upper_lip.y)

            # Command logic — dominant movement wins
            if mouth_dist > MOUTH_OPEN_THRESHOLD:
                raw_command = "GO"
            elif abs(tilt_angle) > TILT_THRESHOLD and abs(tilt_angle) >= abs(nod_angle):
                raw_command = "X+" if tilt_angle > 0 else "X-"
            elif abs(nod_angle) > NOD_THRESHOLD and abs(nod_angle) > abs(tilt_angle):
                raw_command = "Y-" if nod_angle > 0 else "Y+"
            else:
                raw_command = "ST"

            command_buffer.append(raw_command)
            if len(command_buffer) == SMOOTH_FRAMES and len(set(command_buffer)) == 1:
                confirmed_command = raw_command
            elif raw_command == "ST":
                confirmed_command = "ST"

            mp_drawing.draw_landmarks(image=frame, landmark_list=results.multi_face_landmarks[0],
                connections=mp_face_mesh.FACEMESH_TESSELATION, landmark_drawing_spec=None,
                connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_tesselation_style())

            # Draw ear line
            cv2.line(frame, left_ear, right_ear, (0, 255, 180), 2)
            cv2.circle(frame, left_ear, 5, (0, 255, 180), -1)
            cv2.circle(frame, right_ear, 5, (0, 255, 180), -1)

            # Draw ear midpoint to nose line
            ear_mid = ((left_ear[0] + right_ear[0]) // 2, int(ear_mid_y))
            cv2.line(frame, ear_mid, nose, (0, 200, 255), 2)
            cv2.circle(frame, ear_mid, 5, (0, 200, 255), -1)

            cv2.putText(frame, f"Mouth: {mouth_dist:.3f}", (20, h - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 200, 255), 1)

        else:
            confirmed_command = "ST"
            command_buffer.clear()
            cv2.putText(frame, "No face detected — look at camera", (w//2 - 180, h//2), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        draw_hud(frame, confirmed_command, face_cx, face_cy, tilt_angle, nod_angle)
        write_command(confirmed_command)

        font = cv2.FONT_HERSHEY_DUPLEX
        cmd_text = f"CMD: {confirmed_command}"
        cmd_color = (0, 255, 180) if confirmed_command != "ST" else (120, 120, 120)
        (tw, th), _ = cv2.getTextSize(cmd_text, font, 1.0, 2)
        cv2.rectangle(frame, (10, 10), (tw + 20, th + 20), (30, 30, 30), -1)
        cv2.rectangle(frame, (10, 10), (tw + 20, th + 20), cmd_color, 1)
        cv2.putText(frame, cmd_text, (15, th + 15), font, 1.0, cmd_color, 2)

        cv2.putText(frame, "Q = quit", (20, h - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (140, 140, 140), 1)

        cv2.imshow("ClawControl — Angle Mode", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()