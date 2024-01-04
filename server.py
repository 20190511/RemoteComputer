import socket
import random
import struct
import threading
import os
import time
import traceback

DEBUG = False
if not DEBUG:
    HOST = socket.gethostbyname(socket.gethostname())
    #Fixed Host : Random Port 전달용
    FIXED_PORT = 9999
    MAXPORT = 5
    print(f"세팅 초기화 : {HOST} : {FIXED_PORT}")
    main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    main_socket.bind((HOST, FIXED_PORT))
    main_socket.listen()
    main_client, main_cli_addr = main_socket.accept()


def send_file(client_socket, filename):
    # 파일 하나 전송
    fsize = os.path.getsize(filename)
    with open (filename, "rb") as file:
        packMessage(f"파일 전송중.. {filename} , {fsize} byte", sockets=main_client)
        for data in file:
            client_socket.send(data)
    return True
'''
FIXED 9999 포트로 통신 및 Random 포트 전달

나머지 쓰레드 Socket 에서 데이터 전달 
Socket 최대 수는 5개
'''
class PortManager:
    def __init__(self):
        self.__PORT = set()
        self.__mutex = threading.Lock()
        self.__sem = threading.Semaphore(value=MAXPORT)
    def allocPort(self):
        ## Semaphore 보장 + Mutex 보장
        self.__sem.acquire()
        self.__mutex.acquire()
        
        ## Random 포트 설정
        randPort = random.randint(10000, 65535)
        while True:
            if randPort in self.__PORT:
                randPort = random.randint(10000, 65535)
                continue
            break
        self.__PORT.add(randPort)
        self.__mutex.release()
        return randPort
    def releasePort(self, port):
        self.__mutex.acquire()
        self.__PORT.remove(port)
        self.__mutex.release()
        self.__sem.release()

    def resetPort(self):
        self.__mutex.acquire()
        for pp in self.__PORT:
            main_socket.close()
        self.__sem.release()
        self.__mutex.release()
def packMessage(msg, sockets):
    ''' 메시지 길이 패킹 전송
    :param msg:
    :return:
    '''
    msg = msg.encode("utf-8")
    msg_length = len(msg)
    header = struct.pack("!I", msg_length)
    try:
        sockets.sendall(header + msg)
        return True
    except ConnectionError:
        print("error " + msg)
        return False
def transferData(PortManager:PortManager, filename, mode):
    ''' 데이터 전송 쓰레딩
    :param PortManager:
    :param filename:
    :return:
    '''
    print("??? -> " + str(PortManager))
    port = PortManager.allocPort()
    if not packMessage(f"{filename}?{port}", sockets=main_client):
        return False
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, port))

    print(f"서버가 {HOST}:{port} 연결 시도")
    server_socket.listen() # 연결 대기
    client_socket, client_address = server_socket.accept()

    print(f"{client_address} 에서 연결이 수락되었습니다 : 파일명 {filename}")
    if not os.path.isfile(filename):
        packMessage("Fail", sockets=client_socket)
        packMessage(f"{filename} 파일 전송 실패(없는 파일)")
    else:
        packMessage(mode, sockets=client_socket)
        send_file(client_socket, filename)
        print("파일 전송 완료")
        packMessage(f"{filename} 파일 전송 완료", sockets=main_client)
    server_socket.close()
    client_socket.close()
    PortManager.releasePort(port)
def sendFileTree():
    packMessage("true", sockets=main_client)

def sendFileInterface(pm, filename):
    if not os.path.exists(filename):
        return False
    ## 디렉토리인 경우
    if os.path.isdir(filename):
        for a,b,c in list(os.walk(filename)):
            for element in c:
                fpath = os.path.join(a, element)
                packMessage(fpath, sockets=main_client)
                client_thread = threading.Thread(target=transferData, args=(pm, fpath, "dir"))
                client_thread.run()
    ## 파일 인 경우
    else:
        client_thread = threading.Thread(target=transferData, args=(pm, filename, "file"))
        client_thread.run()
def optProcessor(msg: str, pm : PortManager):
    print(f"main Client : {main_client}")
    if "tree" in msg or "t " in msg:
        print("tree setting...")
        sendFileTree()
    else:
        # 데이터 전송 시작
        sendFileInterface(pm=pm, filename=str(msg))
def restartHost():
    ''' Host Restart Function'''
    global  main_client, main_socket, main_cli_addr
    print(f"세팅 초기화 : {HOST} : {FIXED_PORT}")
    main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    main_socket.bind((HOST, FIXED_PORT))
    main_socket.listen()
    main_client, main_cli_addr = main_socket.accept()
def serverInterface():
    global  main_client, main_cli_addr, main_socket
    print(f"Client{main_client}:{main_cli_addr}")
    pm = PortManager()
    while True:
        try:
            msg = main_client.recv(1024).decode("utf-8")
            print(msg)
            if msg == "-1" or "quit" in msg.lower():
                print("Server Down")
                exit(0)
            elif msg == "exit" in msg.lower():
                break
            optProcessor(msg, pm)
        except Exception as ex:
            print("!---- Server Exception Server Restart ----!")
            print(traceback.format_exc())
            return


if __name__ == "__main__":
    while True:
        serverInterface()
        restartHost()



