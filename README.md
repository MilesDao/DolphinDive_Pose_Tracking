<div align="center">
    <h1>🎮 Flappy Bird – Pose Controlled Game (MediaPipe + OpenCV + Pygame)</h1>
<hr/>
</div>

A Flappy Bird–style game controlled by **your arms** using real-time pose estimation.
This project uses a webcam and human pose landmarks to let the player **flap by moving both arms down** instead of pressing a key.

Built as a computer-vision + game integration project.

### ✨ 1. Features

- Control the bird using body movement (both arms)
- Real-time pose tracking with MediaPipe
- Angle-based gesture detection (shoulder–elbow–hip)
- Classic Flappy Bird mechanics (pipes, gravity, score, sounds)
- Keyboard fallback (SPACE)

### 🧠 2. How the control works

The game tracks:
- Left arm angle: `(elbow – shoulder – hip)`
- Right arm angle: `(elbow – shoulder – hip)`

When **both arms move down** and the angles drop below a threshold, a **flap is triggered**.

Internally:

- Shoulder / elbow landmarks: `11, 12, 13, 14`
- Hip landmarks: `23, 24`
- The angles are converted into a percentage
- A flap is detected when both sides go from “up” → “down”

This avoids repeated flaps while the arms stay in the same position.

## 🎯 3. Controls

| Action          | Method                                              |
|-----------------|-----------------------------------------------------|
| Flap            | Lower both arms                                     |
| Flap (fallback) | Press `SPACE`                                      |
| Quit            | Press `q` (camera window) or close the game window |

### 📦 4. How to run

Requirements: Python ≤ 3.10

4.1. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows
```

4.2 Install dependencies
```bash
pip install -r requirements.txt
```
4.3
```bash
python main.py
```

Make sure your webcam is connected.
