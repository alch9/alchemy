

class Registry:
    def __init__(self):
        self.unit_map = {}
        self.flow_map = {}

def is_unit_exists(reg, name):
    return name in reg.unit_map

def is_flow_exists(reg, name):
    return name in reg.flow_map

def get_unit(reg, name):
    return reg.unit_map[name]

def add_unit(reg, name, u):
    reg.unit_map[name] = u

def add_flow(reg, flow_name, flow):
    reg.flow_map[flow_name] = flow

def get_flow(reg, flow_name):
    return reg.flow_map[flow_name]

def get_unit_list(reg):
    return reg.unit_map