
import os, inspect, importlib, logging

import yaml

from alchemy import unit
from alchemy import registry
from alchemy import flow


log = logging.getLogger(__name__)

def parse_config(fname):
    with open(fname) as f:
        cfg = yaml.load(f)

        return cfg

def find_cfg_file(fname):
    mod_name = os.path.splitext(fname)[0]
    m = __import__(mod_name)
    file_name = os.path.join(os.path.dirname(m.__file__), fname + '.yml')
    return file_name
    

def _load_config(fname, seen_cfg, reg = None):
    if fname not in seen_cfg:
        seen_cfg.add(fname)
    else:
        return

    actual_path = find_cfg_file(fname)

    if actual_path is None:
        raise Exception("Config file [%s] not found" % fname)

    if reg is None:
        reg = registry.Registry()
        
    log.info("Parsing config: %s", actual_path)
    cfg = parse_config(actual_path)

    if 'include' in cfg:
        for dep_cfg_file in cfg['include']:
            _load_config(dep_cfg_file, seen_cfg, reg = reg)

    load_units(cfg, reg)
    load_flows(cfg, reg)

    return reg

def load_config(fname, reg = None):
    seen_cfg = set()

    reg = _load_config(fname, seen_cfg, reg = None)
    return reg

            
def load_units(cfg, reg):
    if 'units' not in cfg:
        return 

    for name, udict in cfg['units'].iteritems():
        try:
            u = unit.create_unit_from_dict(name, udict)
        except Exception, e:
            log.error("Failed to load unit: [%s]", name)
            raise

        reg.add_unit(name, u)

def load_flows(cfg, reg):
    if 'flows' not in cfg:
        return

    for name, flow_cfg in cfg['flows'].iteritems():
        f = flow.create_flow(name, flow_cfg)
        reg.add_flow(name, f)
