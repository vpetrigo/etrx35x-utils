#!/usr/bin/env python3
# coding=utf-8

import rfconf
import serial.threaded


class TemperatureReader(rfconf.ETRXModuleReader):
    TEMP_POS = 2
    NODEID_POS = 0

    def handle_line(self, data):
        if not data:
            return

        info, *payload = rfconf.response_split(data)
        if info == "SDATA":
            nodeid = payload[self.NODEID_POS]
            temp = int(payload[self.TEMP_POS], 16)
            # convert temperature value according to the description for LM61
            temp = (temp / 10 - 600) / 10
            print("Node: {} - Temperature: {:.2f}".format(nodeid, temp))


def leave_network(node):
    LEAVE_NWK_CMD = "AT+DASSL"
    node.write_command(LEAVE_NWK_CMD)
    resp = node.read_resp()
    # by default AT+DASSL command in case of success prompt LeftPAN message
    if resp[-1] == "OK":
        msg = ""
        while not msg:
            msg = node.readline()
        print(msg)
    else:
        print(resp[-1])


def create_network(coordinator):
    NWK_INFO_POS = 1
    NWK_PARAMS_POS = 1
    CREATE_NWK_CMD = "AT+EN"
    coordinator.write_command(CREATE_NWK_CMD)
    resp = coordinator.read_resp()
    if resp[-1] == "OK":
        nwk_info = resp[NWK_INFO_POS]
        info, ch, sid, lid = rfconf.response_split(nwk_info)
        print("network created - ", end="")
        print("ch: {}, PANID: {}, EUI64: {}".format(ch, sid, lid))


def main():
    coo_node = rfconf.ETRXModule("COM22", node_type="COO")
    reader = TemperatureReader(coo_node)
    create_network(coo_node)
    ser = coo_node.get_serial_interface()
    reader_thread = serial.threaded.ReaderThread(ser, reader)

    with reader_thread as protocol:
        reader_thread.join()

if __name__ == "__main__":
    main()
