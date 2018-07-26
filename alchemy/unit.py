
import os, inspect
import importlib

UNIT_TYPE_SIMPLE = 1
UNIT_TYPE_META = 2
UNIT_TYPE_DERIVED = 3
UNIT_TYPE_SIMPLE_WRAP = 4

class Unit:
    def __init__(self):
        self.name = None
        self.unit_type = UNIT_TYPE_SIMPLE

class FunctionUnit(Unit):
    def __init__(self):
        Unit.__init__(self)
        self.module = None
        self.func = None
        self.pos_args = None
        self.args = None
        self.kargs = None
        self.input_desc = {}
        self.output = {}
    
    def get_args(self):
        return self.args
    
    def get_default_vars(self):
        if self.kargs is None:
            return None
        return self.kargs.keys()

    def get_spec(self):
        spec = {
            'input': {}, 'output': self.output, 'type': self.unit_type,
        }

        for arg in self.args:
            arg_info = {'def': '', 'desc': ''}
            try:
                if self.kargs:
                    arg_info['def'] = self.kargs[arg]
            except KeyError:
                pass

            try:
                if self.input_desc:
                    arg_info['desc'] = self.input_desc[arg]
            except KeyError:
                pass

            spec['input'][arg] = arg_info            

        return spec

        
class DerivedUnit(Unit):
    def __init__(self):
        Unit.__init__(self)
        self.name = None
        self.input = None
        self.output = None
        self.defaults = {}
        self.ui_list = None
        self.unit_type = UNIT_TYPE_DERIVED

    def get_args(self):
        if not self.defaults:
            return self.input

        args = [a for a in self.input if a not in self.defaults]
        return args

    def get_default_vars(self):
        if self.defaults is None:
            return []
        return self.defaults.keys()

    def get_spec(self):
        spec = {
            'input': {}, 'output': self.output, 'type': self.unit_type,
        }

        for arg in self.input:
            arg_info = {'def': '', 'desc': ''}
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

class UnitInstance:
    def __init__(self, name, params):
        desc = None
        try:
            if params:
                desc = params['@desc']
                del params['@desc']
            else:
                params = {}
        except KeyError:
            pass

        self.name = name
        self.params = params
        self.desc = desc

    def to_dict(self):
        return {
            'name': self.name,
            'desc': self.desc,
            'params': self.params,
        }

    def get_desc(self):
        if not self.desc:
            return self.name

        return self.desc

def create_derived_unit(name, input, output, defaults, ui_list):
    u = DerivedUnit()
    u.name = name
    u.input = input
    u.output = output
    u.ui_list = ui_list
    u.defaults = defaults
    u.unit_type = UNIT_TYPE_DERIVED

    return u

def create_unit_inst_from_dict(d):
    name = d.keys()[0]
    params = d[name]
    return UnitInstance(name, params)

def create_derived_unit_from_dict(name, d):
    check_derived_unit(name, d)

    unit_input = d.get('input', {})
    unit_output = d.get('output', {})
    unit_defaults = d.get('defaults', {})

    ui_list = []
    for unit_info in d['units']:
        ui = create_unit_inst_from_dict(unit_info)
        ui_list.append(ui)

    u = create_derived_unit(name, unit_input, unit_output, unit_defaults, ui_list,)
    return u
        

def _get_pos_args(spec):
    if spec.defaults:
        karg_count = len(spec.defaults)
        return spec.args[:-karg_count]

    return spec.args

def _get_kargs(pos_args, spec):
    kargs = {}
    if spec.defaults:
        for i, v in enumerate(spec.defaults):
            kargs[spec.args[len(pos_args) + i]] = v

    return kargs

def _get_func_args(spec):
    pos_args = _get_pos_args(spec)
    kargs = _get_kargs(pos_args, spec)

    return (spec.args, pos_args, kargs)

def _create(name, module, func):
    spec = inspect.getargspec(func)
    args, pos_args, kargs = _get_func_args(spec)

    u = FunctionUnit()
    u.name = name
    u.module = module
    u.func = func
    u.args = args
    u.kargs = kargs
    u.pos_args = pos_args

    return u

