#!/usr/bin/env python3
# coding=utf-8

import rfconf
import serial
import serial.tools.list_ports


def main():
    configurator = rfconf.ModuleConfigReader("conf.xml")
    configurator.read_config()
    supp_nodes = configurator.get_avail_nodes()

    if len(supp_nodes) > 0:
        print("Configuration XML file support {} nodes:".format(len(supp_nodes)))
        for (id, node) in enumerate(supp_nodes):
            print("#{}: {}".format(id + 1, node))

    print(configurator.get_node_conf("COO"))
    
    for com in serial.tools.list_ports.comports():
        if com.description.split()[0] == "Telegesis":
            tgmodule = rfconf.ModuleInterface(com.device)
            tgmodule.write_command("ATI")
            print(tgmodule.read_resp())

if __name__ == "__main__":
    main()
