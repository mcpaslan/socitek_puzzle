# hand_tracker.py
import cv2
import mediapipe as mp
import math
import time
from settings import *


class HandTracker:
    """
    Kameradan sağ el için imleç & pinch, sol el için yumruk tespiti sağlar.
    process_frame() -> returns: (frame, hand_data)
      hand_data: {
        "cursor_pos": (x,y) or None,
        "pinch_event": 'NONE' | 'PINCH_DOWN' | 'PINCH_UP',
        "pinch_active": bool,
        "left_fist": bool
      }
    """

    def __init__(self, cam_index=0):
        self.cap = cv2.VideoCapture(cam_index)
        # Klasik webcam çözünürlüğü
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        self.mp_hands = mp.solutions.hands
        # İki el olabileceği için max_num_hands=2
        self.hands = self.mp_hands.Hands(max_num_hands=2,
                                         min_detection_confidence=0.6,
                                         min_tracking_confidence=0.6)
        self.mp_draw = mp.solutions.drawing_utils

        # pinch takibi
        self.pinch_state = False
        self.last_pinch_time = 0

        # imleç yumuşatma
        self.smoothed_cursor = None
        self.cursor_smoothing = 1.2  # 0..1 (düşük = ani, yüksek = daha yumuşak)

    def process_frame(self):
        """
        Kameradan tek frame alır, analiz eder ve hand_data döner.
        """
        ret, frame = self.cap.read()
        if not ret:
            return None, {}
        frame = cv2.flip(frame, 1)
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(image_rgb)

        pinch_event = 'NONE'
        cursor_pos = None
        left_fist = False
        pinch_active = self.pinch_state


        if results.multi_hand_landmarks and results.multi_handedness:
            # multi_handedness paralel sıralıdır; işlem sırasında her iki elin tipi elde edilebilir.
            for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                # handedness label (Left/Right)
                handedness = results.multi_handedness[idx].classification[0].label

                # landmark liste (x,y normalized)
                lm = hand_landmarks.landmark
                h_px, w_px, _ = frame.shape
                # convert to pixel coords for kolay geometri
                landmarks_px = [(int(p.x * w_px), int(p.y * h_px)) for p in lm]

                if handedness == "Right":
                    # Sağ el: imleç (index_tip) ve pinch (thumb_tip - index_tip)
                    ix, iy = landmarks_px[8]  # index tip
                    tx, ty = landmarks_px[4]  # thumb tip

                    # map camera coordinates -> ekran (WINDOW_WIDTH x WINDOW_HEIGHT)
                    sx = int(ix / w_px * WINDOW_WIDTH)
                    sy = int(iy / h_px * WINDOW_HEIGHT)
                    cursor_pos = (sx, sy)

                    # smoothing
                    if self.smoothed_cursor is None:
                        self.smoothed_cursor = cursor_pos
                    else:
                        sx_sm = int(self.smoothed_cursor[0] * (1 - self.cursor_smoothing) + cursor_pos[0] * self.cursor_smoothing)
                        sy_sm = int(self.smoothed_cursor[1] * (1 - self.cursor_smoothing) + cursor_pos[1] * self.cursor_smoothing)
                        self.smoothed_cursor = (sx_sm, sy_sm)
                        cursor_pos = self.smoothed_cursor

                    # hand size reference (wrist (0) to middle_finger_mcp (9))
                    wrist_x, wrist_y = landmarks_px[0]
                    midmcp_x, midmcp_y = landmarks_px[9]
                    hand_size_px = math.hypot(wrist_x - midmcp_x, wrist_y - midmcp_y)
                    if hand_size_px < 1e-6:
                        # koruma
                        hand_size_px = 1.0

                    thumb_index_dist = math.hypot(tx - ix, ty - iy)
                    pinch_strength = thumb_index_dist / hand_size_px

                    now_ms = int(time.time() * 1000)
                    # pinch logic using settings thresholds
                    if pinch_strength < PINCH_TRIGGER_LEVEL:
                        # pinch başladı
                        if not self.pinch_state and (now_ms - self.last_pinch_time) > PINCH_COOLDOWN_MS:
                            pinch_event = 'PINCH_DOWN'
                            self.pinch_state = True
                            self.last_pinch_time = now_ms
                        else:
                            # eğer zaten pinç aktif, pinch_event NONE
                            pinch_event = 'NONE'
                    else:
                        if self.pinch_state and pinch_strength > PINCH_RELEASE_LEVEL:
                            pinch_event = 'PINCH_UP'
                            self.pinch_state = False
                        else:
                            pinch_event = 'NONE'

                    pinch_active = self.pinch_state

                elif handedness == "Left":
                    # Sol el: yumruk tespiti
                    # basit yöntem: parmak uçlarının palm/wrist'e olan uzaklık ortalaması
                    # normalize edilmiş koordinatlar kullanılarak threshold uygulanır
                    # landmarks normalized (0..1), ortalama uzaklık
                    dists = []
                    palm_x = lm[0].x
                    palm_y = lm[0].y
                    tips_idx = [8, 12, 16, 20]
                    for t in tips_idx:
                        d = math.hypot(lm[t].x - palm_x, lm[t].y - palm_y)
                        dists.append(d)
                    avg_dist = sum(dists) / len(dists)
                    left_fist = avg_dist < FIST_AVG_DIST_THRESHOLD

                # sadece ilk iki el için döngü yeterli
        hand_data = {
            "frame": frame,
            "cursor_pos": cursor_pos,
            "pinch_event": pinch_event,
            "pinch_active": pinch_active,
            "left_fist": left_fist
        }
        return frame, hand_data

    def close(self):
        self.cap.release()
        self.hands.close()
