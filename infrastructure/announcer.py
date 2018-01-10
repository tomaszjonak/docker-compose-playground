import json
import subprocess
import queue
import threading
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(name)s|%(threadName)s] %(levelname)s: %(message)s')


class DataHarvester(threading.Thread):
    def __init__(self, proc, que: queue.Queue):
        self.proc = proc
        self.queue = que
        super(DataHarvester, self).__init__()

    def run(self):
        for line in iter(self.proc.stdout.readline, b''):
            try:
                data = json.loads(line.decode())
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
        try:
            subprocess.check_call(cmd)
        except subprocess.CalledProcessError as e:
            logging.exception(e)

    @classmethod
    def deannounce_upstream(cls, name):
        cmd = cls.base_command + ['rm', cls.fetcher_resource.format(name)]
        try:
            subprocess.check_call(cmd)
        except subprocess.CalledProcessError as e:
            logging.exception(e)


class EventProcessor(threading.Thread):
    def __init__(self, que: queue.Queue):
        self.queue = que
        super(EventProcessor, self).__init__()

    def run(self):
        while True:
            curr = self.queue.get()
            logging.debug('Caught event: {}'.format((curr['action'], curr['service'])))
            if curr['service'] != 'fetcher':
                continue

            if curr['action'] == 'start':
                self.handle_start(curr)
            if curr['action'] == 'kill':
                self.handle_stop(curr)

    @staticmethod
    def handle_start(data):
        # TODO make this able to read ip address in desired network
        EtcdCtl.announce_upstream(data['attributes']['name'], data['attributes']['name'])

    @staticmethod
    def handle_stop(data):
        EtcdCtl.deannounce_upstream(data['attributes']['name'])


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
