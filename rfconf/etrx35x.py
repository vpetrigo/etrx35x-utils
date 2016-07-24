#!/usr/bin/env python3
# coding=utf-8

import xml.etree.ElementTree as ElemTree


class ConfFileError(Exception):
    pass


class NodeTypeNotFound(Exception):
    pass


class ModuleConfigurator:
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
            raise NodeTypeNotFound(
                "no such node {} in the XML "
                "configuration file".format(node_type))

    def get_avail_nodes(self):
        available_nodes = self.conf_tree.findall("node")

        return [i.get("type") for i in available_nodes]
