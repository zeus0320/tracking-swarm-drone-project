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
