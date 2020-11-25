import cv2
import numpy as np

def onChange(x):
    pass

img = np.zeros((1024 , 1024, 3), np.uint8)
cv2.namedWindow('trackBar',cv2.WINDOW_NORMAL)
cv2.createTrackbar('R', 'trackBar',0,255, onChange)
cv2.createTrackbar('G', 'trackBar', 0, 255, onChange)
cv2.createTrackbar('B','trackBar', 0, 255, onChange)

while True:
    cv2.imshow('trackBar', img)
    R = cv2.getTrackbarPos('R', 'trackBar')
    G = cv2.getTrackbarPos('G', 'trackBar')
    B = cv2.getTrackbarPos('B', 'trackBar')

    img[:] = [B,G,R]
    k = cv2.waitKey(1)
    if k == 27:
        break

cv2.destroyAllWindows()
