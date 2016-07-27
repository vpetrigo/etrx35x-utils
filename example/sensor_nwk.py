#!/usr/bin/env python3
# coding=utf-8

import sys
import time
import traceback
import rfconf
import serial.threaded


class PrintLines(serial.threaded.LineReader):
    def connection_made(self, transport):
        super(PrintLines, self).connection_made(transport)
        sys.stdout.write('port opened\n')
        self.write_line('hello world')

    def handle_line(self, data):
        sys.stdout.write('line received: {}\n'.format(repr(data)))

    def connection_lost(self, exc):
        if exc:
            traceback.print_exc(exc)
        sys.stdout.write('port closed\n')

# ser = serial.serial_for_url('COM22', baudrate=19200, timeout=1)
coo_node = rfconf.ThreadedModuleInterface("COM22", node_type="COO")
reader_thread = serial.threaded.ReaderThread(coo_node.module_com, coo_node)

with reader_thread as protocol:
    reader_thread.join()