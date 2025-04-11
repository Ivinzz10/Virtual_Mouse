import cv2
import mediapipe as mp
import util
import pyautogui
import random
from pynput.mouse import Button, Controller
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import font as tkFont
import threading

pyautogui.FAILSAFE = False
mouse = Controller()
screen_width, screen_height = pyautogui.size()

mpHands = mp.solutions.hands
hands = mpHands.Hands(
    static_image_mode=False,
    model_complexity=1,
    min_detection_confidence=0.5,  
    min_tracking_confidence=0.8, 
    max_num_hands=1
)
SMOOTHING_FACTOR = 0.5  
prev_x, prev_y = 0, 0  
prev_left_click = False  
prev_right_click = False
prev_scroll_up = False
prev_scroll_down = False
prev_double_click = False
prev_screenshot = False
running = False

def find_finger_tip(processed):
    if processed.multi_hand_landmarks:
        hand_landmarks = processed.multi_hand_landmarks[0]
        return hand_landmarks.landmark[mpHands.HandLandmark.INDEX_FINGER_TIP]
    return None

def move_mouse(index_finger_tip, middle_finger_tip, landmarks_list):
    global prev_x, prev_y
    ring_finger_folded = util.get_angle(landmarks_list[13], landmarks_list[14], landmarks_list[16]) < 50
    pinky_finger_folded = util.get_angle(landmarks_list[17], landmarks_list[18], landmarks_list[20]) < 50
    thumb_folded = util.get_angle(landmarks_list[4], landmarks_list[3], landmarks_list[2]) < 130
    if index_finger_tip and middle_finger_tip and ring_finger_folded and pinky_finger_folded and thumb_folded:  
        x = int((index_finger_tip.x + middle_finger_tip.x) / 2 * screen_width)  
        y = int((index_finger_tip.y + middle_finger_tip.y) / 2 * screen_height)  
        smooth_x = int(prev_x * (1 - SMOOTHING_FACTOR) + x * SMOOTHING_FACTOR)
        smooth_y = int(prev_y * (1 - SMOOTHING_FACTOR) + y * SMOOTHING_FACTOR)
        pyautogui.moveTo(smooth_x, smooth_y)
        prev_x, prev_y = smooth_x, smooth_y 

def is_left_click(landmarks_list, thumb_index_dist):
    return (util.get_angle(landmarks_list[5], landmarks_list[6], landmarks_list[8]) < 50 and
            util.get_angle(landmarks_list[9], landmarks_list[10], landmarks_list[12]) > 90 and
            thumb_index_dist > 80)  

def is_right_click(landmark_list, thumb_index_dist):
    return (util.get_angle(landmark_list[9], landmark_list[10], landmark_list[12]) < 50 and
            util.get_angle(landmark_list[5], landmark_list[6], landmark_list[8]) > 90 and
            thumb_index_dist > 80)

def is_double_click(landmark_list, thumb_index_dist):
    return (util.get_angle(landmark_list[5], landmark_list[6], landmark_list[8]) < 50 and
            util.get_angle(landmark_list[9], landmark_list[10], landmark_list[12]) < 50 and
            thumb_index_dist > 80)

def is_screenshot(landmark_list, thumb_index_dist):
    return (util.get_angle(landmark_list[5], landmark_list[6], landmark_list[8]) < 50 and
            util.get_angle(landmark_list[9], landmark_list[10], landmark_list[12]) < 50 and
            util.get_angle(landmark_list[13], landmark_list[14], landmark_list[16]) < 50 and
            util.get_angle(landmark_list[17], landmark_list[18], landmark_list[20]) < 50 and
            thumb_index_dist < 50)

def is_scroll_up(landmarks_list):
    return (util.get_angle(landmarks_list[5], landmarks_list[6], landmarks_list[8]) > 160 and  
            util.get_angle(landmarks_list[9], landmarks_list[10], landmarks_list[12]) > 160 and  
            util.get_angle(landmarks_list[13], landmarks_list[14], landmarks_list[16]) > 160 and  
            util.get_angle(landmarks_list[17], landmarks_list[18], landmarks_list[20]) > 160 and  
            util.get_angle(landmarks_list[4], landmarks_list[3], landmarks_list[2]) < 100)  

