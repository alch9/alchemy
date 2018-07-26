#!/usr/bin/env python 

import os, sys, argparse
import logging

log = None

EXENAME = os.path.basename(sys.argv[0])

CMDINFO = {
    'help': 'Print top level help',
    'cmd' : 'Prints the available commands',
    'check': 'Check integrity of the config file',
    'run' : 'Runs the flow',
    'dryrun' : 'Runs the flow',
    'listu': 'List units',
    'listf': 'List flows',
    'discover': 'Discover alchemy modules',
    'cfginc': 'Show config hierarchy',
    'version': 'Show alchemy version',
}

def top_level_help():
    print "Usage: {0} <command> <command args>".format(EXENAME)
    print "See '{0} cmd' to see the available commands".format(EXENAME)

def version_cmd(_):
    import alchemy
    print alchemy.__version__

def cmd_cmd():
    print "Available commands:"
    for cmd, info in CMDINFO.iteritems():
        print "{0:10} {1}".format(cmd, info)

def check_cmd(args):
    if len(args) < 1:
        print "Error: not enough arguments"
        print "Usage: {0} check <config file>".format(EXENAME)
        sys.exit(1)

    cfgfile = args[0]

    import yaml
    from pprint import pprint
    with open(cfgfile) as f:
        y = yaml.load(f)
        pprint(y)


def get_registry(cfgfile):
    from alchemy import yconfig

    reg = yconfig.load_config(cfgfile)
    return reg
    

def run_cmd(args, dryrun=False):
    if len(args) < 2:
        print "Error: not enough arguments"
        print "Usage: {0} run <config file> <flow name>".format(EXENAME)
        sys.exit(1)
    
    cfgfile, flow_name = args[0], args[1]
    log.info("Config file: %s", cfgfile)
    log.info("Flow name: %s", flow_name)

    from alchemy import registry, engine

    if dryrun:
        engine.run_function_unit = engine.run_function_unit_dryrun

    reg = get_registry(cfgfile)
    flow_inst = reg.get_flow(flow_name)

    from threading import Thread
    from Queue import Queue

    progress_q = Queue()

    def print_names(pq):
        while True:
            name, event = pq.get()
            if name == '--end--':
                log.info("-- END --")
                break
            log.info("%s - %s", name, event)

    def notify(name, event):
        if event == 'start':
            print ">>", name
        progress_q.put((name, event))
        
    t = Thread(target = print_names, args=(progress_q,))
    t.start()

    try:
        ctx = engine.Context()
        ctx.registry = reg
        ret = engine.run_flow(flow_inst, {}, ctx=ctx, notify=notify)
        if ret:
            ctx.values.update(ret)
    except Exception, e:
        print "Flow run=[%s] failed, err = %s" % (flow_name, str(e))
        os._exit(1)
    finally:
        progress_q.put(("--end--", None))

    if dryrun:
        print "\n---- CONTEXT START ---"
        for k,v in iter(sorted(ctx.values.iteritems())):
            print "%s = [%s]" % (k, v)
        print "---- CONTEXT END ---"

def listu_cmd(args):
    if len(args) < 1:
        print "Error: not enough arguments"
        print "Usage: {0} listu <config file>".format(EXENAME)
        sys.exit(1)

    cfgfile = args[0]
    reg = get_registry(cfgfile)

    from alchemy.unit import FunctionUnit

    for i, (name, u) in enumerate(reg.unit_map.iteritems()):
        doc = ""
        
        if isinstance(u, FunctionUnit):
            if u.func.__doc__:
                doc = u.func.__doc__
            print "{0:<3} {1:<20} {2}".format((i+1), name, doc)
        else:
            print "{0:<3} {1:<20}".format((i+1), name)
            
        print "------------------------------------------"

def listf_cmd(args):
    if len(args) < 1:
        print "Error: not enough arguments"
        print "Usage: {0} listf <config file>".format(EXENAME)
        sys.exit(1)

    cfgfile = args[0]
    reg = get_registry(cfgfile)

    for i, name in enumerate(reg.flow_map.keys()):
        print "{0:<2} {1}".format((i+1), name)

def discover_cmd(args):
    from alchemy import query
    config = query.discover_config()

    for name, cfgfile in config.iteritems():
        print "{0:20} : {1}".format(name, cfgfile)
    
def cfginc_cmd(args):
    if len(args) < 1:
        print "Error: not enough arguments"
        print "Usage: {0} cfginc <config>".format(EXENAME)
        sys.exit(1)

    mod_name = args[0]
    from alchemy import query
    info = query.get_config_hierarchy(mod_name)
    if info:
        for name, cfgfile, _ in info:
            print "{0:20} : {1}".format(name, cfgfile)
    

def dispatch_cmd(cmd, args):
    if cmd == 'help':
        top_level_help()
    elif cmd == 'cmd':
        cmd_cmd()
    elif cmd == 'check':
        check_cmd(args)
    elif cmd == 'run':
        run_cmd(args)
    elif cmd == 'dryrun':
        run_cmd(args, dryrun=True)
    elif cmd == 'listf':
        listf_cmd(args)
    elif cmd == 'listu':
        listu_cmd(args)
    elif cmd == 'discover':
        discover_cmd(args)
    elif cmd == 'cfginc':
        cfginc_cmd(args)
    elif cmd == 'version':
        version_cmd(args)
    else:
        print "Error: unknown command [{0}]".format(cmd)
        top_level_help()
        sys.exit(1)

def setup_logging():
    global log
    log = logging.getLogger()

    handler = logging.FileHandler('alch.log', mode='w')
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s: %(message)s')
    handler.setFormatter(formatter)
    log.addHandler(handler)
    log.setLevel(logging.INFO)

def run():
    if len(sys.argv[1:]) < 1:
        print "Error: not enough arguments"
        top_level_help()
        sys.exit(1)

    cmd, args = sys.argv[1], sys.argv[2:]

    setup_logging()
    log.info("Logging setup done")
    dispatch_cmd(cmd, args)


if __name__ == '__main__':
    run()


    
