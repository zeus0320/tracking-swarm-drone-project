from djitellopy import Tello
import cv2
import numpy as np

width = 640  # 이미지의 초기 폭
height = 480  # 이미지의 초기 높이
deadZone = 100 # 경계값

startCounter =0    # 비행 모드 / 검사 모드 전환 변수, startCounter = 0 : Flight Mode

# 텔로 연결, 초기 속도값 설정(전/후/좌/우, 상하, Yaw 속도 = 0)
me = Tello()
me.connect()
me.for_back_velocity = 0
me.left_right_velocity = 0
me.up_down_velocity = 0
me.yaw_velocity = 0
me.speed = 0

print(me.get_battery())  # 텔로 잔여 배터리 값 출력

me.streamoff()           # 텔로 카메라 off/on
me.streamon()

#################################################################

frameWidth = width
frameHeight = height

# 전역변수로 imgContour, dir(direction) 설정
global imgContour
global dir;
# pass : 작업 수행 후 아무것도 하지 않는 상태, empty 함수로 설정
def empty(a):
    pass

# Trackbar 명칭, 크기, 수치 설정
cv2.namedWindow("HSV")
cv2.resizeWindow("HSV",640,240)
cv2.createTrackbar("HUE Min","HSV",20,179,empty)  # Trackbar 생성,
cv2.createTrackbar("HUE Max","HSV",40,179,empty)  # cv2.createTrackbar(Trackbar 이름, 창 이름, 초기값, 최대값, callback 함수)
cv2.createTrackbar("SAT Min","HSV",148,255,empty)
cv2.createTrackbar("SAT Max","HSV",255,255,empty)
cv2.createTrackbar("VALUE Min","HSV",89,255,empty)
cv2.createTrackbar("VALUE Max","HSV",255,255,empty)

cv2.namedWindow("Parameters")                    # Trackbar Parameters for Canny Edge Detector
cv2.resizeWindow("Parameters",640,240)
cv2.createTrackbar("Threshold1","Parameters",166,255,empty)
cv2.createTrackbar("Threshold2","Parameters",171,255,empty)
cv2.createTrackbar("Area","Parameters",1750,30000,empty)

# 사이즈가 다른 이미지/ 흑백 컬러 이미지를 resize 하고, 배열하는 함수
def stackImages(scale, imgArray):
    rows = len(imgArray)
    cols = len(imgArray[0])
    rowsAvailable = isinstance(imgArray[0], list)       # imgArray[0]이 list형인지 검사(T/F)
    width = imgArray[0][0].shape[1]     # 배열 전체의 열의 개수
    height = imgArray[0][0].shape[0]    # 배열 전체의 행의 개수
    if rowsAvailable:
        for x in range(0, rows):
            for y in range(0, cols):
                if imgArray[x][y].shape[:2] == imgArray[0][0].shape[:2]:          # Array Indexing
                    imgArray[x][y] = cv2.resize(imgArray[x][y], (0, 0), None, scale, scale)
                else:
                    imgArray[x][y] = cv2.resize(imgArray[x][y], (imgArray[0][0].shape[1], imgArray[0][0].shape[0]), None, scale, scale)
                if len(imgArray[x][y].shape) == 2:
                    imgArray[x][y]= cv2.cvtColor(imgArray[x][y], cv2.COLOR_GRAY2BGR)
        imageBlank = np.zeros((height, width, 3), np.uint8) # 배열을 모두 0으로, 8비트(0~255) 양수
        hor = [imageBlank]*rows
        hor_con = [imageBlank]*rows
        for x in range(0, rows):
            hor[x] = np.hstack(imgArray[x])
        ver = np.vstack(hor)
    else:                             # imgArray[0]이 list형이 아닐 때
        for x in range(0, rows):
            if imgArray[x].shape[:2] == imgArray[0].shape[:2]:
                imgArray[x] = cv2.resize(imgArray[x], (0, 0), None, scale, scale)
            else:
                imgArray[x] = cv2.resize(imgArray[x], (imgArray[0].shape[1], imgArray[0].shape[0]), None, scale, scale)
            if len(imgArray[x].shape) == 2:
                imgArray[x] = cv2.cvtColor(imgArray[x], cv2.COLOR_GRAY2BGR)
        hor = np.hstack(imgArray) # 두 배열을 하나로
        ver = hor
    return ver

