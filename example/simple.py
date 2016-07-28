#!/usr/bin/env python3
# coding=utf-8

import rfconf
import serial.tools.list_ports


def main():
    configurator = rfconf.ETRXModuleConfigReader("sensor_nwk.xml")
    supp_nodes = dict(enumerate(configurator.get_avail_nodes()))
    node_available = len(supp_nodes)
    USR_PROMPT = "How would you like to configure that node (-1 - skip): "
    NODE_FORMAT = "Configuration XML file support {} nodes:"

    if node_available > 0:
        print(NODE_FORMAT.format(node_available))
        print(supp_nodes)

        for com in serial.tools.list_ports.comports():
            if com.description.split()[0] == "Telegesis":
                tgmodule = rfconf.ETRXModule(com.device)
                print(com.description)
                usr_choice = int(input(USR_PROMPT))
                if usr_choice != -1:
                    tgmodule.set_node_type(supp_nodes[usr_choice])
                    tgmodule.write_config(configurator)
    else:
        print("There is nothing to do")

if __name__ == "__main__":
    main()
