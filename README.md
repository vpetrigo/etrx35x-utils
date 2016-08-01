# Python interface for Silabs' ETRX357 modules

That module has simple interface for working with ETRX357 modules.
It supports several helper classes:

```python
class ETRXModule:
    ...
    
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
