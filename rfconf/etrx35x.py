#!/usr/bin/env python3
# coding=utf-8

import xml.etree.ElementTree as ElemTree


class ConfFileError(Exception):
    pass


class ModuleConfigurator:
    _XMLFileHeaderTag = "rfconfig"

    def __init__(self, config_file: "XML file with configuration"):
        self.config_file = config_file

    def read_config(self):
        self.conf_tree = ElemTree.parse(self.config_file)
        if self.conf_tree.getroot().tag != self._XMLFileHeaderTag:
            raise ConfFileError("unsupported XML file format")

    def get_node_conf(self, node_type: "node type - COO, FFD, etc"):
        for node in self.conf_tree.iter("node"):
            print(node.tag, node.attrib)
            if node.get("type") == node_type:
                return list(node)

    def get_avail_nodes(self):
        available_nodes = self.conf_tree.findall("node")

        return [i.get("type") for i in available_nodes]
