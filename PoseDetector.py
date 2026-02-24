import cv2
import math
import numpy as np
from ultralytics import YOLO

class PoseDetector:
    def __init__(self, model_path="yolov8n-pose.pt", use_gpu=True):
        self.device = 'cuda' if use_gpu else 'cpu'
        self.model = YOLO(model_path)
        self.model.to(self.device)
        self.results = None
        self.lmList = []

    def findPose(self, img, draw=True):
        """Find pose in image and draw skeleton if needed"""
        # run YOLO inference
        self.results = self.model(img, verbose=False, device=self.device)
        
        if draw:
            # ultralytics has a built-in plot function to draw keypoints
            # but we can also draw manually or use plot()
            annotated_img = self.results[0].plot()
            return annotated_img
        
        return img

    def findPosition(self, img, draw=False):
        """Returns the list of coordinates (id, x, y) of the landmarks"""
        self.lmList = []
        
        if not self.results or len(self.results[0].keypoints) == 0:
            return self.lmList

        # get keypoints of the first person detected
        # keypoints.data shape is (N, 17, 3) where 3 is (x, y, confidence)
        keypoints = self.results[0].keypoints.data[0].cpu().numpy()
        
        for idx, kp in enumerate(keypoints):
            x, y, conf = kp
            if conf > 0.3: # only append confident keypoints
                self.lmList.append([idx, int(x), int(y)])
            else:
                self.lmList.append([idx, 0, 0])
                
        if draw:
            for item in self.lmList:
                if item[1] != 0 or item[2] != 0:
                    cv2.circle(img, (item[1], item[2]), 5, (0, 0, 255), cv2.FILLED)

        return self.lmList

    def findAngle(self, img, p1, p2, p3, draw=True):
        """
        Tính góc tại p2 tạo bởi 3 điểm p1, p2, p3.
        """
        if not self.lmList or len(self.lmList) <= max(p1, p2, p3):
            return 0
            
        _, x1, y1 = self.lmList[p1]
        _, x2, y2 = self.lmList[p2]
        _, x3, y3 = self.lmList[p3]
        
        if (x1, y1) == (0, 0) or (x2, y2) == (0, 0) or (x3, y3) == (0, 0):
            return 0

        # Calculate distance between points
        a = math.hypot(x3 - x2, y3 - y2)
        c = math.hypot(x1 - x2, y1 - y2)
        b = math.hypot(x1 - x3, y1 - y3)

        if a * c == 0:
            angle = 0.0
        else:
            # Law of cosines
            cos_b = (a**2 + c**2 - b**2) / (2 * a * c)
            cos_b = max(-1.0, min(1.0, cos_b))
            angle = math.degrees(math.acos(cos_b))

        if draw:
            cv2.line(img, (x1, y1), (x2, y2), (255, 255, 255), 2)
            cv2.line(img, (x2, y2), (x3, y3), (255, 255, 255), 2)
            for (x, y) in [(x1, y1), (x2, y2), (x3, y3)]:
                cv2.circle(img, (x, y), 8, (0, 255, 0), cv2.FILLED)
                cv2.circle(img, (x, y), 12, (0, 255, 0), 2)

        return angle
