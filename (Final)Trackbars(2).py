# Trackbar 명칭, 크기, 수치 설정
cv2.namedWindow("HSV")
cv2.resizeWindow("HSV",640,240)
cv2.createTrackbar("HUE Min","HSV",20,179,empty)  # Trackbar 생성
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