def check_func_unit(name, args, kargs, d):
    
    tmp_args = args
    if d['type'] == 'meta':
        tmp_args = [a for a in args if a != 'ctx']
    
    if d['type'] == 'simple-wrap':
        if 'output' not in d:
            raise Exception("Output spec not defined for unit [%s]" % name)

        if len(d['output']) < 1 :
            raise Exception("Output param needs to be defined for unit [%s]" % name)
        
        if len(d['output']) > 1:
            raise Exception("More than one output param defined for unit [%s]" % name)

    tmp_args = [a for a in tmp_args if a != 'dryrun']

    if len(tmp_args) > 0:
        if 'input' not in d or not isinstance(d['input'], dict):
            raise Exception("Inputs not defined defined (or is not a dict) for unit %s" % name)
        
        if len(tmp_args) != len(d['input']):
            raise Exception("Argument count mismatch between function and configured for unit %s" % name)

        for arg in tmp_args:
            if arg not in d['input']:
                raise Exception("Arg [%s] not defined in input for unit %s" % (arg, name))

    tmp_kargs = {k:v for k, v in kargs.iteritems() if k != 'dryrun'}
    if len(tmp_kargs) > 0:
        if 'defaults' not in d:
            raise Exception("Keyword args defined in function but not configured for unit %s" % name)

        if len(tmp_kargs) != len(d['defaults']):
            raise Exception("Keyword argument count mismatch between function and configured for unit %s" % name)

        for k, v in tmp_kargs.iteritems():
            if v != d['defaults'][k]:
                raise Exception("Keyword argument value mismatch for arg %s for unit %s" % (k, name))

                
def check_derived_unit(name, d):
    if 'defaults' in d:
        if 'input' not in d:
            raise Exception("Defaults defined but not inputs for unit %s" % name)

        for arg in d['defaults']:
            if arg not in d['input']:
                raise Exception("Default arg %s not defined in input for unit %s" % (arg, name))
    
def create_function_unit_from_dict(name, d):
    if 'func' not in d:
        raise Exception("Key 'func' not defined for unit: %s" % name)
    
    func_path = d['func']
    module_name, func_name = os.path.splitext(func_path)
    m = importlib.import_module(module_name)
    func_name = func_name[1:]

    if not hasattr(m, func_name):
        raise Exception("Function [%s] not found in module [%s] for unit [%s]" % (func_name, module_name, name))

    func = getattr(m, func_name)
    spec = inspect.getargspec(func)
    args, pos_args, kargs = _get_func_args(spec)

    check_func_unit(name, args, kargs, d)
    u = FunctionUnit()
    u.name = name
    u.module = m
    u.func = func
    u.args = args
    u.kargs = kargs
    u.pos_args = pos_args

    try:
        u.output = d['output']
    except KeyError:
        pass

    if d['type'] == 'simple':
        u.unit_type = UNIT_TYPE_SIMPLE
    elif d['type'] == 'simple-wrap':
        u.unit_type = UNIT_TYPE_SIMPLE_WRAP
    elif d['type'] == 'meta':
        u.unit_type = UNIT_TYPE_META
    else:
        raise Exception("Unknown unit type [%s]" % d['type'])

    return u


def create_unit_from_dict(name, d):
    if 'type' not in d:
        d['type'] = 'simple'

    if 'desc' not in d:
        raise Exception("Description missing for unit: %s" % name)

    unit_type = d['type']
    if unit_type in ['simple', 'meta', 'simple-wrap']:
        u = create_function_unit_from_dict(name, d)
    elif unit_type == 'derived':
        u = create_derived_unit_from_dict(name, d)
    else:
        raise Exception("Unknown unit type [%s] for unit [%s]" % (unit_type, name))

    return u
    

def create_unit(name, module, func_name):
    f = getattr(module, func_name)
    return _create(name, module, f)

def create_unit_by_str(name, module_name, func_name):
    m = importlib.import_module(module_name)
    return create_unit(name, m, func_name)

def mark_as_meta_unit(u):
    u.unit_type = 'meta'

def is_meta_unit(u):
    return u.unit_type == 'meta'

    
