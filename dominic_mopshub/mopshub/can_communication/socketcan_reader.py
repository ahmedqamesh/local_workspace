import queue
import time

from additional_scripts import logger_setup
from can_communication.socketcan_config import can_config
from threading import Thread
import logging


class READSocketcan(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.receive_queue = queue.Queue()
        self.current_subindex = None
        self.current_channel = None
        self.cobid_ret = None

        self.read_timeout = 2000
        self.logger_thread = logging.getLogger('mopshub_log:socketcan_receive_thread')
        self.logger_thread.setLevel(logging.WARNING)
        self.running = True
        self.err_counter = 0
        self.good_frames = 0

    def run(self):
        while self.running:
            self.logger_thread.info("Receive Thread is waiting")
            can_config.sem_recv_block.acquire()
            self.logger_thread.info("Receive Thread is running")
            t0 = time.perf_counter()
            break_flag = True
            while time.perf_counter() - t0 < self.read_timeout / 1000 and break_flag:
                try:
                    can_msg = can_config.receive(self.current_channel)
                    if can_msg is not None:
                        data = can_msg.data
                        if can_msg.is_error_frame:
                            self.err_counter += 1
                        if data[3] == self.current_subindex and not can_msg.is_error_frame and \
                                can_msg.arbitration_id == self.cobid_ret:
                            self.logger_thread.info(f"Read msg from socket: {can_msg}")
                            self.receive_queue.put(can_msg)
                            self.good_frames += 1
                            break_flag = False
                except Exception as e:
                    self.logger_thread.error(f'Some Error occurred while reading Channel {self.channel}: {e}')
            self.logger_thread.info("Receive Thread is finished")
            can_config.sem_read_block.release()

    def stop(self):
        self.running = False
