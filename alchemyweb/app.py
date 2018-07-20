from flask import Flask, jsonify
app = Flask(__name__)

import alchemy
from alchemy import query

@app.route("/")
@app.route("/index.html")
def index():
    return app.send_static_file('index.html')

@app.route("/version")
def version():
    return jsonify({'version': alchemy.__version__})

@app.route("/config")
def discover():
    config = query.discover_config()
    return jsonify(config)

@app.route("/config/<cfgname>/units")
def cfg_units(cfgname):
    unit_info = query.get_cfg_units(cfgname)
    return jsonify(unit_info)

@app.route("/config/<cfgname>/flows")
def cfg_flows(cfgname):
    flow_info = query.get_cfg_flows(cfgname)
    return jsonify(flow_info)

@app.route("/config/<cfgname>/flows/<flow_name>")
def cfg_flow_info(cfgname, flow_name):
    flow_info = query.get_flow_info(cfgname, flow_name)
    return jsonify(flow_info)