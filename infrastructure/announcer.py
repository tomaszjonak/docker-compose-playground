import json
import subprocess
import queue
import threading
import logging


class DataHarvester(threading.Thread):
    def __init__(self, proc, que: queue.Queue):
        self.proc = proc
        self.queue = que
        super(DataHarvester, self).__init__()

    def run(self):
        for line in iter(self.proc.stdout.readline, b''):
            try:
                data = json.dumps(line)
                self.queue.put(data)
            except Exception as e:
                logging.exception(e)
                logging.error(self.proc.stderr.read())


class EtcdCtl(object):
    base_command = ['docker', 'exec', 'infrastructure_configuration-store_1', '/usr/local/bin/etcdctl']
    fetcher_resource = '/lb/upstream/{}'

    @classmethod
    def announce_upstream(cls, name, address):
        cmd = cls.base_command + ['mk', cls.fetcher_resource.format(name), str(address)]
        subprocess.check_call(cmd)

    @classmethod
    def deannounce_upstream(cls, name):
        cmd = cls.base_command + ['rm', cls.fetcher_resource.format(name)]
        subprocess.check_call(cmd)


class EventProcessor(threading.Thread):
    def __init__(self, que: queue.Queue):
        self.queue = que
        super(EventProcessor, self).__init__()

    def run(self):
        while True:
            curr = self.queue.get()
            if curr['service'] != 'fetcher':
                continue

            if curr['action'] == 'create':
                self.handle_start(curr)
            if curr['action'] == 'stop':
                self.handle_stop(curr)

    @staticmethod
    def handle_start(data):
        # TODO make this able to read ip address in desired network
        EtcdCtl.announce_upstream(data['name'], None)

    @staticmethod
    def handle_stop(data):
        EtcdCtl.deannounce_upstream(data['name'])


def main():
    que = queue.Queue()
    proc = subprocess.Popen(['docker-compose', 'events', '--json'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    harvester = DataHarvester(proc, que)
    processor = EventProcessor(que)

    harvester.start()
    processor.start()

    harvester.join()
    processor.join()


main()
