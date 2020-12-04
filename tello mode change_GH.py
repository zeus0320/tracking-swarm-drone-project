import socket  #ip주소와 포트를 이용하여 통신을 하게 해줌

def set_ap(ssid, password):    #set_ap 지정

    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # cmd로 보내기 위한 socket
    my_socket.bind(('', 8889))
    cmd_str = 'command'      #command 명령어 전달
    print ('sending command %s' % cmd_str)   #cmd화면에 표시
    my_socket.sendto(cmd_str.encode('utf-8'), ('192.168.10.1', 8889))  #utf-8을 이용해 인코딩함 tello 포트는 8889
    response, ip = my_socket.recvfrom(100)  #응답
    print('from %s: %s' % (ip, response))

    cmd_str = 'ap %s %s' % (ssid, password)  #네트워크 이름과 비번을 이용하여 ap모드를 설정
    print ('sending command %s' % cmd_str)
    my_socket.sendto(cmd_str.encode('utf-8'), ('192.168.10.1', 8889))  #ap모드 이후 네트워크와 연결 확인
    response, ip = my_socket.recvfrom(100)
    print('from %s: %s' % (ip, response))


set_ap('Tello_Nest', 'tellotello')  #연결하고자 하는 네트워크 이름과 비번 작성