# 이미지 윤곽선 검출 함수
def getContours(img,imgContour):
    global dir
    # 이미지의 윤곽선들 간의 관계 파악, cv2.findContours(이미지, Contours 검출 방법, Contours 검출 범위)
    contours, hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE) # (이미지, 외곽 윤곽선만 검출, 윤곽점들의 모든 점을 반환)
    for cnt in contours:               # cnt : 검출된 윤곽선들이 저장된 Numpy 배열
        area = cv2.contourArea(cnt)    # 윤곽선 내부의 면적 계산
        areaMin = cv2.getTrackbarPos("Area", "Parameters") # Parameters 트랙바의 값을 받아옴
        if area > areaMin:
            # 검출된 윤곽선 그리기(이미지, 윤곽선, -1 =모든 윤곽선 그리기, 색, 두께)
            cv2.drawContours(imgContour, cnt, -1, (255, 0, 255), 7)
            peri = cv2.arcLength(cnt, True)     # Contour 둘레 길이, True = 폐곡선 상태의 둘레 길이
            approx = cv2.approxPolyDP(cnt, 0.02 * peri, True) # 근사치가 적용된 윤곽선 점 배열 - 두번째 인자: 근사 정확도

            x , y , w, h = cv2.boundingRect(approx)  # 근사치가 적용된 윤곽선의 경계 사각형 그리기((x,y): 좌상단 좌표, w:폭 h:높이)
            cx = int(x + (w / 2))  # 도형 중심 x좌표
            cy = int(y + (h / 2))  # 도형 중심 y좌표

            # 카메라 영역 별 검출 반응 조건문(명령 텍스트, 검출 영역 빨갛게 변하고, dir 변수에 결과를 수치로 대입)
            if (cx < int(frameWidth/2)-deadZone and int(frameHeight/2-deadZone< cy <frameHeight/2+deadZone)):
                cv2.putText(imgContour, " GO LEFT " , (20, 50), cv2.FONT_HERSHEY_COMPLEX,1,(0, 0, 255), 3)
                cv2.rectangle(imgContour,(0,int(frameHeight/2-deadZone)),(int(frameWidth/2)-deadZone,int(frameHeight/2)+deadZone),(0,0,255),cv2.FILLED)
                dir = 1
            elif (cx > int(frameWidth / 2) + deadZone and int(frameHeight/2-deadZone< cy <frameHeight/2+deadZone)):
                cv2.putText(imgContour, " GO RIGHT ", (20, 50), cv2.FONT_HERSHEY_COMPLEX,1,(0, 0, 255), 3)
                cv2.rectangle(imgContour,(int(frameWidth/2+deadZone),int(frameHeight/2-deadZone)),(frameWidth,int(frameHeight/2)+deadZone),(0,0,255),cv2.FILLED)
                dir = 2
            elif (cy < int(frameHeight / 2) - deadZone and int(frameWidth/2-deadZone < cx <frameWidth/2 +deadZone)):
                cv2.putText(imgContour, " GO UP ", (20, 50), cv2.FONT_HERSHEY_COMPLEX,1,(0, 0, 255), 3)
                cv2.rectangle(imgContour,(int(frameWidth/2-deadZone),0),(int(frameWidth/2+deadZone),int(frameHeight/2)-deadZone),(0,0,255),cv2.FILLED)
                dir = 3
            elif (cy > int(frameHeight / 2) + deadZone and int(frameWidth/2-deadZone < cx <frameWidth/2 +deadZone)):
                cv2.putText(imgContour, " GO DOWN ", (20, 50), cv2.FONT_HERSHEY_COMPLEX, 1,(0, 0, 255), 3)
                cv2.rectangle(imgContour,(int(frameWidth/2-deadZone),int(frameHeight/2)+deadZone),(int(frameWidth/2+deadZone),frameHeight),(0,0,255),cv2.FILLED)
                dir = 4
            elif (cx < int(frameWidth/2)-deadZone and cy < int(frameHeight/2 - deadZone)):
                cv2.putText(imgContour, " GO LEFT UP ", (20, 50), cv2.FONT_HERSHEY_COMPLEX, 1,(0, 0, 255), 3)
                cv2.rectangle(imgContour,((0,0),int(frameHeight/2)-deadZone,int(frameWidth/2-deadZone)),(0,0,255),cv2.FILLED)
                dir = 5
            elif (cy > int(frameHeight / 2) + deadZone and cy < int(frameHeight/2 - deadZone)):
                cv2.putText(imgContour, " GO RIGHT UP ", (20, 50), cv2.FONT_HERSHEY_COMPLEX, 1,(0, 0, 255), 3)
                cv2.rectangle(imgContour,(frameWidth,0),(int(frameWidth/2+deadZone),int(frameHeight/2-deadZone)),(0,0,255),cv2.FILLED)
                dir = 6
            elif (cy > int(frameHeight / 2) + deadZone and cx > int(frameHeight/2 + deadZone)):
                cv2.putText(imgContour, " GO LEFT DOWN ", (20, 50), cv2.FONT_HERSHEY_COMPLEX, 1,(0, 0, 255), 3)
                cv2.rectangle(imgContour,(0,frameHeight),(int(frameWidth/2-deadZone),int(frameHeight/2 + deadZone)),(0,0,255),cv2.FILLED)
                dir = 7
            elif (cy > int(frameHeight / 2) + deadZone and cx > int(frameHeight/2 + deadZone)):
                cv2.putText(imgContour, " GO RIGHT DOWN ", (20, 50), cv2.FONT_HERSHEY_COMPLEX, 1,(0, 0, 255), 3)
                cv2.rectangle(imgContour,(int(frameWidth/2+deadZone),int(frameHeight/2)+deadZone),(frameWidth,frameHeight),(0,0,255),cv2.FILLED)
                dir = 8
                # dir 5~8 추가: 좌상/우상/좌하/우하
            else: dir=0
            # 탐지된 물체 표시, 실시간 Area, Points 값 생성
            cv2.line(imgContour, (int(frameWidth/2),int(frameHeight/2)), (cx,cy),(0, 0, 255), 3)
            cv2.rectangle(imgContour, (x, y), (x + w, y + h), (0, 255, 0), 5)
            cv2.putText(imgContour, "Points: " + str(len(approx)), (x + w + 20, y + 20), cv2.FONT_HERSHEY_COMPLEX, 0.7,(0, 255, 0), 2)
            cv2.putText(imgContour, "Area: " + str(int(area)), (x + w + 20, y + 45), cv2.FONT_HERSHEY_COMPLEX, 0.7,(0, 255, 0), 2)
            cv2.putText(imgContour, " " + str(int(x)) + " " + str(int(y)), (x - 20, y - 45), cv2.FONT_HERSHEY_COMPLEX,0.7,(0, 255, 0), 2)
        else: dir=0

