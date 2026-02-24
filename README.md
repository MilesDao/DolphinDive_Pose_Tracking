🎮 Flappy Bird – Pose Controlled Game (MediaPipe + OpenCV + Pygame)

A Flappy Bird–style game controlled by your arms using real-time pose estimation.

This project uses a webcam and human pose landmarks to let the player flap by moving both arms down instead of pressing a key.

Built as a computer-vision + game integration project.

✨ Features

Control the bird using body movement (both arms)

Real-time pose tracking with MediaPipe

Angle-based gesture detection (shoulder–elbow–hip)

Classic Flappy Bird mechanics (pipes, gravity, score, sounds)

Keyboard fallback (SPACE)

🧠 How the control works

The game tracks:

Left arm angle: (elbow – shoulder – hip)

Right arm angle: (elbow – shoulder – hip)

When both arms move down and the angles drop below a threshold, a flap is triggered.

Internally:

Shoulder / elbow landmarks: 11, 12, 13, 14

Hip landmarks: 23, 24

The angles are converted into a percentage

A flap is detected when both sides go from “up” → “down”

This avoids repeated flaps while the arms stay in the same position.

🎯 Controls
Action	Method
Flap	Lower both arms
Flap (fallback)	Press SPACE
Quit	Press q (camera window) or close the game window
📦 Requirements

Python 3.8+

Libraries:

pip install pygame opencv-python mediapipe numpy
▶️ How to run

From the project folder:

python game.py

Make sure your webcam is connected.