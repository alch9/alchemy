
import os, logging, types
import registry
from alchemy.unit import FunctionUnit, DerivedUnit, UNIT_TYPE_META, UNIT_TYPE_SIMPLE, UNIT_TYPE_SIMPLE_WRAP


log = logging.getLogger(__name__)

class Context:
    def __init__(self):
        self.registry = None
        self.values = {}
        self.flow = None
        self.curr_unit_inst = None
        self.fault = False
        self.curr_unit_name = None
        self.notifyfn = None
        self.dryrun = False

def clone_context(ctx):
    newctx = Context()
    newctx.registry = ctx.registry
    newctx.notifyfn = ctx.notifyfn

    return newctx

def mark_fault(ctx):
    ctx.fault = True

def get_static_params(ui_params):
    params = {}
    for key, value in ui_params.iteritems():
        if not isinstance(value, str):
            params[key] = value
        elif not value.startswith('$'):
            params[key] = value
    return params


def get_runtime_params(ui_params):
    deps = []
    for key, value in ui_params.iteritems():
        if isinstance(value, str) and value.startswith('$'):
            deps.append((key, value[1:]))
    return deps

def resolve_unit_inst_params(ctx, ui, unit_arg_list):
    ui_params = get_static_params(ui.params)
    runtime_params = get_runtime_params(ui.params)

    for key, ctx_param in runtime_params:
        if ctx_param not in ctx.values:
            raise Exception("Resolve [%s]: param [%s] not found in context" % (ui.name, ctx_param))
        ui_params[key] = ctx.values[ctx_param]

    for arg in unit_arg_list:
        if arg == 'ctx' or arg == 'dryrun': continue
        if arg not in ui_params:
            if arg not in ctx.values:
                raise Exception("Param [%s] not found in context" % arg)
            ui_params[arg] = ctx.values[arg]

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

def run_function_unit(ctx, u, params, with_ctx = False):
    if ctx.dryrun:
        return run_function_unit_dryrun(ctx, u, params, with_ctx=with_ctx)

    if with_ctx:
        pos_args = [ctx]
    else:
        pos_args = []

    for a in u.pos_args: 
        if a != 'ctx':
            pos_args.append(params[a])
    
    kargs = {}
    for a in u.kargs: 
        try:
            kargs[a] = params[a]
        except KeyError:
            pass

    retval = u.func(*pos_args, **kargs)

    if u.unit_type == UNIT_TYPE_SIMPLE_WRAP:
        key = u.output.keys()[0]
        return {key: retval}

    return retval

def execute_unit_inst(ctx, ui):
    if ctx.fault:
        os._exit(1)
    
    if ui.name.startswith('$'):
        log.info("Sub flow detected: %s", ui.name)
        flow_name = ui.name[1:]
        flow = ctx.registry.get_flow(flow_name)
        flow_params = resolve_unit_inst_params(ctx, ui, flow.get_args())
        newctx = clone_context(ctx)
        ret_val = run_flow(flow, flow_params, ctx=newctx)
    else:
        u = ctx.registry.get_unit(ui.name)
        unit_params = resolve_unit_inst_params(ctx, ui, u.get_args())

        if isinstance(u, FunctionUnit):
            ctx.curr_unit_inst = ui

            if u.unit_type == UNIT_TYPE_META:
                ret_val = run_function_unit(ctx, u, unit_params, with_ctx = True)
            else:
                ret_val = run_function_unit(ctx, u, unit_params, with_ctx = False)
        else:
            ret_val = run_derived_unit(ctx, u, unit_params)

    if isinstance(ret_val, types.NoneType):
        ctx.values['@result'] = None
    elif not isinstance(ret_val, dict):
        ctx.values['@result'] = ret_val
    else:
        if '_status' in ret_val and ret_val['_status'] == False:
            mark_fault(ctx)
        ctx.values.update(ret_val)


def validate_derived_unit(ctx, u, params):
    for ui in u.ui_list:
        if not ctx.registry.is_unit_exists(ui.name):
            raise Exception("Unit [%s] not found" % ui.name)

    for var in u.get_args():
        if var not in params:
            raise Exception("Context var [%s] is required for unit [%s]" % (var, u.name))

def check_ui_list(ctx, ui_list, allow_flow):
    for ui in ui_list:
        if ui.name.startswith('$'):
            if not allow_flow:
                raise Exception("Using references to flow [%s] not allowed" % ui.name)
            else:
                flow_name = ui.name[1:]
                if not ctx.registry.is_flow_exists(flow_name):
                    raise Exception("Referenced flow [%s] not found" % ui.name)
        else:
            if not ctx.registry.is_unit_exists(ui.name):
                raise Exception("Unit [%s] not found" % ui.name)
                
def run_ui_list(ctx, ui_list, allow_flow = False):
    check_ui_list(ctx, ui_list, allow_flow)

    for ui in ui_list:
        if ctx.notifyfn:
            ctx.notifyfn(ui.get_desc(), 'start')

        log.info("") 
        log.info("Unit instance: %s ---- START", ui.name)
        try:
            execute_unit_inst(ctx, ui)
        except Exception, e:
            log.exception("Failed to run instance: [%s], err = %s", ui.get_desc(), str(e))
            raise
        log.info("Unit instance: %s ---- END", ui.name)

        if ctx.notifyfn:
            ctx.notifyfn(ui.get_desc(), 'end')
        
def run_derived_unit(ctx, dunit, params, notify = None):
    validate_derived_unit(ctx, dunit, params)

    newctx = clone_context(ctx)

    defaults = {}
    if dunit.defaults:
        defaults = dunit.defaults

    for var in dunit.input:
        try:
            newctx.values[var] = params[var]
        except KeyError:
            if var not in defaults:
                raise
            else:
                newctx.values[var] = defaults[var]
    
    log.debug("Run Derived unit: %s %s", dunit.name, params)
    run_ui_list(newctx, dunit.ui_list, allow_flow=False)
            
    ret = None
    if dunit.output:
        ret = {var: newctx.values[var] for var in dunit.output}
    return ret

