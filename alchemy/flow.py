
class UnitInstance:
    def __init__(self, name):
        self.name = name
        self.desc = None
        self.params = {}
        self.inst_type = 'simple'

class Flow:
    def __init__(self, name):
        self.name = name
        self.unit_inst_list = []


def mark_as_meta(ui):
    ui.inst_type = 'meta'

def is_meta_inst(ui):
    return ui.inst_type == 'meta'

def get_static_params(ui):
    params = {}
    for key, value in ui.params.iteritems():
        if not isinstance(value, str):
            params[key] = value
        elif not value.startswith('$'):
            params[key] = value
    return params


def get_runtime_params(ui):
    deps = []
    for key, value in ui.params.iteritems():
        if isinstance(value, str) and value.startswith('$'):
            deps.append((key, value[1:]))
    return deps
            

def create_unit_inst(name, params):
    if params is None:
        params = {}

    i = UnitInstance(name)

    if '@desc' in params:
        i.desc = params['@desc']
    else:
        i.desc = name

    i.params = params
    return i

def create_flow(name):
    return Flow(name)

def add_unit_inst(flow, inst):
    flow.unit_inst_list.append(inst)

def get_unit_list(f):
    return f.unit_inst_list
        
