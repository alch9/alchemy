
import os
from alchemy import executor, flow

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

def define_context(ctx, values):
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
    ui = flow.create_unit_inst("anon", values)
    new_values = executor.resolve_unit_inst_params(ctx, ui)
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
            ui = flow.create_unit_inst(ui_name, ui_params)
            ui_list.append(ui)

    for _ in range(count):
        for ui in ui_list:
            executor.execute_unit_inst(ctx, ui)
    
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
        print line
        
    
def cli_args_positional(spec):
    """
    spec: list of positional args
    out:
        'spec: [a,b]' gets converted to ctx params 'input_a', 'input_b'
    """
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
        try:
            ctx_vars["ENV_" + v] = os.environ[v]
        except Exception as e:
            pass

    return ctx_vars
