#!/usr/bin/env python3
# coding=utf-8

import sys
import time
import traceback
import rfconf
import serial.threaded

def main():
    coo_node = rfconf.ThreadedModuleInterface("COM22", node_type="COO")
    reader_thread = serial.threaded.ReaderThread(coo_node.get_serial_interface(), coo_node)

    with reader_thread as protocol:
        reader_thread.join()
    
if __name__ == "__main__":
    main()