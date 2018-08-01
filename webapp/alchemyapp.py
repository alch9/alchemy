from flask import Flask, jsonify, render_template
import flask

app = Flask(__name__, static_folder='./react-app/public', template_folder='./react-app/public')

import alchemy
from alchemy import query, api

def wrap_response(rsp):
    rsp.headers['Access-Control-Allow-Origin'] = '*'
    return rsp

@app.route("/")
@app.route("/index.html")
def index():
    return render_template('index.html')

@app.route("/version")
def version():
    return wrap_response(jsonify({'version': alchemy.__version__}))

@app.route("/config")
def discover():
    config = query.discover_config()
    return wrap_response(jsonify(config))

@app.route("/config/<cfgname>/units")
def cfg_units(cfgname):
    unit_info = query.get_cfg_units(cfgname)
    return wrap_response(jsonify(unit_info))

@app.route("/config/<cfgname>/flows")
def cfg_flows(cfgname):
    flow_info = query.get_cfg_flows(cfgname)
    return wrap_response(jsonify(flow_info))

@app.route("/config/<cfgname>/flows/<flow_name>", methods=['GET', 'POST'])
def cfg_flow_info(cfgname, flow_name):
    if flask.request.method == 'GET':
        flow_info = query.get_flow_info(cfgname, flow_name)
        return wrap_response(jsonify(flow_info))
    else:
        dryrun = flask.request.args.get('dryrun', 'false') == 'true'
        flow_cfg = flask.request.get_json(force=True)
        ctx = api.run_flow_with_dict(cfgname, flow_name, flow_cfg, dryrun=True)

        return wrap_response(jsonify(ctx.values))
