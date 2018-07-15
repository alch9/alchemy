

class Registry:
    def __init__(self):
        self.unit_map = {}
        self.flow_map = {}

    def get_unit(self, name):
        return self.unit_map[name]

    def is_unit_exists(self, name):
        return name in self.unit_map

    def is_flow_exists(self, name):
        return name in self.flow_map

    def add_unit(self, name, u):
        self.unit_map[name] = u

    def add_flow(self, flow_name, flow):
        self.flow_map[flow_name] = flow

    def get_flow(self, flow_name):
        return self.flow_map[flow_name]


