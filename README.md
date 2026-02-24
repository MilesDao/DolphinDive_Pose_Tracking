<div align="center">
    <h1>🎮 Flappy Bird – Pose Controlled (YOLOv8 + OpenCV + Pygame)</h1>
<hr/>
</div>

A Flappy Bird–style game controlled by **arm movements** using real-time human pose estimation with **YOLOv8 Pose**.

This project focuses on **real-time computer vision** and human–computer interaction.

### ✨ 1. Features

- Control the bird by **raising and lowering both arms**
- Real-time pose estimation using YOLOv8 pose model
- Angle-based gesture detection (shoulder–elbow–hip)
- One unified window:
    + left: camera view
    + right: game view
- Classic Flappy Bird gameplay (pipes, gravity, score, sounds)
- Keyboard fallback (SPACE)

### 🧠 2. How the control works

The game tracks:
- Left arm angle: `(elbow – shoulder – hip)`
- Right arm angle: `(elbow – shoulder – hip)`

When **both arms move down** and the angles drop below a threshold, a **flap is triggered**.

Used keypoints (YOLOv8 format):

- Left side: 5, 7, 11
- Right side: 6, 8, 12

## 🎯 3. Controls

| Action          | Method                                              |
|-----------------|-----------------------------------------------------|
| Flap            | Lower both arms                                     |
| Flap (fallback) | Press `SPACE`                                      |
| Quit            | Press `q` (camera window) or close the game window |

### 📦 4. How to run

Requirements: Python 3.9+

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
