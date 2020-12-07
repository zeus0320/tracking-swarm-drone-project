class Swarm(object):

    def __init__(drones, fpath):           # 비행 기본구조 만들기

        drones.fpath = fpath
        drones.commands = self._get_commands(fpath)
        drones.manager = TelloManager()
        drones.tellos = []
        drones.pools = []
        drones.sn2ip = {
            '0TQZGANED0021X': '192.168.3.101',            #시리얼 넘버와 ip 배정
            '0TQZGANED0020C': '192.168.3.103',
        }
        drones.id2sn = {
            0: '0TQZGANED0021X',                        #시리얼 넘버 별 순서 배정
            1: '0TQZGANED0020C',

        }
        drones.ip2id = {
            '192.168.3.101': 0,                    #ip별 순서 배정
            '192.168.3.103': 1,
        }

    def start(drones):             # 군집 비행 메인 루프, 위에서 작성한 틀 바탕


        def is_invalid_command(command):     #커멘드 기본 설정
            if command is None:
                return True
            c = command.strip()
            if len(c) == 0:
                return True
            if c == '':
                return True
            if c == '\n':
                return True
            return False

        try:
            for command in self.commands:                 #커멘드 실행
                if is_invalid_command(command):
                    continue

                command = command.rstrip()

                if '//' in command:
                    drones._handle_comments(command)
                elif 'scan' in command:
                    drones._handle_scan(command)
                elif '>' in command:
                    drones._handle_gte(command)
                elif 'battery_check' in command:
                    drones._handle_battery_check(command)                 #커멘드 명령 별 조작
                elif 'delay' in command:
                    drones._handle_delay(command)
                elif 'correct_ip' in command:
                    drones._handle_correct_ip(command)
                elif '=' in command:
                    drones._handle_eq(command)
                elif 'sync' in command:
                    drones._handle_sync(command)

            drones._wait_for_all()
        except KeyboardInterrupt as ki:
            drones._handle_keyboard_interrupt()
        except Exception as e:
            drones._handle_exception(e)
            traceback.print_exc()
        finally:
            SwarmUtil.save_log(self.manager)

    def _wait_for_all(drones):              #드론이 아무 행동이 없을 때 가만히 있게 해주는 코드
       
        while not SwarmUtil.all_queue_empty(self.pools):
            time.sleep(0.5)

        time.sleep(1)

        while not SwarmUtil.all_got_response(self.manager):
            time.sleep(0.5)

    def _get_commands(drones, fpath):             #커멘드를 받게 하는 코드

        with open(fpath, 'r') as f:
            return f.readlines()

    def _handle_comments(drones, command):          #받은 커멘드를 보여주는 코드

        print(f'[COMMENT] {command}')

    def _handle_scan(drones, command):                    #커멘드 중 scan 명령실행 코드

        n_tellos = int(command.partition('scan')[2])

        drones.manager.find_avaliable_tello(n_tellos)
        drones.tellos = self.manager.get_tello_list()
        drones.pools = SwarmUtil.create_execution_pools(n_tellos)

        for x, (tello, pool) in enumerate(zip(self.tellos, self.pools)):
            self.ip2id[tello.tello_ip] = x

            t = Thread(target=SwarmUtil.drone_handler, args=(tello, pool))
            t.daemon = True
            t.start()

            print(f'[SCAN] IP = {tello.tello_ip}, ID = {x}')

    def _handle_gte(drones, command):               #각 드론의 작동 명령 >표시가 명령을 하는 역할
       
        id_list = []
        id = command.partition('>')[0]

        if id == '*':
            id_list = [t for t in range(len(self.tellos))]
        else:
            id_list.append(int(id) - 1)

        action = str(command.partition('>')[2])

        for tello_id in id_list:
            sn = self.id2sn[tello_id]
            ip = self.sn2ip[sn]
            id = self.ip2id[ip]

            self.pools[id].put(action)
            print(f'[ACTION] SN = {sn}, IP = {ip}, ID = {id}, ACTION = {action}')

    def _handle_battery_check(drones, command):              #sdk명령어로 배터리를 체크하는 코드
       
        threshold = int(command.partition('battery_check')[2])
        for queue in self.pools:
            queue.put('battery?')

        drones._wait_for_all()

        is_low = False

        for log in self.manager.get_last_logs():
            battery = int(log.response)
            drone_ip = log.drone_ip

            print(f'[BATTERY] IP = {drone_ip}, LIFE = {battery}%')

            if battery < threshold:
                is_low = True

        if is_low:
            raise Exception('Battery check failed!')
        else:
            print('[BATTERY] Passed battery check')

    def _handle_delay(drones, command):            #명령 사이에 텀을 주는 코드
        
        delay_time = float(command.partition('delay')[2])
        print(f'[DELAY] Start Delay for {delay_time} second')
        time.sleep(delay_time)

    def _handle_correct_ip(drones, command):     #ip를 확인하는 코드
        
        for queue in drones.pools:
            queue.put('sn?')

        self._wait_for_all()

        for log in self.manager.get_last_logs():
            sn = str(log.response)
            tello_ip = str(log.drone_ip)
            drones.sn2ip[sn] = tello_ip

            print(f'[CORRECT_IP] SN = {sn}, IP = {tello_ip}')

    def _handle_eq(drones, command):         #tello의 시리얼 넘버를 확인하는 코드
        
        id = int(command.partition('=')[0])
        sn = command.partition('=')[2]
        ip = self.sn2ip[sn]

        self.id2sn[id - 1] = sn

        print(f'[IP_SN_ID] IP = {ip}, SN = {sn}, ID = {id}')

    def _handle_sync(drones, command):              #각 명령에 대한 행동들 사이에 간격을 주는 코드

        timeout = float(command.partition('sync')[2])
        print(f'[SYNC] Sync for {timeout} seconds')

        time.sleep(1)

        try:
            start = time.time()

            while not SwarmUtil.all_queue_empty(drones.pools):
                now = time.time()
                if SwarmUtil.check_timeout(start, now, timeout):
                    raise RuntimeError('Sync failed since all queues were not empty!')

            print('[SYNC] All queues empty and all commands sent')

            while not SwarmUtil.all_got_response(drones.manager):
                now = time.time()
                if SwarmUtil.check_timeout(start, now, timeout):
                    raise RuntimeError('Sync failed since all responses were not received!')

            print('[SYNC] All response received')
        except RuntimeError:
            print('[SYNC] Failed to sync; timeout exceeded')

    def _handle_keyboard_interrupt(drones):     #비행 종료
        
        print('[QUIT_ALL], KeyboardInterrupt. Sending land to all drones')
