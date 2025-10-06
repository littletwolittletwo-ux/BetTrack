import cv2
import numpy as np

def preprocess(img_bgr):
 gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
 gray = cv2.bilateralFilter(gray, 9, 75, 75)
 th = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                            cv2.THRESH_BINARY, 35, 10)
 h, w = th.shape
 scale = 1600.0 / max(w, 1)
 if scale > 0: th = cv2.resize(th, (int(w*scale), int(h*scale)))
 return th