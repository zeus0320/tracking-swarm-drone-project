from djitellopy import Tello
import cv2
import numpy as np


width = 480  # width of the image
height = 360  # height of the image
deadZone = 100


startCounter = 0        # startCounter = 1, Inspection Mode, startCounter = 0, Flight Mode

# CONNECT TO TELLO                        # Tello Connect, Initial velocity settings
us = Tello()
us.connect()
us.for_back_velocity = 0
us.left_right_velocity = 0
us.up_down_velocity = 0
us.yaw_velocity = 0
us.speed = 0


print(us.get_battery())

us.streamoff()
us.streamon()
########################

frameWidth = width
frameHeight = height
# cap = cv2.VideoCapture(1)
# cap.set(3, frameWidth)
# cap.set(4, frameHeight)
# cap.set(10,200)

# set Global variables
global imgContour
global room;

# pass function
def empty(a):
    pass

# Create Two Trackbars (HSV SPACE, CANNY EDGE DETECT)
cv2.namedWindow("HSV")
cv2.resizeWindow("HSV",640,240)
cv2.createTrackbar("HUE Min","HSV",20,179,empty)
cv2.createTrackbar("HUE Max","HSV",40,179,empty)
cv2.createTrackbar("SAT Min","HSV",148,255,empty)
cv2.createTrackbar("SAT Max","HSV",255,255,empty)
cv2.createTrackbar("VALUE Min","HSV",89,255,empty)
cv2.createTrackbar("VALUE Max","HSV",255,255,empty)

cv2.namedWindow("Parameters")
cv2.resizeWindow("Parameters",640,240)
cv2.createTrackbar("Threshold1","Parameters",166,255,empty)
cv2.createTrackbar("Threshold2","Parameters",171,255,empty)
cv2.createTrackbar("Area","Parameters",1750,30000,empty)


def stackImages(scale,imgArray):                                    #이미지 배열 함수
    rows = len(imgArray)
    cols = len(imgArray[0])
    rowsAvailable = isinstance(imgArray[0], list)
    width = imgArray[0][0].shape[1]
    height = imgArray[0][0].shape[0]
    if rowsAvailable:
        for x in range ( 0, rows):
            for y in range(0, cols):
                if imgArray[x][y].shape[:2] == imgArray[0][0].shape [:2]:
                    imgArray[x][y] = cv2.resize(imgArray[x][y], (0, 0), None, scale, scale)
                else:
                    imgArray[x][y] = cv2.resize(imgArray[x][y], (imgArray[0][0].shape[1], imgArray[0][0].shape[0]), None, scale, scale)
                if len(imgArray[x][y].shape) == 2: imgArray[x][y]= cv2.cvtColor( imgArray[x][y], cv2.COLOR_GRAY2BGR)
        imageBlank = np.zeros((height, width, 3), np.uint8)
        hor = [imageBlank]*rows
        hor_con = [imageBlank]*rows
        for x in range(0, rows):

            hor[x] = np.hstack(imgArray[x])
        ver = np.vstack(hor)
    else:
        for x in range(0, rows):
            if imgArray[x].shape[:2] == imgArray[0].shape[:2]:
                imgArray[x] = cv2.resize(imgArray[x], (0, 0), None, scale, scale)
            else:
                imgArray[x] = cv2.resize(imgArray[x], (imgArray[0].shape[1], imgArray[0].shape[0]), None,scale, scale)
            if len(imgArray[x].shape) == 2: imgArray[x] = cv2.cvtColor(imgArray[x], cv2.COLOR_GRAY2BGR)
        hor= np.hstack(imgArray)
        ver = hor
    return ver

def getContours(img,imgContour):                         #윤곽선 검출 함수
    global room
    contours, hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    for cnt in contours:
        area = cv2.contourArea(cnt)
        areaMin = cv2.getTrackbarPos("Area", "Parameters")
        if area > areaMin:
            cv2.drawContours(imgContour, cnt, -1, (255, 0, 255), 7)      # -1: 모든 컨투어 그려짐
            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
            #print(len(approx))
            x , y , w, h = cv2.boundingRect(approx)
            cx = int(x + (w / 2))  # CENTER X OF THE OBJECT
            cy = int(y + (h / 2))  # CENTER X OF THE OBJECT

            if (cx <int(frameWidth/2)-deadZone):
                cv2.putText(imgContour, " GO LEFT " , (20, 50), cv2.FONT_HERSHEY_COMPLEX,1,(0, 0, 255), 3)
                cv2.rectangle(imgContour,(0,int(frameHeight/2-deadZone)),(int(frameWidth/2)-deadZone,int(frameHeight/2)+deadZone),(0,0,255),cv2.FILLED)
                room = 1
            elif (cx > int(frameWidth / 2) + deadZone):
                cv2.putText(imgContour, " GO RIGHT ", (20, 50), cv2.FONT_HERSHEY_COMPLEX,1,(0, 0, 255), 3)
                cv2.rectangle(imgContour,(int(frameWidth/2+deadZone),int(frameHeight/2-deadZone)),(frameWidth,int(frameHeight/2)+deadZone),(0,0,255),cv2.FILLED)
                room = 2
            elif (cy < int(frameHeight / 2) - deadZone):
                cv2.putText(imgContour, " GO UP ", (20, 50), cv2.FONT_HERSHEY_COMPLEX,1,(0, 0, 255), 3)
                cv2.rectangle(imgContour,(int(frameWidth/2-deadZone),0),(int(frameWidth/2+deadZone),int(frameHeight/2)-deadZone),(0,0,255),cv2.FILLED)
                room = 3
            elif (cy > int(frameHeight / 2) + deadZone):
                cv2.putText(imgContour, " GO DOWN ", (20, 50), cv2.FONT_HERSHEY_COMPLEX, 1,(0, 0, 255), 3)
                cv2.rectangle(imgContour,(int(frameWidth/2-deadZone),int(frameHeight/2)+deadZone),(int(frameWidth/2+deadZone),frameHeight),(0,0,255),cv2.FILLED)
                room = 4
            else: room = 0

            cv2.line(imgContour, (int(frameWidth/2),int(frameHeight/2)), (cx,cy),(0, 0, 255), 3)
            cv2.rectangle(imgContour, (x, y), (x + w, y + h), (0, 255, 0), 5)
            cv2.putText(imgContour, "Points: " + str(len(approx)), (x + w + 20, y + 20), cv2.FONT_HERSHEY_COMPLEX, .7,(0, 255, 0), 2)
            cv2.putText(imgContour, "Area: " + str(int(area)), (x + w + 20, y + 45), cv2.FONT_HERSHEY_COMPLEX, 0.7,(0, 255, 0), 2)
            cv2.putText(imgContour, " " + str(int(x)) + " " + str(int(y)), (x - 20, y - 45), cv2.FONT_HERSHEY_COMPLEX,0.7,(0, 255, 0), 2)
        else: room = 0

