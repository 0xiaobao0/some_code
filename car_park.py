import numpy
import time
import random
from multiprocessing import JoinableQueue, Process
from concurrent.futures import ThreadPoolExecutor
import threading
from threading import Thread

class Car():
    def __init__(self, num):
        # 车牌号
        self.car_num = num
        # 停车位车位号
        self.parking_num = None
        self.driving()

    def driving(self):
        print('汽车:{}行驶中...'.format(self.car_num))
        time.sleep(random.random())

    def parking(self):
        time.sleep(random.uniform(2, 2.5))


class Car_park(object):

    def __init__(self, num):
        self._parking_space_num = num
        self._space_used = {i:None for i in range(1, num + 1)}
        self.empty_num = threading.Semaphore(num)

    #等待进入，若停车场车位资源不足，则阻塞线程等待，直至其他线程释放资源。若有多个线程等待资源，遵循先来先服务的原则
    def waiting(self, car):
        print('汽车:{}等待车位...'.format(car.car_num))
        self.empty_num.acquire()
        self.car_coming(car)
        print('汽车:{}获得车位'.format(car.car_num))
        car.parking()
        self.car_leaving(car)
        self.empty_num.release()

    def car_coming(self, car):
        number = self.display(car)
        car.parking_num = number
        self._space_used[number] = car

    def display(self, car):
        empty_space_list = [i for i in self._space_used.keys() if self._space_used[i] is None]
        print('当前可用车位数：{}'.format(len(empty_space_list)))
        parking_lot_num = numpy.random.choice(empty_space_list, size=1, replace=False)[0]
        print('已为汽车:{}选择车位：{}'.format(car.car_num, parking_lot_num))
        return parking_lot_num

    def car_leaving(self, car):
        self._space_used[car.parking_num] = None
        print('汽车:{}已离开停车场'.format(car.car_num))

#生产者，产生开向停车场的车，用队列做缓存，将产生的汽车对象储存之队列
class Worker():
    def produce(self, car_num, queue):
        for i in range(1, car_num + 1):
            queue.put(Car(i))
        queue.join()

#消费者，从队列中取汽车对象，生成线程
class Consumer():
    def consume(self, park_space_num, car_num, queue):
        if park_space_num <= 0:
            print('车位资源数不能小于等于0')
            return
        car_park = Car_park(park_space_num)
        executor = ThreadPoolExecutor(max_workers=4*park_space_num)
        while True:
            try:
                car = queue.get()
                executor.submit(car_park.waiting, (car))
                if car.car_num == car_num:
                    break
            finally:
                queue.task_done()


if __name__ == '__main__':
    park_space_num = 5 # int(input('请输入停车场车位数：'))
    car_num = 20 # int(input('请输入车辆数目：'))
    q = JoinableQueue()

    w = Worker()
    worker = Process(target=w.produce, args=(car_num, q))
    worker.start()

    c = Consumer()
    consumer = Process(target=c.consume, args=(park_space_num, car_num, q))
    consumer.start()