
import os
import yaml
import inspect
import importlib
import logging

import unit
import registry
import flow


log = logging.getLogger(__name__)

def load_module_units(reg, module, units):
    func_dict = dict(inspect.getmembers(module, inspect.isfunction))

    for general_name, func_info in units.iteritems():
        func_name = func_info['func']
        if func_name not in func_dict:
            raise Exception("Unit name [%s.%s] not found" % (module.__name__, func_name))
        u = unit.create(general_name, module, func_name)
        if 'type' in func_info and func_info['type'] == 'meta':
            unit.mark_as_meta_unit(u)
        registry.add_unit(reg, general_name, u)



def load_units(cfg, reg):
    for module_str, module_units in cfg['units'].iteritems():
        m = importlib.import_module(module_str)
        log.info('Loading units from module at: %s', m.__file__)
        load_module_units(reg, m, module_units)

def load_single_flow(reg, flow_name, flow_info):
    f = flow.create_flow(flow_name)

    for inst_info in flow_info:
        if len(inst_info.keys()) > 1:
            raise Exception("Multiple unit instances defined")

        inst_name = inst_info.keys()[0]
        if inst_info.values()[0] is None:
            inst_params = {}
        else:
            inst_params = inst_info.values()[0] 

        if inst_name.startswith('$'):
            inst_name = inst_name[1:]
            ui = flow.create_unit_inst(inst_name, inst_params)
            flow.mark_as_meta(ui)
        else:
            ui = flow.create_unit_inst(inst_name, inst_params)
            
        flow.add_unit_inst(f, ui)

    return f

def load_flows(cfg, reg):
    if 'flows' not in cfg:
        return

    for flow_name, flow_info in cfg['flows'].iteritems():
        f = load_single_flow(reg, flow_name, flow_info)
        registry.add_flow(reg, flow_name, f)
        

def parse_config(fname):
    with open(fname) as f:
        cfg = yaml.load(f)

        return cfg

def find_cfg_file(fname, path_list):
    mod_name = os.path.splitext(fname)[0]
    m = __import__(mod_name)
    file_name = os.path.join(os.path.dirname(m.__file__), fname + '.yml')
    return file_name
    

def _load_config(fname, seen_cfg, cfgpath, reg = None):
    if fname not in seen_cfg:
        seen_cfg.add(fname)
    else:
        return

    actual_path = find_cfg_file(fname, cfgpath)

    if actual_path is None:
        raise Exception("Config file [%s] not found" % fname)

    if reg is None:
        reg = registry.Registry()
        
    log.info("Parsing config: %s", actual_path)
    cfg = parse_config(actual_path)

    if 'include' in cfg:
        for dep_cfg_file in cfg['include']:
            _load_config(dep_cfg_file, seen_cfg, cfgpath=cfgpath, reg = reg)

    load_units(cfg, reg)
    load_flows(cfg, reg)

    return reg

def load_config(fname, cfgpath, reg = None):
    seen_cfg = set()

    reg = _load_config(fname, seen_cfg, cfgpath, reg = None)
    return reg

if __name__ == "__main__":
    from pprint import pprint
    reg = load_config("test.yml", cfgpath=['.'])
