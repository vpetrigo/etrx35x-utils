#!/usr/bin/env python3
# coding=utf-8

import re
import xml.etree.ElementTree as ElemTree
import serial
import serial.threaded
import traceback


class ConfFileError(Exception):
    pass


class NodeTypeNotFound(Exception):
    pass


class FirmwareError(Exception):
    pass


class ConfigIterator:
    PASSWORD_FIELD = "password"
    TYPE_FIELD = "type"
    REGISTER_NAME_FIELD = "name"
    OVERWRITE_FIELD = "overwrite"
    VALUE_FIELD = "value"

    def __init__(self, conf):
        """
        Construct iterator through a given configuration
        In: @conf - a list of dictionaries with configuration values
        """
        self.conf = conf
        # register to be configured
        self.reg = None
        # value to be written
        self.value = None
        # password to be used
        self.password = None
        # flag for doing OR with previously stored value in
        # a S-register
        self.overwrite = True

    def __iter__(self):
        """
        Iterate through the whole @self.conf list and
        extract necessary information that might be used
        by access via a particular field
        """
        for item in self.conf:
            self.password = item.get(self.PASSWORD_FIELD)
            self.value = item[self.VALUE_FIELD]

            if item[self.TYPE_FIELD] == "int":
                self.value = int(self.value)
            elif item[self.TYPE_FIELD] == "hex":
                self.value = int(self.value, 16)

            self.reg = item[self.REGISTER_NAME_FIELD]
            overwrite_flag = item.get(self.OVERWRITE_FIELD)
            if (overwrite_flag is not None and
                (overwrite_flag.casefold() == "n" or
                 overwrite_flag.casefold() == "no")):
                self.overwrite = False
            else:
                self.overwrite = True

            yield self
        else:
            raise StopIteration


class ETRXModuleConfigReader:
    _XMLFileHeaderTag = "rfconfig"
    _XMLNodeTag = "node"
    _XMLNodeTypeAttrName = "type"
    _XMLRegisterTagName = "reg"

    def __init__(self, config_file: "XML file with configuration"):
        self.conf_tree = ElemTree.parse(config_file)
        if self.conf_tree.getroot().tag != self._XMLFileHeaderTag:
            raise ConfFileError("unsupported XML file format")

    def get_node_conf(self, node_type: "node type - COO, FFD, etc"):
        for node in self.conf_tree.iter(self._XMLNodeTag):
            if node.get(self._XMLNodeTypeAttrName) == node_type:
                config = []
                for conf_line in list(node):
                    if conf_line.tag != self._XMLRegisterTagName:
                        raise ConfFileError(
                            "Node configuration only support <reg> tag")
                    # add all parameters to the configuration list
                    config.append(
                        dict(((tag, val) for tag, val in conf_line.items()),
                             value=conf_line.text.strip()))
                return ConfigIterator(config)
        # if there is no such node type in the config file
        raise NodeTypeNotFound(
            "no such node {} in the XML "
            "configuration file".format(node_type))

    def get_avail_nodes(self):
        available_nodes = self.conf_tree.findall("node")

        return [i.get("type") for i in available_nodes]