def is_scroll_down(landmarks_list):
    return (util.get_angle(landmarks_list[5], landmarks_list[6], landmarks_list[8]) > 160 and  
            util.get_angle(landmarks_list[9], landmarks_list[10], landmarks_list[12]) > 160 and  
            util.get_angle(landmarks_list[13], landmarks_list[14], landmarks_list[16]) < 60 and  
            util.get_angle(landmarks_list[17], landmarks_list[18], landmarks_list[20]) > 160 and  
            util.get_angle(landmarks_list[4], landmarks_list[3], landmarks_list[2]) < 100)

def detect_gestures(frame, landmarks_list, processed):
    global prev_left_click, prev_right_click
    if len(landmarks_list) >= 21:
        index_finger_tip = find_finger_tip(processed)
        thumb_index_dist = util.get_distance([landmarks_list[4], landmarks_list[5]])
        middle_finger_tip = processed.multi_hand_landmarks[0].landmark[mpHands.HandLandmark.MIDDLE_FINGER_TIP]       
        move_mouse(index_finger_tip, middle_finger_tip, landmarks_list)

        left_click = is_left_click(landmarks_list, thumb_index_dist)
        if left_click and not prev_left_click:
            mouse.press(Button.left)
            mouse.release(Button.left)
            cv2.putText(frame, "Left Click", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        right_click = is_right_click(landmarks_list, thumb_index_dist)
        if right_click and not prev_right_click:
            mouse.press(Button.right)
            mouse.release(Button.right)
            cv2.putText(frame, "Right Click", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        prev_left_click = left_click
        prev_right_click = right_click

        scroll_up = is_scroll_up(landmarks_list)
        if scroll_up and not prev_scroll_up:
            pyautogui.scroll(40)
            cv2.putText(frame, "Scroll Up", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

        scroll_down = is_scroll_down(landmarks_list)
        if scroll_down and not prev_scroll_down:
            pyautogui.scroll(-40)
            cv2.putText(frame, "Scroll Down", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

        double_click = is_double_click(landmarks_list, thumb_index_dist)
        if double_click and not prev_double_click:
            pyautogui.doubleClick()
            cv2.putText(frame, "Double Click", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

        screenshot = is_screenshot(landmarks_list, thumb_index_dist)
        if screenshot and not prev_screenshot:
            im1 = pyautogui.screenshot()
            label = random.randint(1, 1000)
            im1.save(f'my_screenshot_{label}.png')
            cv2.putText(frame, "Screenshot Taken", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)


def main():
    global running
    cap = cv2.VideoCapture(0)
    draw = mp.solutions.drawing_utils
    running = True
    try:
        while running and cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv2.flip(frame, 1)
            frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            processed = hands.process(frameRGB)
            landmarks_list = []
            if processed.multi_hand_landmarks:
                hand_landmarks = processed.multi_hand_landmarks[0]
                draw.draw_landmarks(frame, hand_landmarks, mpHands.HAND_CONNECTIONS)

                for lm in hand_landmarks.landmark:
                    landmarks_list.append((lm.x, lm.y))

            detect_gestures(frame, landmarks_list, processed)

            cv2.imshow('Frame', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()
        running = False


# Help Section Content
HELP_TEXT = """
Welcome to Virtual Mouse!

📌 Gestures:
• Move Mouse: Extend index & middle fingers. Fold ring & pinky.
• Left Click: Fold index finger.
• Right Click: Fold middle finger.
• Scroll Up: Extend all fingers.
• Scroll Down: Extend index, middle & pinky.
• Double Click: Fold index & middle fingers.
• Screenshot: Fold index & middle, extend ring & pinky.

Ensure proper lighting for best results."""

class HandGestureUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Virtual Mouse")
        self.root.geometry("750x570")
        self.root.configure(bg="#2E3440")  

        self.title_font = tkFont.Font(family="Helvetica", size=24, weight="bold")
        self.button_font = tkFont.Font(family="Helvetica", size=14, weight="bold")
        self.help_font = tkFont.Font(family="Helvetica", size=12)

        self.main_frame = tk.Frame(root, bg="#2E3440")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        title_label = tk.Label(self.main_frame, text="Virtual Mouse", font=self.title_font, bg="#2E3440", fg="#ECEFF4")
        title_label.pack(pady=50)

        # Frame for Start and Stop Buttons
        button_frame = tk.Frame(self.main_frame, bg="#2E3440")
        button_frame.pack(pady=25)
    
        self.start_button = tk.Button(button_frame, text="▶ Start", command=self.start_recognition, font=self.button_font,
                                     bg="#5E81AC", fg="#ECEFF4", activebackground="#81A1C1", activeforeground="#ECEFF4",
                                     relief="flat", bd=0, padx=35, pady=15, cursor="hand2")
        self.start_button.pack(side="left", padx=15)


        self.stop_button = tk.Button(button_frame, text="■ Stop", command=self.stop_recognition, font=self.button_font,
                                    bg="#BF616A", fg="#ECEFF4", activebackground="#D08770", activeforeground="#ECEFF4",
                                    relief="flat", bd=0, padx=35, pady=15, cursor="hand2", state=tk.DISABLED)
        self.stop_button.pack(side="left", padx=15)

        # Frame for Help and Settings Buttons
        bottom_button_frame = tk.Frame(self.main_frame, bg="#2E3440")
        bottom_button_frame.pack(pady=10)
    
        self.help_button = tk.Button(bottom_button_frame, text="❓ Help", command=self.show_help, font=self.help_font,
                                    bg="#4C566A", fg="#ECEFF4", activebackground="#5E81AC", activeforeground="#ECEFF4",
                                    relief="flat", bd=0, padx=20, pady=5, cursor="hand2")
        self.help_button.pack(side="left", padx=10)

   
        self.settings_button = tk.Button(bottom_button_frame, text="⚙ Settings", command=self.toggle_settings, font=self.help_font,
                                         bg="#4C566A", fg="#ECEFF4", activebackground="#5E81AC", activeforeground="#ECEFF4",
                                         relief="flat", bd=0, padx=20, pady=5, cursor="hand2")
        self.settings_button.pack(side="left", padx=10)
       
        self.settings_panel = tk.Frame(self.main_frame, bg="#3B4252", bd=2, relief=tk.RAISED)
        self.settings_panel.pack(pady=10, fill=tk.X, padx=20)
        self.settings_panel.pack_forget() 
 
        self.smoothing_label = tk.Label(self.settings_panel, text="Smoothing Factor", font=self.help_font, bg="#3B4252", fg="#ECEFF4")
        self.smoothing_label.pack(pady=5)

        self.smoothing_slider = ttk.Scale(self.settings_panel, from_=0.1, to=1.0, orient=tk.HORIZONTAL, length=300)
        self.smoothing_slider.set(SMOOTHING_FACTOR)  # Set default value
        self.smoothing_slider.pack(pady=5)

        self.status_label = tk.Label(self.main_frame, text="Status: Stopped", font=self.button_font, bg="#2E3440", fg="#ECEFF4")
        self.status_label.pack(pady=20)

    def start_recognition(self):
        global running
        if not running:
            threading.Thread(target=main, daemon=True).start()
            self.status_label.config(text="Status: Running", fg="#A3BE8C")
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)

    def stop_recognition(self):
        global running
        running = False
        self.status_label.config(text="Status: Stopped", fg="#BF616A")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def show_help(self):
        help_window = tk.Toplevel(self.root)
        help_window.title("Help")
        help_window.geometry("600x400")
        help_window.configure(bg="#2E3440")      
        help_text = tk.Text(help_window, wrap=tk.WORD, font=self.help_font, bg="#2E3440", fg="#ECEFF4", padx=10, pady=10)
        help_text.insert(tk.END, HELP_TEXT)
        help_text.config(state=tk.DISABLED) 
        help_text.pack(fill=tk.BOTH, expand=True)     
        close_button = tk.Button(help_window, text="Close", command=help_window.destroy, font=self.help_font,
                                 bg="#5E81AC", fg="#ECEFF4", activebackground="#81A1C1", activeforeground="#ECEFF4",
                                 relief="flat", bd=0, padx=15, pady=5, cursor="hand2")
        close_button.pack(pady=10)

    def toggle_settings(self):    
        if self.settings_panel.winfo_ismapped():
            self.settings_panel.pack_forget()
        else:
            self.settings_panel.pack(pady=10, fill=tk.X, padx=20)

    def update_smoothing_factor(self, value):
        global SMOOTHING_FACTOR
        SMOOTHING_FACTOR = float(value)

if __name__ == '__main__':
    root = tk.Tk()
    app = HandGestureUI(root)
    app.smoothing_slider.configure(command=app.update_smoothing_factor)
    root.mainloop()