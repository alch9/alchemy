
from alchemy.unit import UnitInstance

class Flow:
    def __init__(self, name):
        self.name = name
        self.input = {}
        self.output = {}
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

    def get_spec(self):
        spec = {
            'input': {}, 'output': self.output,
        }

        if self.input:
            for arg in self.input:
                arg_info = {'desc': ''}
                try:
                    if self.defaults:
                        arg_info['def'] = self.defaults[arg]
                except KeyError:
                    pass

                try:
                    if self.input:
                        arg_info['desc'] = self.input[arg]
                except KeyError:
                    pass

                spec['input'][arg] = arg_info 

        return spec

def create_flow(name, ui_cfg):
    if 'input' not in ui_cfg:
        raise Exception("Input must be defined for flow [%s]" % name)

    if 'output' not in ui_cfg:
        raise Exception("Output must be defined for flow [%s]" % name)

    if 'units' not in ui_cfg:
        raise Exception("Unit sequence must be defined for flow [%s]" % name)

    defaults = {}
    try:
        defaults = ui_cfg['defaults']
        for arg in defaults:
            if arg not in ui_cfg['input']:
                raise Exception("Argument [%s] defined as keyword but not defined in input for flow %s" % (arg, name))
    except KeyError:
        pass

    ui_list = ui_cfg['units']

    f = Flow(name)
    f.defaults = defaults
    if ui_cfg['input']:
        f.input = ui_cfg['input']
    if ui_cfg['output']:
        f.output = ui_cfg['output']

    for ui_dict in ui_list:
        ui_name = ui_dict.keys()[0]
        ui_params = ui_dict[ui_name]
        ui = UnitInstance(ui_name, ui_params)
        f.ui_list.append(ui)

    return f

def create_from_dict(d):
    name = d.keys()[0]
    ui_cfg = d[name]
    f = create_flow(name, ui_cfg)

    return f
