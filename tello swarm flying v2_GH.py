scan 
bettary check #뒤에 숫자 입력
correct_ip 
1 = 
2 = 
3 = 
#각각 ip작성

while True:   
     try:  
         if keyboard.is_pressed('w'): 
             wpressed == True 
             while wpressed == True: 
                 print("forward") 
                 forward() 
         elif keyboard.is_pressed('s'): 
             spressed = True 
             while spressed == True: 
                 print("backward") 
                 back() 
         elif keyboard.is_pressed('z'): 
             print('up 20') 
             up() 
         elif keyboard.is_pressed('x'): 
             print('down 20') 
             down() 
         elif keyboard.is_pressed('d'): 
             print('cw 5') 
             cw() 
         elif keyboard.is_pressed('a'): 
             print('ccw 5') 
             ccw() 
         elif keyboard.is_pressed('t'): 
             print('takeoff') 
             takeoff() 
         elif keyboard.is_pressed('l'): 
             print('land') 
             land() 
         elif keyboard.is_pressed('c'): 
             print('command') 
             start() 
         else: 
             pass 
     except: 
         break 




*>take off   # 이륙 

*>up to 100
sync 10
1>left 100   1번기체 위치 세팅
sync 10

2>forward 200   2번기체 위치 세팅
sync 10

3>up to 50     3번기체 위치 세팅 
sync 10


*> #opencv 구동 
sync 10
*> #image tracking 시작 

*>land
