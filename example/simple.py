#!/usr/bin/env python3
# coding=utf-8

import rfconf
import serial
import serial.tools.list_ports


def write_conf(device, node_type, config):
    dev_config = config.get_node_conf(node_type)
    device.set_node_type(node_type)

    for conf_line in dev_config:
        new_reg_val = conf_line["value"]
        if conf_line["overwrite"] == 'n':
            if conf_line["type"] == "int":
                resp = device.register_read(conf_line["name"])
                new_reg_val = "{:04X}".format(int(new_reg_val, 16) | int(resp[1], 16))

        password = conf_line.get("password")
        device.register_write(conf_line["name"], new_reg_val, password)


def main():
    configurator = rfconf.ModuleConfigReader("conf.xml")
    supp_nodes = configurator.get_avail_nodes()

    if len(supp_nodes) > 0:
        print("Configuration XML file support {} nodes:".format(len(supp_nodes)))
        supp_nodes = dict(enumerate(supp_nodes))
        print(supp_nodes)

    for com in serial.tools.list_ports.comports():
        if com.description.split()[0] == "Telegesis":
            tgmodule = rfconf.ModuleInterface(com.device)
            usr_choice = int(input("How would you like to configure that node: "))
            write_conf(tgmodule, supp_nodes[usr_choice], configurator)

if __name__ == "__main__":
    main()