class ETRXModule:
    EOL_CONST = "\r"
    NODE_TYPE = {"COO": 0x0000, "FFD": 0x0000,
                 "MED": 0xC000, "ZED": 0x8000,
                 "SED": 0x4000}
    MAIN_FUNC_REG = "S0A"
    COMM_PREFIX = "AT"
    # position of a register value in a response from module
    # with !command echo on!
    RESP_REGISTER_POS = 1
    RESP_STATUS_POS = -1

    def __init__(self, port, *, node_type="FFD",
                 baudrate=19200, timeout=1, xonxoff=True, **kwargs):
        self.module_com = serial.serial_for_url(port, baudrate=baudrate,
                                                timeout=timeout,
                                                xonxoff=xonxoff,
                                                **kwargs)
        # by default let it be all devices to be routers
        self.node_type = node_type
        # send appropriate command to set up node type in the hardware
        # to be in a sync state with it
        self.set_node_type(self.node_type)

    def get_serial_interface(self):
        return self.module_com

    def write_command(self, command):
        command += self.EOL_CONST
        n_bytes = self.module_com.write(bytes(command, "utf-8"))
        assert n_bytes == len(command), "Something wrong during write"

    def reader(self):
        line = ""
        while True:
            line = self.readline()
            if line:
                yield line

    def is_statusline(self, line):
        if line == "OK" or line.split(":")[0] == "ERROR":
            return True
        return False

    def read_resp(self):
        data = []
        for line in self.reader():
            data.append(line)
            # usually all commands end with the "OK" or "ERROR:XX" status code
            if self.is_statusline(line):
                break

        return data

    def register_read(self, reg):
        """
        Form register read command: ATSXX?
        Input: @reg - register name
        Output: all data in the serial port after sending a read command
        """
        command = self.COMM_PREFIX + reg + "?"
        self.write_command(command)
        resp = self.read_resp()
        self._check_response(resp)

        return resp

    def register_write(self, reg, value, password=None):
        """
        Form register write command: ATSXX=<value>[:<password>]
        Input:  @reg - register name
                @password - (optional) access to a register @reg might be
                provided only with a password
        Output: None
        """
        # Form register write command: ATSXX=<value>
        command = self.COMM_PREFIX + reg + "=" + str(value)
        if password:
            command += ":" + password
        command += self.EOL_CONST
        self.write_command(command)
        resp = self.read_resp()
        self._check_response(resp)

        return resp

    def set_node_type(self, node_type):
        """
        Set module node type to a requested value
        Input:  @node_type - desirable node type (COO, FFD, etc)
        Output: None
        """
        if node_type not in self.NODE_TYPE.keys():
            raise NodeTypeNotFound("Wrong node type: " + str(node_type))

        self.node_type = node_type
        resp = self.register_read(self.MAIN_FUNC_REG)
        # Node type is determined by 2 most significant bits E and F
        # left all data except those bits
        MASK = 0x3FFF
        masked_value = (MASK & int(resp[self.RESP_REGISTER_POS], 16) |
                        self.NODE_TYPE[node_type])
        value = self._determine_new_value(resp[self.RESP_REGISTER_POS],
                                          masked_value, False)
        self.register_write(self.MAIN_FUNC_REG, value, "password")

    def set_router(self):
        self.set_node_type("FFD")

    def set_sleepy(self):
        self.set_node_type("SED")

    def set_mobile(self):
        self.set_node_type("MED")

    def set_end_device(self):
        self.set_node_type("ZED")

    def _check_response(self, resp):
        status_code = resp[self.RESP_STATUS_POS]
        if status_code != "OK":
            raise FirmwareError(status_code)

    def _determine_reg_size(self, resp_reg_value):
        return len(resp_reg_value.strip())

    def _determine_new_value(self, resp_value, new_value, overwrite):
        resp_len = self._determine_reg_size(resp_value)
        # if we have a string put it back as is, otherwise we should
        # add leading zeros
        format_string = "{0:0{1}X}" if not isinstance(new_value, str) else "{}"
        value = new_value if overwrite else new_value | int(resp_value, 16)

        return format_string.format(value, resp_len)

    def write_config(self, config_reader):
        dev_config = config_reader.get_node_conf(self.node_type)

        for conf_line in dev_config:
            new_reg_val = conf_line.value
            # we have to read a register here for determining value size
            resp = self.register_read(conf_line.reg)
            print(resp)
            resp_reg_value = resp[self.RESP_REGISTER_POS]
            new_reg_val = self._determine_new_value(resp_reg_value,
                                                    new_reg_val,
                                                    conf_line.overwrite)
            self.register_write(conf_line.reg, new_reg_val, conf_line.password)

    def readline(self):
        return self.module_com.readline().decode("utf8").strip()


class ETRXModuleReader(serial.threaded.LineReader):
    def __init__(self, module_inst):
        super().__init__()
        self.module_inst = module_inst

    def __call__(self):
        return self

    def connection_made(self, transport):
        super().connection_made(transport)
        print("Connection with the module opened")

    def handle_line(self, data):
        print("line received: {}".format(repr(data)))

    def connection_lost(self, exc):
        if exc:
            traceback.print_exc(exc)
        print("Connection with the module closed")


def response_split(resp):
    """
    Split module response so that in the output list
    there are only info prefix and values without punctuation
    """
    return re.split("\W+", resp)