def display(img):
    cv2.line(img,(int(frameWidth/2)-deadZone,0),(int(frameWidth/2)-deadZone,frameHeight),(255,255,0),3)
    cv2.line(img,(int(frameWidth/2)+deadZone,0),(int(frameWidth/2)+deadZone,frameHeight),(255,255,0),3)
    cv2.circle(img,(int(frameWidth/2),int(frameHeight/2)),5,(0,0,255),5)
    cv2.line(img, (0,int(frameHeight / 2) - deadZone), (frameWidth,int(frameHeight / 2) - deadZone), (255, 255, 0), 3)
    cv2.line(img, (0, int(frameHeight / 2) + deadZone), (frameWidth, int(frameHeight / 2) + deadZone), (255, 255, 0), 3)

while True:

    # GET THE IMAGE FROM TELLO
    frame_read = us.get_frame_read()
    myFrame = frame_read.frame
    img = cv2.resize(myFrame, (width, height))
    imgContour = img.copy()
    imgHsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)


    h_min = cv2.getTrackbarPos("HUE Min","HSV")
    h_max = cv2.getTrackbarPos("HUE Max", "HSV")
    s_min = cv2.getTrackbarPos("SAT Min", "HSV")
    s_max = cv2.getTrackbarPos("SAT Max", "HSV")
    v_min = cv2.getTrackbarPos("VALUE Min", "HSV")
    v_max = cv2.getTrackbarPos("VALUE Max", "HSV")


    lower = np.array([h_min,s_min,v_min]) #트랙바 결과값을 받아온 수치의 최소/최대값을 배열
    upper = np.array([h_max,s_max,v_max])
    mask = cv2.inRange(imgHsv,lower,upper) # 소스인 ImgHsv의 모든 값이 lower~upper 범위에 있는지 체크, 해당하면 1 나머지는 0
    result = cv2.bitwise_and(img,img, mask = mask) #이미지 비트연산 -
    mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR) # 마스크 이미지를 RGB 색상 이미지로 변환

    imgBlur = cv2.GaussianBlur(result, (7, 7), 1)  #GaussianBlur 라이브러리 - 이미지 노이즈 제거
    imgGray = cv2.cvtColor(imgBlur, cv2.COLOR_BGR2GRAY) # 노이즈 제거된 이미지를 GRAY이미지로 변환
    threshold1 = cv2.getTrackbarPos("Threshold1", "Parameters")  # Parameters 트랙바 결과값을 변수에 각각 저장
    threshold2 = cv2.getTrackbarPos("Threshold2", "Parameters")
    imgCanny = cv2.Canny(imgGray, threshold1, threshold2)    #Canny Edge Detector - 엣지 검출
    kernel = np.ones((5, 5))   #1로 가득찬 5x5 shape matrix kernel 생성
    imgDil = cv2.dilate(imgCanny, kernel, iterations=1) # imgCanny 이미지 dilate(팽창) 작업 1회 반복
    getContours(imgDil, imgContour) #getContours 함수에 팽창된 Canny이미지와 원본 이미지 대입
    display(imgContour)

    # FLIGHT START
    if startCounter == 0:         # startCounter = 0, Tello Takeoff
       us.takeoff()
       startCounter = 1


    if room == 1:                # getContours 함수 조건문의 room 출력값에 따른 드론의 동작
       us.left_right_velocity = -30
    elif room == 2:
       us.left_right_velocity = 30
    elif room == 3:
       us.for_back_velocity= 30
    elif room == 4:
       us.for_back_velocity= -30
    else:
       us.left_right_velocity = 0; us.for_back_velocity = 0;us.up_down_velocity = 0; us.yaw_velocity = 0

   # SEND VELOCITY VALUES TO TELLO
    if us.send_rc_control:
       us.send_rc_control(us.left_right_velocity, us.for_back_velocity, us.up_down_velocity, us.yaw_velocity)
    print(room)

    stack = stackImages(0.9, ([img, result], [imgDil, imgContour]))    # 각기 다른 이미지를 나란히 놓기
    cv2.imshow('Horizontal Stacking', stack)                           # 화면 출력

    if cv2.waitKey(1) & 0xFF == ord('q'):
        us.land()
        break

# cap.release()
cv2.destroyAllWindows()
