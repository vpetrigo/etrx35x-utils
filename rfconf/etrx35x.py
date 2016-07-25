#!/usr/bin/env python3
# coding=utf-8

import xml.etree.ElementTree as ElemTree
import serial


class ConfFileError(Exception):
    pass


class NodeTypeNotFound(Exception):
    pass


class ModuleConfigReader:
    _XMLFileHeaderTag = "rfconfig"
    _XMLNodeTag = "node"
    _XMLNodeTypeAttrName = "type"

    def __init__(self, config_file: "XML file with configuration"):
        self.config_file = config_file

    def read_config(self):
        self.conf_tree = ElemTree.parse(self.config_file)
        if self.conf_tree.getroot().tag != self._XMLFileHeaderTag:
            raise ConfFileError("unsupported XML file format")

    def get_node_conf(self, node_type: "node type - COO, FFD, etc"):
        for node in self.conf_tree.iter(self._XMLNodeTag):
            if node.get(self._XMLNodeTypeAttrName) == node_type:
                config = []
                for conf_line in list(node):
                    config.append(
                        dict(((tag, val) for tag, val in conf_line.items()),
                             value=conf_line.text.strip())
                    )
                return config
        # if there is no such node type in the config file
        raise NodeTypeNotFound(
            "no such node {} in the XML "
            "configuration file".format(node_type))

    def get_avail_nodes(self):
        available_nodes = self.conf_tree.findall("node")

        return [i.get("type") for i in available_nodes]


class ModuleInterface:
    EOL_CONST = "\r\n"
    
    def __init__(self, port, baudrate=19200, xonxoff=False, rtscts=False):
        self.module_com = serial.Serial(port, baudrate=baudrate, timeout=0.05, 
                                        xonxoff=xonxoff, rtscts=rtscts)
    
    def write_command(self, command):
        command += self.EOL_CONST
        n_bytes = self.module_com.write(bytes(command, "utf-8"))
        assert n_bytes == len(command), "Something wrong during write"
        
    def read_resp(self):
        data = []
        for line in iter(self.module_com):
            data.append(line)
        
        return data
