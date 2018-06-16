
import inspect
import importlib

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

    return (pos_args, kargs)

def _create(name, module, func):
    spec = inspect.getargspec(func)
    args, kargs = _get_func_args(spec)

    u = Unit()
    u.name = name
    u.module = module
    u.func = func
    u.args = args
    u.kargs = kargs

    return u


def create(name, module, func_name):
    f = getattr(module, func_name)
    return _create(name, module, f)

def create_by_str(name, module_name, func_name):
    m = importlib.import_module(module_name)
    return create(name, m, func_name)


class Unit:
    def __init__(self):
        self.name = None
        self.module = None
        self.func = None
        self.args = None
        self.kargs = None


    def run(self, param_dict):
        pos_args = []
        for a in self.args: 
            pos_args.append(param_dict[a])
        
        kargs = {}

        for a in self.kargs: 
            try:
                kargs[a] = param_dict[a]
            except KeyError:
                pass

        return self.func(*pos_args, **kargs)


if __name__ == '__main__':

    #def test(a,b, c = None, d = 1):
    u = create_by_str('Add', 'a.b', 'test')

    p = {
            'a': 1, 
            'b': 9,
            'c': "Hello",
            'd': 10000
        }

    print u.run(p)

    #create_by_str('Test', 'a.b', 'test')
    #create_by_str('Test2', 'a.b', 'test2')
    #create_by_str('Test3', 'a.b', 'test3')
