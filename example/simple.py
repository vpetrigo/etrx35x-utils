#!/usr/bin/env python3
# coding=utf-8

import rfconf
import serial.tools.list_ports


def main():
    configurator = rfconf.ModuleConfigReader("sensor_nwk.xml")
    supp_nodes = configurator.get_avail_nodes()
    supp_nodes = dict(enumerate(supp_nodes))
    
    if len(supp_nodes) > 0:
        print("Configuration XML file support {} nodes:".format(len(supp_nodes)))
        print(supp_nodes)

        for com in serial.tools.list_ports.comports():
            if com.description.split()[0] == "Telegesis":
                tgmodule = rfconf.ModuleInterface(com.device)
                print(com.description)
                usr_choice = int(input("How would you like to configure that node: "))
                tgmodule.set_node_type(supp_nodes[usr_choice])
                tgmodule.write_config(configurator)
    else:
        print("There is nothing to do")

if __name__ == "__main__":
    main()
