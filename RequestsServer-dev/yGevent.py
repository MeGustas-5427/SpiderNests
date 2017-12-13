import gevent
import time
from queue import Queue
from gevent import monkey
import traceback

monkey.patch_socket()
monkey.patch_os()
monkey.patch_time()
monkey.patch_subprocess()

class yGevent:
    #state -> the state of the yGevent
    # 0 Run 1 Pause 2 Break
    state = 0

    #gevents -> gevents Pool
    gevents = []

    # jobs -> the Tasks to do
    jobs = Queue()

    # __init__
    # Init yGevent
    def __init__(self, Max_gevent= 10):
        self.gevents = []
        for i in range(Max_gevent):
            self.gevents.append(gevent.spawn(self._Gevent,i))

    #Three Mehod to Control the state
    def exit(self):
        self.state = 2

    def pause(self):
        self.state = 1

    def go(self):
        self.state = 0

    #Task MGR
    def task_add(self,*args,**kwargs):
        while not self.jobs.full():
            self.jobs.put([
                args[0],
                args[1],
                args[2],
                args[3:],
                kwargs
            ])
            return True
        return False

    # Worker
    def _Gevent(self,id):
        while self.state != 2:
            while self.jobs.empty() and self.state == 0:
                gevent.sleep(0.01)
            if self.state != 0:
                return
            job = self.jobs.get()
            fail = 0
            while fail < 3:
                try:
                    print("waiting ->",self.jobs.qsize())
                    resv = job[0](*job[3],**job[4])
                    gevent.spawn(job[1](resv,job[2]))
                    break
                except Exception as e:
                    #print(traceback.format_exc())
                    print(e)
                    fail += 1

            while self.state == 1:
                gevent.sleep(0.001)
            #Must Sleep
            gevent.sleep(0.001)
        return

    def joinall(self):
        while 1:
            if self.jobs.empty():
                self.state = 2
                break
            time.sleep(0.001)
        gevent.joinall(self.gevents)

    def getWorks(self):
        return self.gevents


if __name__ == "__main__":
    import requests
    import time
    s = time.time()
    a = 0
    def ck(res, source):
        global a
        a += 1
        print(res.text)

    g = yGevent(100)

    for i in range(20):
        #Function Name , CallbakcName, CallbackAddInfo
        g.task_add(requests.get,ck,["KimiYo"],"http://192.168.121.135:8080/parse?aid=2000000020&token=test404")

    time.sleep(1)
    g.exit()
    gevent.joinall(g.getWorks())
    print(time.time()-s)