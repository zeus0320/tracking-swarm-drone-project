from djitellopy import tello
import cv2

width = 320
height = 240
startcounter = 0  #비행 시 0, 테스트시 1

me = Tello()
me.connect()
me.for_back_v = 0
me.left_right_v = 0
me.up_down_v = 0
me.yaw_v = 0
me.speed = 0

print(me.get_battery())

me.streamoff()
me.streamon()

while True:
    frame_read = me.get_frame_read()
    myFrame = frame_read.frame
    img = cv2.resize(myFrame, (width, height))
    
    if startCounter == 0:
        me.takeoff()
        time.sleep(3)
        me.rotate_clockwise(90)
        time.sleep(3)
        me.move_left(45)
        time.sleep(3)
        me.land()
        startCounter = 1
        
    cv2.imshow("Myresult", img)
    
    if cv2.waitkey(1) & 0xFF == ord('q'):
        me.land()
        break
        
