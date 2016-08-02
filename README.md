# Python interface for Silabs' ETRX357 modules

That module has simple interface for working with ETRX357 modules.
It supports several helper classes:

**1**. `class ETRXModule` - interface for ETRX35X module that utilizes [pySerial](https://github.com/pyserial/pyserial) module

Example:
```python
import rfconf

def create_module_inst():
    # connect to the module on the COM1
    module = rfconf.ETRXModule("COM1")
    return module

def access_module_register(module):
    # read the register S00
    reg = module.register_read("S00")
    return reg

def write_module_register(module, data):
    # write data to module's register
    module.register_write("S00", data)
```

**2**. `class ETRXModuleConfigReader` - simple interface for reading initial configuration from XML files for different ZigBee node types that available in the standard modules firmware. Available methods:
  - `get_node_conf(node_type: "node type - COO, FFD, etc")` - read configuration branch for the particular `node_type`
  - `get_avail_nodes()` - returns list of supported node types from a XML file

Example of XML file:
```xml
<!-- Header name. In current version it must be 'rfconf' -->
<rfconfig>
  <!-- Start config for a Coordinator (COO) node -->
  <node type="COO">
    <reg name="S09" password="password" overwrite="y" type="string">
      12341234123412341234123412341234
    </reg>
    <reg name="S0A" password="password" overwrite="n" type="hex">
      0114
    </reg>
    <reg name="S01" overwrite="y" type="int">
      8
    </reg>
  </node>
  <!-- Start config for a Router (FFD) node -->
  <node type="FFD">
    <reg name="S09" password="password" overwrite="y" type="string">
      12341234123412341234123412341234
    </reg>
    <reg name="S0A" password="password" overwrite="n" type="hex">
      0114
    </reg>
    <reg name="S01" overwrite="y" type="int">
      3
    </reg>
  </node>
  <!-- Start config for a Sleepy end device -->
  <node type="SED">
    <reg name="S09" password="password" overwrite="y" type="string">
      12341234123412341234123412341234
    </reg>
    <reg name="S0A" password="password" overwrite="n" type="hex">
      0114
    </reg>
    <reg name="S01" overwrite="y" type="int">
      3
    </reg>
  </node>
</rfconfig>
```

Available tags:
- `<node>` - determine node type by adding necessary attribute `type="..."`
- inside `<node>` section it is possible to determine module's internal registers value. For that use the `<reg>` tag. Necessary attributes:
    - `name="SXX"` - an internal S-register name (ex.: `name="S00")
    - `password="..."` - if a register is protected, provide password info
    - `overwrite="..."` - possible values are `y/n`. This attribute shows whether it is necessary to save previously stored value by doing logical OR operation with a new value or it must be overwritten
    - `type="..."` - type of register values. In the current version supports only `hex`, `string`, `int`. It determines how the obtained value must be interpreted during the processing

Example:
```python
# read configuration from the file conf.xml
configurator = rfconf.ETRXModuleConfigReader("conf.xml")
# get supported nodes
supp_nodes = dict(enumerate(configurator.get_avail_nodes()))
print(supp_node)
```

# Useful links

- [AT-commands Dictionary](http://www.wless.ru/files/ZigBee/Firmware/TG-ETRXn-R309-Commands.pdf) for ETRX35X modules

# Contributing

Please fork this repository and contribute back using [pull requests](https://github.com/vpetrigo/etrx35x-utils/pulls). Features can be requested by using [issues](https://github.com/vpetrigo/etrx35x-utils/issues). All code, comments, and critiques are greatly appreciated.
