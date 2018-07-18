
import os, logging
from alchemy import engine, flow, unit

log = logging.getLogger(__name__)

def print_ctx(ctx, param_list):
    """
    param_list: List of context variables to be printed. If null, then print all
    """
    print "--- ctx start --"
    if param_list is None:
        for key, value in ctx.values.iteritems():
            print "{0} = {1}".format(key, value)
    else:
        for p in param_list:
            try:
                print "{0} = {1}".format(p, ctx.values[p])
            except KeyError:
                print "Param [%s] not found" % p

    print "--- ctx end --"

def define_context(ctx, varmap):
    """
    values: Dict of values, where each key:value is a mapping to set the context
    out: Updates the context directly
    Example:
        values:
            a: $b
            c: 1
            d: "hello"
        This defines 3 context variables a,c & d. The value of a is set as the 
        value of context var 'b'
    """
    new_values = engine.resolve_dict(ctx, varmap)
    ctx.values.update(new_values)


def loop(ctx, count, units):
    """
    count: Number of times the loop will run
    units: List of units to run
    Example:
        count: 3
        units:
            - Run command:
                cmd: ls -lrt
            - Print stream:
                stream: $stdout

        This runs the command and prints 3 times
    """
    ui_list = [] 
    for unit_info in units:
        for ui_name, ui_params in unit_info.iteritems():
            ui = unit.UnitInstance(ui_name, ui_params)
            ui_list.append(ui)

    for _ in range(count):
        engine.run_ui_list(ctx, ui_list, allow_flow=False, notify=None)
    
def run_command(cmd, errordup = False, background = False, ignore_error = False):
    """
    cmd: The command string e.g. "uname -a"
    errdup: (False) Duplicate stderr to stdout
    background: (False) Run the command in background i.e. the unix '&'
    ignore_error: (False) Do not fault if the cmd fails with non-exit code
    out:
        status_code: The OS exit code of a process
        stdout: The stdout stream
        stderr: The stderr stream
    """
    import subprocess

    o_status_code = 0
    o_stdout = None
    o_stderr = None

    if errordup:
        o_stderr = subprocess.STDOUT
    else:
        o_stderr = subprocess.PIPE

    if background:
        out = subprocess.Popen(cmd ,shell=True)
        o_status_code = [0]
        o_stdout = None
        o_stderr = None
    else:
        out = subprocess.Popen(cmd ,shell=True, stdout=subprocess.PIPE, stderr=o_stderr)
        o_status_code = out.returncode
        o_stdout = out.communicate()[0].split('\n')

    
    unit_status = True
    if not ignore_error and (o_status_code is not None and o_status_code != 0):
        unit_status = False

    return {
        '_status': unit_status,
        'status_code': o_status_code,
        'stdout': o_stdout,
        'stderr': o_stderr,
    }


def print_stream(stream):
    """
    stream: Any valid file like object or stdout, strerr
    """
    if not stream:
        return
        
    for line in stream:
        print line.rstrip()
        
    
def cli_args_positional(spec, dryrun=False):
    """
    spec: list of positional args
    out:
        'spec: [a,b]' gets converted to ctx params 'input_a', 'input_b'
    """

    if dryrun:
        args = {}
        for arg in spec:
            args['input_' + arg] = ""
        return args
        

    import sys    
    if len(sys.argv[4:]) < len(spec):
        print "Error: not enough args"
        print "args:", " ".join(["<{0}>".format(a) for a in spec])
        return {
            '_status': False
        }

    args = {}
    for i, arg in enumerate(spec):
        args['input_' + arg] = sys.argv[3 + i+1]

    return args

def to_int(ctx, varlist):
    """
    varlist: List of context parameters
    out:
        Updates the context after the type conversion
    """
    for a in varlist:
        try:
            ctx.values[a] = int(ctx.values[a])
        except KeyError:
            pass

