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
    NODE_TYPE = {"COO": 0x0000, "FFD": 0x0000,
                 "MED": 0xC000, "ZED": 0x8000, 
                 "SED": 0x4000}
    MAIN_FUNC_REG = "S0A"
    COMM_PREFIX = "AT"
    
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
        
    def register_read(self, reg):
        """
        Form register read command: ATSXX?
        Input: @reg - register name
        Output: all data in the serial port after sending a read command
        """
        command = self.COMM_PREFIX + self.MAIN_FUNC_REG + "?"
        self.write_command(command)
        
        return self.read_resp()
    
    def register_write(self, reg, value, password=None):
        """
        Form register write command: ATSXX=<value>[:<password>]
        Input:  @reg - register name
                @password - (optional) access to a register @reg might be
                provided only with a password
        Output: all data in the serial port after sending a write command
        """
        # Form register write command: ATSXX=<value>
        command = self.COMM_PREFIX + self.MAIN_FUNC_REG + "=" + value
        if password:
            command += ":" + password
        command += self.EOL_CONST
        self.write_command(command)
        
        return self.read_resp()
    
    def set_node_type(self, node_type):
        """
        Set module node type to a requested value
        Input:  @node_type - desirable node type (COO, FFD, etc)
        Output: None
        """
        if node_type not in self.NODE_TYPE.keys():
            raise NodeTypeNotFound("Wrong node type: " + str(node_type))
        resp = self.register_read(self.MAIN_FUNC_REG)
        print(resp)
        # Node type is determined by 2 most significant bits E and F
        # left all data except those bits
        MASK = 0x3FFF
        masked_value = MASK & int(resp[1], 16)
        value = "{:04X}".format(self.NODE_TYPE[node_type] | masked_value)
        resp = self.register_write(self.MAIN_FUNC_REG, value, "password")
        print(resp)
    
    def set_router(self):
        self.set_node_type("FFD")
    
    def set_sleepy(self):
        self.set_node_type("SED")
    
    def set_mobile(self):
        self.set_node_type("MED")
    
    def set_end_device(self):
        self.set_node_type("ZED")
    
    def apply_config(self, config):
        """
        Experimental
        """
        pass
