
import os, importlib
import pkgutil

import yaml

from alchemy import yconfig, unit

def is_cfg_file(filepath):
    try:
        with open(filepath) as f:
            data = yaml.load(f)
            if 'alchemy' in data:
                return True
            return False
    except:
        return False

def get_config_file_by_module(mod):
    try:
        mod_path = os.path.dirname(mod.__file__)
    except AttributeError:
        return

    cfgfile = os.path.join(mod_path, mod.__name__ + ".yml")
    if os.path.exists(cfgfile):
        with open(cfgfile) as f:
            data = yaml.load(f)
            if 'alchemy' in data:
                return (cfgfile, data)
            
def discover_config():
    config = {}
    for _, name, ispkg in pkgutil.iter_modules():
        if ispkg:
            try:
                m = importlib.import_module(name)
                cfgfile = get_config_file_by_module(m)
                if cfgfile:
                    config[name] = cfgfile[0]
            except ImportError:
                pass
    return config

def _get_config_hierarchy(module_name, seen, hlist):
    if module_name in seen:
        return
    
    seen.add(module_name)
    m = importlib.import_module(module_name)
    cfginfo = get_config_file_by_module(m)
    if not cfginfo:
        raise Exception("Config module [%s] not found" % module_name)

    cfgfile, cfg = cfginfo
    hlist.append((module_name, cfgfile, cfg))
    if 'include' in cfg:
        for include_name in cfg['include']:
            _get_config_hierarchy(include_name, seen, hlist)

def get_config_hierarchy(module_name):
    hlist = []
    seen = set()
    _get_config_hierarchy(module_name, seen, hlist)
    return hlist

def get_registry(cfgfile):
    reg = yconfig.load_config(cfgfile)
    return reg


def get_cfg_units(cfgname):
    reg = get_registry(cfgname)

    unit_info = {}
    for name, u in reg.unit_map.iteritems():
        unit_info[name] = u.get_spec()

    return unit_info

def get_cfg_flows(cfgname):
    reg = get_registry(cfgname)

    flow_info = {}
    for name, u in reg.flow_map.iteritems():
        flow_info[name] = {
            'input': u.input,
            'defaults': u.defaults,
            'output': u.output,
        }

    return flow_info

def get_flow_info(cfgname, flow_name):
    reg = get_registry(cfgname)

    f = reg.flow_map[flow_name]
    flow_info = {}

    flow_info['name'] = f.name
    flow_info['input'] = f.input
    flow_info['output'] = f.output
    flow_info['defaults'] = f.defaults
    ui_list = [ui.to_dict() for ui in f.ui_list]
    flow_info['ui_list'] = ui_list
        
    return flow_info