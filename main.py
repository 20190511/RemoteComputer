import os
from collections import deque

LOGIN_DIR_NAME = "login"

class findPath:
    def __init__(self, path=os.getcwd()):
        if not os.path.isfile(path):
            print("Not This Directory" , path)
            self.__del__()
            return
        self.dirList = os.listdir(path)

    def __del__(self):
        print("End Search Object")

    def findFile(self, name:str):
        if name in self.dirList:
            print("find")
        else:
            print("cant find")

    def printList(self):
        print(self.dirList)

    def find(self, name:str):
        ## BFS 방식으로 File Searching
        q = deque()


class loginInterface:
    def __init__(self):
        self.checkLogin = False
        self.checkLoginFile()

    def checkLoginFile(self):
        l_dir = os.path.join(os.getcwd(), LOGIN_DIR_NAME)

        # make login session
        while not os.path.isdir(l_dir):
            print("make dir : ", l_dir)
            os.mkdir(l_dir)



        print(l_dir)


if __name__ == "__main__":
    path = findPath("D:\\Bae's Fil")
    path.findFile("2015년")

    l = loginInterface()



print(os.listdir(os.getcwd()))