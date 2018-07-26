
from alchemy.unit import UnitInstance

class Flow:
    def __init__(self, name):
        self.name = name
        self.input = None
        self.output = None
        self.defaults = {}
        self.ui_list = []
    
    def get_args(self):
        if self.input is None:
            return []

        if not self.defaults:
            return self.input.keys()

        args = [a for a in self.input if a not in self.defaults]
        return args

    def get_default_vars(self):
        return self.defaults.keys()

def create_flow(name, ui_cfg):
    f = Flow(name)

    input_found = False
    output_found = False
    for ui_dict in ui_cfg:
        ui_name = ui_dict.keys()[0]
        if ui_name == 'input':
            input_found = True
            f.input = ui_dict[ui_name]
        elif ui_name == 'output':
            output_found = True
            f.output = ui_dict[ui_name]
        elif ui_name == 'defaults':
            f.defaults = ui_dict[ui_name]
        else: 
            ui_params = ui_dict[ui_name]
            ui = UnitInstance(ui_name, ui_params)
            f.ui_list.append(ui)

    if not input_found:
        raise Exception("Input must be defined for flow [%s]" % name)
    if not output_found:
        raise Exception("Output must be defined for flow [%s]" % name)
    return f

def create_from_dict(d):
    name = d.keys()[0]
    ui_cfg = d[name]
    f = create_flow(name, ui_cfg)

    return f
