from djitellopy import Tello
import cv2
import numpy as np

def initializeTello():
    JwTello = Tello()
    JwTello.connect()
    JwTello.for_back_velocity = 0
    JwTello.left_right_velocity = 0
    JwTello.up_down_velocity = 0
    JwTello.yaw_velocity = 0
    JwTello.speed = 0
    print(JwTello.get_battery())
    JwTello.streamoff()
    JwTello.streamon()
    return JwTello


def telloFrame(JwTello, w = 360, h = 240):
    TFrame = JwTello.get_frame_read()
    TFrame = TFrame.frame
    img = cv2.resize(TFrame, (w,h))
    return img 

def tellofindFace(img):
    faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    imgGray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(imgGray, 1.2,4)
    
    myFaceListC = []
    myFaceListArea = []
    
    for (x,y,w,h) in faces:
        cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,255), 2)
        cx = x + w//2
        cy = y + h//2
        area = w*h
        myFaceListArea.append(area)
        myFaceListC.append([cx,cy])
        
    if len(myFaceListArea) != 0:
        i = myFaceListArea.index(max(myFaceListArea))
        return img, [myFaceListC[i], myFaceListArea[i]]
    else:
        return img, [[0,0],0]
    
def tellotrackFace(JwTello, info, w, pid, pError):
    
    # PID 동작
    error = info[0][0] - w//2
    speed = pid[0]*error + pid[1]*(error-pError)
    speed = int(np.clip(speed, -100, 100))
    print(speed)
    
    if info[0][0] != 0:
        JwTello.yaw_velocity = speed
    else:
        JwTello.for_back_velocity = 0
        JwTello.left_right_velocity = 0
        JwTello.up_down_velocity = 0
        JwTello.yaw_velocity = 0
        error = 0
    if JwTello.send_rc_control:
        JwTello.send_rc_control(JwTello.left_right_velocity, 
                                JwTello.for_back_velocity,
                                JwTello.up_down_velocity,
                                JwTello.yaw_velocity)
                
    return error
