 ## Virtual Mouse Using Hand Gestures with AI

A Python-based AI-powered virtual mouse that uses real-time hand gesture recognition to control mouse movements and actions — without touching any physical device!

## Features

- Real-time cursor movemen based on hand tracking
- Left click, right click, double click
- Scroll up / down using specific gestures
- Take screenshots with hand signals
- Smooth gesture control with adjustable sensitivity
- Intuitive Tkinter GUI with start/stop, help, and settings options

## Tech Stack

- Python
- OpenCV – for video capture and image processing
- MediaPipe – for hand landmark detection
- PyAutoGUI – for simulating mouse movements and clicks
- Pynput – for more control over mouse actions
- Tkinter – for GUI interface

## 📸 Gestures Implemented

| Gesture | Action |
|--------|--------|
| ✌️ (Index + Middle finger open) | Mouse movement |
| ☝️ (Index finger folded) | Left click |
| 🤞 (Middle finger folded) | Right click |
| 🤙 (Index + Middle folded) | Double click |
| 🖐️ (All fingers extended) | Scroll up |
| 🤘 (Ring finger folded) | Scroll down |
| 🤟 (Ring + Pinky extended, thumb near index) | Screenshot |

## 🖥️ How it Works

1. Uses webcam input to capture hand position.
2. Detects hand landmarks using MediaPipe.
3. Recognizes gestures based on joint angles and distances.
4. Maps gestures to corresponding mouse actions using PyAutoGUI and Pynput.
5. GUI lets user start/stop tracking and access help/settings.
