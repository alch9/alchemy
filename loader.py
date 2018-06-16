

import yaml
import inspect
import importlib


class UnitFunction:
    def __init__(self, func, module):
        spec = inspect.getargspec(f)
        self.func = func
        self.module = module
        self.args = spec.args
        self.kargs = {}


    def add_arg(self, arg):
        self.args.append(arg)

    def add_karg(self, name, value):
        self.kargs[name] = value


    def call(self):
        return self.func(*self.args, **self.kargs)


def load_config(fname):
    with open(fname) as f:
        cfg = yaml.load(f)

        return cfg

def get_func_info(f, module):
    print spec
    u = Unit(f, module)
    self.args = []
    if spec.defaults is None:
        pass
    else:
        pass
    print inspect.getcomments(f)

    

def load_module_units(module, units):
    func_dict = dict(inspect.getmembers(module, inspect.isfunction))

    for general_name, func_name in units.iteritems():
        try:
            get_func_info(func_dict[func_name], module)
        except KeyError:
            return

        print "-" * 40



def load_units(cfg):
    for module_str, module_units in cfg['units'].iteritems():
        print "importing", module_str
        m = importlib.import_module(module_str)
        load_module_units(m, module_units)


if __name__ == "__main__":
    from pprint import pprint
    cfg = load_config("test.yml")
    load_units(cfg)

