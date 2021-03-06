
from alchemy import registry, engine, yconfig, flow

def get_registry(cfgfile):
    reg = yconfig.load_config(cfgfile)
    return reg

def run_flow_with_reg(reg, config_name, flow_name, notifyfn=None, dryrun=False):
    flow_inst = reg.get_flow(flow_name)

    ctx = engine.Context()
    ctx.dryrun = dryrun
    ctx.registry = reg
    ctx.notifyfn = notifyfn
    ret = engine.run_flow(flow_inst, {}, ctx=ctx, notify=notifyfn)
    if ret:
        ctx.values.update(ret)

    return ctx
    

def run_flow(config_name, flow_name, notifyfn=None, dryrun=False):
    reg = get_registry(config_name)
    return run_flow_with_reg(reg, config_name, flow_name, notifyfn=notifyfn, dryrun=dryrun)

def run_flow_with_dict(config_name, flow_name, flow_dict, reg=None, notifyfn=None, dryrun=False):
    if not reg:
        reg = get_registry(config_name)
    f = flow.create_flow(flow_name, flow_dict)

    ctx = engine.Context()
    ctx.dryrun = dryrun
    ctx.registry = reg
    ctx.notifyfn = notifyfn

    ret = engine.run_flow(f, {}, ctx=ctx, notify=notifyfn)
    if ret:
        ctx.values.update(ret)

    return ctx