# 화면 내의 구역을 선으로 나누고, 중앙점을 표시하는 함수
def display(img):
    cv2.line(img,(int(frameWidth/2)-deadZone,0),(int(frameWidth/2)-deadZone,frameHeight),(255,255,0),3)
    cv2.line(img,(int(frameWidth/2)+deadZone,0),(int(frameWidth/2)+deadZone,frameHeight),(255,255,0),3)
    cv2.circle(img,(int(frameWidth/2),int(frameHeight/2)),5,(0,0,255),5)
    cv2.line(img, (0,int(frameHeight / 2) - deadZone), (frameWidth,int(frameHeight / 2) - deadZone), (255, 255, 0), 3)
    cv2.line(img, (0, int(frameHeight / 2) + deadZone), (frameWidth, int(frameHeight / 2) + deadZone), (255, 255, 0), 3)



while True:

    # 텔로 영상을 받아서 처리하는 과정
    frame_read = me.get_frame_read()
    myFrame = frame_read.frame
    img = cv2.resize(myFrame, (width, height))
    imgContour = img.copy()
    imgHsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)       # BGR을 HSV 모드로 전환

    # Trackbar 값을 받아와서 각 변수에 저장
    h_min = cv2.getTrackbarPos("HUE Min","HSV")
    h_max = cv2.getTrackbarPos("HUE Max", "HSV")
    s_min = cv2.getTrackbarPos("SAT Min", "HSV")
    s_max = cv2.getTrackbarPos("SAT Max", "HSV")
    v_min = cv2.getTrackbarPos("VALUE Min", "HSV")
    v_max = cv2.getTrackbarPos("VALUE Max", "HSV")

    # HSV에서 BGR로 가정할 범위를 정의함
    lower = np.array([h_min,s_min,v_min])
    upper = np.array([h_max,s_max,v_max])

    # imgHsv에서 픽셀별로 검사하여 lower와 upper 사이에 해당하는 값은 그대로, 나머지 부분 = 0으로 mask에 전달
    mask = cv2.inRange(imgHsv,lower,upper)

    result = cv2.bitwise_and(img,img, mask = mask)          # mask와 원본 img 이미지를 비트 연산 = 마스킹
    mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)           # mask를 GRAY 이미지에서 BGR 모드로 전환

    # imgContour 물체 탐지 이미지 생성
    imgBlur = cv2.GaussianBlur(result, (7, 7), 1)                # GaussianBlur 라이브러리 - 이미지 노이즈 제거
    imgGray = cv2.cvtColor(imgBlur, cv2.COLOR_BGR2GRAY)          # 노이즈 제거된 이미지를 GRAY 이미지로 변환
    threshold1 = cv2.getTrackbarPos("Threshold1", "Parameters")  # Parameters Trackbar 결과값을 변수에 각각 저장
    threshold2 = cv2.getTrackbarPos("Threshold2", "Parameters")
    imgCanny = cv2.Canny(imgGray, threshold1, threshold2)        # Canny Edge Detect - 엣지 검출
    kernel = np.ones((5, 5))                                     # 1로 가득찬 5x5 shape matrix kernel 생성
    imgDil = cv2.dilate(imgCanny, kernel, iterations=1)          # imgCanny 이미지 dilate(팽창) 작업 1회 반복
    getContours(imgDil, imgContour)                              # getContours 함수에 dilated Canny 이미지와 원본 이미지 대입
    display(imgContour)                                          # display 함수에 imgContour 대입 = 이미지 경계선, 중앙점

    # Tello Flight
    if startCounter == 0:
       me.takeoff()
       startCounter = 1

    # getContours 함수에서 영역 별 검출 반응 후 Tello의 움직임 설정              
    if dir == 1:
       me.yaw_velocity = -30
    elif dir == 2:
       me.yaw_velocity = 30
    elif dir == 3:
       me.up_down_velocity= 20
    elif dir == 4:
       me.up_down_velocity= -20
    elif dir == 5:
       me.up_down_velocity= 20;  me.left_right_velocity = 20
    elif dir == 6:
       me.up_down_velocity = 20; me.left_right_velocity = -20
    elif dir == 7:
       me.up_down_velocity = -20; me.left_right_velocity = 20
    elif dir == 8:
       me.up_down_velocity = -20; me.left_right_velocity = -20
       # dir 5~8 설정
       
    else:
       me.left_right_velocity = 0; me.for_back_velocity = 0; me.up_down_velocity = 0; me.yaw_velocity = 0

    # Tello 에 속도값을 보냄
    if me.send_rc_control:
       me.send_rc_control(me.left_right_velocity, me.for_back_velocity, me.up_down_velocity, me.yaw_velocity)
    print(dir)

    # Tello 실시간 카메라 영상을 컴퓨터 화면에 배열 - stackImages 함수 사용
    stack = stackImages(0.7, ([img, result], [imgDil, imgContour]))
    cv2.imshow('Horizontal Stacking', stack)

    # 키보드 q를 누를 시 Tello 착륙 후 루프에서 벗어남
    if cv2.waitKey(1) & 0xFF == ord('q'):
        me.land()
        break

# 열린 창을 모두 닫음
cv2.destroyAllWindows()
