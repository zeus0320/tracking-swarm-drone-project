from utlis import *
import cv2

w,h = 360,240
pid = [0.5,0.5,0]
pError = 0
startCounter = 0  # 비행 시 0, 점검 시 1

JwTello = initializeTello()

while True:
    
    if startCounter == 0:
        JwTello.takeoff()
        startcounter = 1
        
    img = telloFrame(JwTello,w,h)
    
    img, info = tellofindFace(img)
    
    pError = tellotrackFace(JwTello, info, w, pid, pError)
    
    print(info[0][0])
    cv2.imshow('Image', img)
    if cv2.waitkey(1) & 0xFF == ord('q'):
        JwTello.land()
        break
