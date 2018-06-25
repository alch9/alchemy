
import os, logging
import flow
import registry
import unit

log = logging.getLogger(__name__)

class Context:
    def __init__(self):
        self.registry = None
        self.values = {}
        self.flow = None
        self.curr_unit_inst = None
        self.fault = False

def mark_fault(ctx):
    ctx.fault = True

def resolve_unit_inst_params(ctx, ui):
    ui_params = flow.get_static_params(ui)
    runtime_params = flow.get_runtime_params(ui)

    for key, ctx_param in runtime_params:
        if ctx_param not in ctx.values:
            raise Exception("Param [%s] not found in context" % ctx_param)
        ui_params[key] = ctx.values[ctx_param]

    return ui_params

def resolve_list(ctx, arglist):
    args = []

    for a in arglist:
        if isinstance(a, str) and a.startswith('$'):
            try:
                a = a[1:]
                args.append(ctx.values[a])
            except KeyError:
                raise Exception("Variable [%s] not found in context" % a)
        else:
            args.append(a)

    return args

def resolve_dict(ctx, argdict):
    args = {}

    for k,v in argdict.iteritems():
        if isinstance(v, str) and v.startswith('$'):
            try:
                v = v[1:]
                args[k] = ctx.values[v]
            except KeyError:
                raise Exception("Variable [%s] not found in context" % v)
        else:
            args[k] = v

    return args

def execute_unit_inst(ctx, ui):
    if ctx.fault:
        os._exit(1)
    u = registry.get_unit(ctx.registry, ui.name)
    unit_params = resolve_unit_inst_params(ctx, ui)
    ctx.values.update(unit_params)
    ctx.curr_unit_inst = ui

    if unit.is_meta_unit(u):
        ret_val = unit.run_unit(u, ctx.values, ctx = ctx)
    else:
        ret_val = unit.run_unit(u, ctx.values)
        
    if ret_val:
        if '_status' in ret_val and ret_val['_status'] == False:
            mark_fault(ctx)
        ctx.values.update(ret_val)

def execute_meta_inst(ctx, ui):
    if ctx.fault:
        os._exit(1)
    unit_params = resolve_unit_inst_params(ctx, ui)
    ctx.values.update(unit_params)

    flow_name = ui.name
    flow_inst = registry.get_flow(ctx.registry, flow_name)
    execute(None, flow_inst, ctx = ctx)


def validate_flow(ctx, ui_list):
    for ui in ui_list:
        if flow.is_meta_inst(ui):
            if not registry.is_flow_exists(ctx.registry, ui.name):
                raise Exception("Meta flow [%s] not found" % ui.name)
        else:
            if not registry.is_unit_exists(ctx.registry, ui.name):
                raise Exception("Unit [%s] not found" % ui.name)

def execute(reg, flow_inst, notify = None, ctx = None):
    if ctx is None:
        ctx = Context()
        ctx.registry = reg
    ctx.flow = flow_inst

    ui_list = flow.get_unit_list(ctx.flow)
    validate_flow(ctx, ui_list)

    for ui in ui_list:
        if notify:
            notify(ui.name, 'start')

        if flow.is_meta_inst(ui):
            log.info("execute meta instance: %s", ui.name)
            execute_meta_inst(ctx, ui) 
        else:
            execute_unit_inst(ctx, ui)

        if notify:
            notify(ui.name, 'end')
            
