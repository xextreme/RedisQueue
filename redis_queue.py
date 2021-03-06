# -*- coding: utf-8 -*-
__author__ = 'tea'
import random
import redis
import time
import json

"""
模拟两个队列（key_queue是主队列，tmp_queue是临时队列）操作：
length: 计算队列包含的元素个数,用来判断是否为空
# empty: 清空队列
put: 移除并返回主队列的头元素。对元素进行处理，如果不成功，将得到的头push到临时队列
get: push元素到队列中
"""

class RedisQueues(object):  #模拟两个队列操作
    """Simple Queue with Redis Backend"""

    def __init__(self, key_queue, **redis_kwargs):
        self._db = redis.Redis(**redis_kwargs)
        self.key_queue = key_queue
        self.crash_bak = key_queue + '.crash.bak'
        self.item_to_random_key = dict()
        self.recover_crashed_items()


    def length(self):   #计算长度,用来判断是否为空,用于测试
        return self._db.llen(self.key_queue)
    def empty(self): #判断列表是否为空
        if  self._db.llen(self.key_queue) == 0:
            return True
        else:
            return False
    def put(self, item):  #插入到列表que的表尾
        self._db.rpush(self.key_queue, item)
    def delete(self): #清空列表
        print self._db.llen(self.key_queue)
        self._db.ltrim(self.key_queue, -1,0)

    def get(self): #弹出列表的头元素
        item = self._db.lpop(self.key_queue)
        random_key = '{}:{}'.format(random.randint(0, 100000000), time.time())
        self.item_to_random_key[item] = random_key
        self._db.hset(self.crash_bak, random_key, item)
        print 'from redis_queue get item and print it:', item
        return item

    def task_done(self, item): #根据结果，处理
        random_key = self.item_to_random_key.pop(item)
        self._db.hdel(self.crash_bak, random_key)

    def recover_crashed_items(self):#扫描
        random_keys = self._db.hkeys(self.crash_bak)
        now = time.time()
        for k in random_keys:
            random_int_s, in_time_s = k.split(':')
            in_time = json.loads(in_time_s)
            if now - in_time <= 3600:
                continue
            item = self._db.hget(self.crash_bak, k)
            self._db.hdel(self.crash_bak, k)
            self._db.rpush(self.key_queue, item)


if __name__ == '__main__':

    name_key = 'testA'
    name_tmp = 'testB'
    redis_que = RedisQueues(name_key)
    redis_que.delete()
    # hosts = ["http://yahoo.com", "http://google.com","http://amazon.com","http://ibm.com","http://apple.com","http://baidu.com"]
#提取已经下载的页面里面的URL，保存至队列中
    # for item in hosts:
    #     print "item1:",  item
    #     redis_que.put(item)

    print redis_que.length()