def run_flow(flow, params, notify = None, ctx = None):
    log.info("Running flow: %s %s", flow.name, params)

    if ctx is not None:
        newctx = ctx
    else:
        newctx = Context()
        newctx.registry = ctx.registry
        newctx.notifyfn = notify

    newctx.values.update(flow.defaults)

    for var in flow.input:
        print var, params[var]
        newctx.values[var] = params[var]

    run_ui_list(newctx, flow.ui_list, allow_flow=True)

    ret = None
    if flow.output:
        ret = {var: newctx.values[var] for var in flow.output}

    log.debug("Flow [%s] output: %s", flow.name, ret)
    return ret

def run_flow_by_name(flow_name, params, notify = None, ctx = None):
    if not ctx.registry.is_flow_exists(flow_name):
        raise Exception("Flow [%s] not found" % flow_name)

    flow = ctx.registry.get_flow(flow_name)
    return run_flow(flow, params, notify=notify, ctx=ctx)

def check_refs_in_params(ctx, d):
    if isinstance(d, dict):
        for v in d.values():
            check_refs_in_params(ctx, v)
    elif isinstance(d, list):
        for v in d:
            check_refs_in_params(ctx, v)
    elif isinstance(d, str):
        try:
            _ = d.format(**ctx.values)
        except KeyError, e:
            key = e.args[0]
            reason = "Var=[%s] used in [%s] not found" % (key, d)
            log.error(reason)
            raise Exception(reason)

def run_function_unit_dryrun(ctx, u, params, with_ctx = False):
    if with_ctx:
        pos_args = [ctx]
        check_refs_in_params(ctx, params)
    else:
        pos_args = []

    for a in u.pos_args: 
        if a != 'ctx':
            pos_args.append(params[a])
    
    kargs = {}
    for a in u.kargs: 
        try:
            if a == 'dryrun':
                kargs['dryrun'] = True
            else:
                kargs[a] = params[a]
        except KeyError:
            pass

    ret = u.func(*pos_args, **kargs)
    if ret and isinstance(ret, dict):
        for k in ret.keys():
            ret[k] = u.name

    return ret        
    

if __name__ == '__main__':
    import sys

    log = logging.getLogger()
    log.setLevel(logging.DEBUG)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    log.addHandler(ch) 

    from alchemy.unit import create_unit_by_str, UnitInstance, create_derived_unit
    from alchemy.flow import create_from_dict

    def add(a,b):
        return {'result': a+b}

    def mul(a,b):
        return {'result': a*b}

    def greet(name = None):
        if name is None:
            name = "World"
        return "Hello " + name
        

    def add_ctx(ctx, varmap):
        val = resolve_dict(ctx, varmap)
        return val
    

    add_unit = create_unit_by_str('Add', '__main__', 'add')
    mul_unit = create_unit_by_str('Mul', '__main__', 'mul')
    greet_unit = create_unit_by_str('Greet', '__main__', 'greet')
    add_ctx_unit = create_unit_by_str('Context', '__main__', 'add_ctx')
    add_ctx_unit.unit_type = UNIT_TYPE_META

    double = create_derived_unit('Double', ['num'], ['result'], {}, [
        UnitInstance('Add', {'a': '$num', 'b': '$num'})        
    ])

    add_3 = create_derived_unit('Add3', ['a', 'b', 'c'], ['result'], {}, [
        UnitInstance('Add', {}),
        UnitInstance('Add', {'a': '$result', 'b': '$c'})
    ])

    add_3.defaults = {'c': 1}

    square = create_derived_unit('Square', ['num'], ['result'], {}, [
        UnitInstance('Mul', {'a': '$num', 'b': '$num'})        
    ])

    triple = create_derived_unit('Triple', ['num'], ['result'], {}, [
        UnitInstance('Double', {}),
        UnitInstance('Add', {'a': '$result', 'b': '$num'}),
    ])

    ctx = Context()
    ctx.registry = registry.Registry()
    ctx.registry.add_unit('Context', add_ctx_unit)
    ctx.registry.add_unit('Add', add_unit)
    ctx.registry.add_unit('Add3', add_3)
    ctx.registry.add_unit('Mul', mul_unit)
    ctx.registry.add_unit('Square', square)
    ctx.registry.add_unit('Double', double)
    ctx.registry.add_unit('Triple', triple)
    ctx.registry.add_unit('Greet', greet_unit)

    ab_flow = create_from_dict({
        'abflow': [
            { 'input': {'a': "Integer", 'b': "Integer"}, },
            { 'output': {"ab_result": "Compute value"}, },
            { 'Add': {}},
            { 'Square': {'num': '$result'}},

            { 'Context': { 'varmap': { 'ab_result': '$result'}} },
        ]
    })

    flow1 = create_from_dict({
        'flow1': [
            {'output': {'ab_result': "abc"}},
            { '$abflow': {'a': 3, 'b': 2}, },
        ]
    })

    add_3_flow = create_from_dict({
        'add-3': [
            {'input': {'num': "Some integer"}},
            {'defaults': {'num': 10}},
            {'output': {'result': "Result"}},
            { 'Add3': {'a': 1, 'b': 1, 'c': '$num'}, },
        ]
    })

    ctx.registry.add_flow('abflow', ab_flow)
    ctx.registry.add_flow('flow1', flow1)
    ctx.registry.add_flow('add-3', add_3_flow)

    print run_flow_by_name('add-3', {}, ctx=ctx)

    print ctx.values
