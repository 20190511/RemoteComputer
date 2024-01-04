import socket
import struct
import time


INIT_PORT = 9999
HOST = "172.29.64.1"
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def unpackMsg(sockets=client_socket):
    header = sockets.recv(4)
    msg_length = struct.unpack("!I", header)[0]
    msg = sockets.recv(msg_length).decode("utf-8")
    return msg

def receive_file(server_client, filename):
    print(f"엔터 시 {filename}으로 저장됩니다..")
    new_name = input("새로운 경로이름 >>")

    if new_name != "":
        filename = new_name

    if unpackMsg(server_client) == "Fail":
        print(f"fail to receive File : {filename}")
        return

    with open(filename, "wb") as file:
        print(unpackMsg())
        while True:
            try:
                data = server_client.recv(1024)
            except socket.timeout:
                break
            if not data:
                break
            file.write(data)


client_socket.connect((HOST, INIT_PORT))
print(f"서버에 {HOST}:{INIT_PORT} 로 연결되었습니다")


def getData(message: str):
    response = unpackMsg()
    print("서버 응답 ====> " + response)
    filename, port = response.split("?")
    if filename != message:
        print("Error Filename : " + filename)
        return False

    receive_cliSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    receive_cliSocket.connect((HOST, int(port)))

    receive_file(receive_cliSocket, filename)  #데이터 전송 수락

    print(unpackMsg())
    receive_cliSocket.close()
    return True

def getTree():
    print(unpackMsg())

def receiveData():
    message = ""
    while message == "":
        message = input("파일 경로 >> ")
    client_socket.send(message.encode("utf-8"))
    if message == "1" or "exit" in message.lower():
        client_socket.close()
        exit(0)
    if "tree" in message:
        getTree()
    else:
        getData(message)


if __name__ == "__main__":
    ## init FIXED PORT
    while True:
        receiveData()