def parse_yaml_file(filename):
    """
    filename: Input Yaml filepath
    out:
        export data as is into the context
    """
    try:
        import yaml
        with open(filename) as f:
            data = yaml.load(f)

            return data
    except Exception as e:
        print "Error: unable to open yml file: %s, err = %s" % (filename, str(e))
        return {
            '_status': False
        }

def env_values(varlist):
    """
    varlist: List of env variables
    out:
        Each env var X is exported as ENV_X in the context
    """

    ctx_vars = {}
    for v in varlist:
        ctx_vars["ENV_" + v] = os.environ[v]

    return ctx_vars


def to_list(ctx, varlist):
    """
    varlist: Values to be converted to python list by resolving the parameters
    out:
        list: List of values after resolving
    Example:
       varlist:
            - 1
            - 2
            - $x

        If the x == 10 then output will be [1,2,10]
    """

    l = engine.resolve_list(ctx, varlist)
    return {'list': l}

def delete_ctx(ctx, varlist):
    """
    varlist: List of context variables which need to be deleted
    """

    for v in varlist:
        del ctx.values[v]


def ctx_required(ctx, varlist, dryrun=False):
    """
    varlist: List of context variables which must exist in the context
    """

    if dryrun:
        return {v: '' for v in varlist}

    for v in varlist:
        if not v in ctx.values:
            raise Exception("Context variable [%s] is required but not found" % v)


def for_each(ctx, itemlist, varname, units):
    """
    input:
        varlist: List of items to iterate on.
        varname: The variable name which will be set per iteration. This is deleted once loop finishes
        units: List of units to run
    """
    if not isinstance(varname, str):
        raise Exception("For each variable name %s must be a string" % varname)
        
    ui_list = [] 
    for unit_info in units:
        for ui_name, ui_params in unit_info.iteritems():
            ui = unit.UnitInstance(ui_name, ui_params)
            ui_list.append(ui)

    for item in itemlist:
        ctx.values[varname] = item
        engine.run_ui_list(ctx, ui_list, allow_flow=False)

    if varname in ctx.values:        
        del ctx.values[varname]


def dict_to_ctx(dict_var, keys = None):
    if not isinstance(dict_var, dict):
        raise Exception("Dict to ctx, the dict_var must be a dict")

    if keys is None:
        return dict_var
    else:
        d = {}
        for k in keys:
            d[k] = dict_var[k]
        return d

def to_str(var):
    return {'str_var': str(var)}

def query_dict(ctx, dict_var, pathmap, separator = '/', dryrun=False):
    if dryrun:
        return pathmap

    for ctx_var, dict_path in pathmap.iteritems():
        keylist = dict_path.split(separator)
        val = dict_var
        for key in keylist:
            if not isinstance(val, dict):
                raise Exception("Key=[%s] in path=[%s] is not a dict" % (key, dict_path))

            try:
                val = val[key]
            except KeyError:
                raise Exception("key=[%s] in path=[%s] not found" % (key, dict_path))
        ctx.values[ctx_var] = val

def load_yaml_file(filename, dryrun=False):
    if dryrun:
        return {'yaml_data': ''}

    import yaml

    with open(filename) as f:
        y = yaml.load(f)
        return {'yaml_data': y}

def format_str(ctx, varmap, dryrun=False):
    if dryrun:
        return varmap

    log.info("format-str varmap: %s", varmap)
    ret = {}
    for key, pattern in varmap.iteritems():
        log.info("format_str: exporting var = %s", key)
        ret[key] = pattern.format(**ctx.values)

    return ret

if __name__ == '__main__':
    class A:
        pass

    c = A()
    c.values = {}

    d = {
        'a': {
            'b': 10,
            'c': {
                'c1': [1,2,3]
            }
        }
    }

    path = {
        'x': 'a/b',
        'y': 'a/c',
        'z': 'a/c/c1',
    }
    query_dict(c, d, path)
    print c.values
