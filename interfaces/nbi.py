#!/usr/local/bin/python3.4
"""
## Copyright (c) 2015 SONATA-NFV, 2017 5GTANGO [, ANY ADDITIONAL AFFILIATION]
## ALL RIGHTS RESERVED.
##
## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.
##
## Neither the name of the SONATA-NFV, 5GTANGO [, ANY ADDITIONAL AFFILIATION]
## nor the names of its contributors may be used to endorse or promote
## products derived from this software without specific prior written
## permission.
##
## This work has been performed in the framework of the SONATA project,
## funded by the European Commission under Grant number 671517 through
## the Horizon 2020 and 5G-PPP programmes. The authors would like to
## acknowledge the contributions of their colleagues of the SONATA
## partner consortium (www.sonata-nfv.eu).
##
## This work has been performed in the framework of the 5GTANGO project,
## funded by the European Commission under Grant number 761493 through
## the Horizon 2020 and 5G-PPP programmes. The authors would like to
## acknowledge the contributions of their colleagues of the 5GTANGO
## partner consortium (www.5gtango.eu).
"""

from flask import Flask, request, jsonify
import logging, json, datetime

from tornado import websocket, web, ioloop, httpserver
from slice_manager.script_ssm_slice import app_ssm

import worker.worker as worker
import interfaces.validate_incoming_json as json_validator
from logger import TangoLogger

#Log definition to make the slice logs idetified among the other possible 5GTango components.
LOG = TangoLogger.getLogger(__name__, log_level=logging.DEBUG, log_json=True)
TangoLogger.getLogger("resistoApi:nbi", logging.DEBUG, log_json=True)
LOG.setLevel(logging.DEBUG)

app = Flask(__name__)

#Variables with the API path sections
API_ROOT="/api"
API_VERSION="/v1"
API_SLICE="/slice"

############################################# RESISTO API PING ############################################
# PING function to validate if the resisto-api-docker is active
@app.route('/pings', methods=['GET'])
def getPings():
  ping_response  = {'alive_since': '2018-07-18 10:00:00 UTC', 'current_time': str(datetime.datetime.now().isoformat())}

  return jsonify(ping_response), 200



######################################### RESISTO API Actions #########################################
# CREATES a Slice
@app.route(API_ROOT+API_VERSION+API_SLICE, methods=['POST'])
def create_slice():
  LOG.info("Request to create a Slice with the following information: " + str(request.json))
  
  # validates the fields with uuids (if they are right UUIDv4 format), 400 Bad request / 201 ok
  creating_slice = json_validator.validate_create_slice(request.json)
  
  if (creating_slice[1] == 200):
    creating_slice = worker.create_slice(request.json)
  
  return jsonify(creating_slice[0]), creating_slice[1]


# CREATES a Slice Subnet
@app.route(API_ROOT+API_VERSION+API_SLICE+'/<name>/action/create', methods=['PUT'])
def create_slice_subnet(name):
  LOG.info("Request to create a Slice Subnet with the following information: " + str(request.json))
  
  # validates the fields with uuids (if they are right UUIDv4 format), 400 Bad request / 201 ok
  creating_slice_subnet = json_validator.validate_create_slice_subnet(request.json)
  
  if (creating_slice_subnet[1] == 200):
    creating_slice_subnet = worker.create_slice_subnet(request.json, name)
  
  return jsonify(creating_slice_subnet[0]), creating_slice_subnet[1]

# Add a Slice Subnet
@app.route(API_ROOT+API_VERSION+API_SLICE+'/<name>/action/add', methods=['PUT'])
def add_slice_subnet(name):
  LOG.info("Request to add the Slice Subnet according to the following: " + str(request.json))
  
  # validates the fields with uuids (if they are right UUIDv4 format), 400 Bad request / 202 ok
  adding_slice_subnet = json_validator.validate_add_slice_subnet(request.json)
  
  if (adding_slice_subnet[1] == 200):
    adding_slice_subnet = worker.add_slice_subnet(request.json, name)  
  
  return jsonify(adding_slice_subnet[0]), adding_slice_subnet[1]

# Registration
@app.route(API_ROOT+API_VERSION+API_SLICE+'/<name>/action/registration', methods=['PUT'])
def registration(name):
  LOG.info("Request to registration according to the following: " + str(request.json))
  
  # validates the fields with uuids (if they are right UUIDv4 format), 400 Bad request / 202 ok
  #registration = json_validator.validate_registration(request.json)
  registration = ("", 200)

  if (registration[1] == 200):
    registration = worker.registration(request.json, name)  
  
  return jsonify(registration[0]), registration[1]

# Handover
@app.route(API_ROOT+API_VERSION+API_SLICE+'/<name>/action/handover', methods=['PUT'])
def handover(name):
  LOG.info("Request to handover according to the following: " + str(request.json))
  
  # validates the fields with uuids (if they are right UUIDv4 format), 400 Bad request / 202 ok
  #handover = json_validator.validate_handover(request.json)
  handover = ("", 200)

  if (handover[1] == 200):
    handover = worker.handover(request.json, name)  
  
  return jsonify(handover[0]), handover[1]

# REMOVES a Slice Subnet
@app.route(API_ROOT+API_VERSION+API_SLICE+'/<name>/action/remove', methods=['PUT'])
def remove_slice_subnet(name):
  LOG.info("Request to remove the Slice Subnet according to the following: " + str(request.json))
  
  # validates the fields with uuids (if they are right UUIDv4 format), 400 Bad request / 202 ok
  removing_slice_subnet = json_validator.validate_remove_slice_subnet(request.json)
  
  if (removing_slice_subnet[1] == 200):
    removing_slice_subnet = worker.remove_slice_subnet(request.json, name)  
  
  return jsonify(removing_slice_subnet[0]), removing_slice_subnet[1]

# DELETE a Slice Subnet
@app.route(API_ROOT+API_VERSION+API_SLICE+'/<name>/action/delete', methods=['PUT'])
def delete_slice_subnet(name):
  LOG.info("Request to delete the Slice Subnet according to the following: " + str(request.json))
  
  # validates the fields with uuids (if they are right UUIDv4 format), 400 Bad request / 202 ok
  deleting_slice_subnet = json_validator.validate_delete_slice_subnet(request.json)
  
  if (deleting_slice_subnet[1] == 200):
    deleting_slice_subnet = worker.delete_slice_subnet(request.json, name)  
  
  return jsonify(deleting_slice_subnet[0]), deleting_slice_subnet[1]

# DELETE a Slice
@app.route(API_ROOT+API_VERSION+API_SLICE, methods=['DELETE'])
def delete_slice():
  LOG.info("Request to delete a Slice with the following information: " + str(request.json))
  
  # validates the fields with uuids (if they are right UUIDv4 format), 400 Bad request / 204 ok
  deleting_slice = json_validator.validate_delete_slice(request.json)
  
  if (deleting_slice[1] == 200):
    deleting_slice = worker.delete_slice(request.json)
  
  return jsonify(deleting_slice[0]), deleting_slice[1]

# GETS ALL the Slice Status information
@app.route(API_ROOT+API_VERSION+API_SLICE, methods=['GET'])
def get_all_slice_status():
  LOG.info("Request to retreive all the Slice Status.")
  allSliceStatus = worker.get_all_slice_status()

  return jsonify(allSliceStatus[0]), allSliceStatus[1]

# GETS a SPECIFIC Slice Status
@app.route(API_ROOT+API_VERSION+API_SLICE+'/<name>/status', methods=['GET'])
def get_slice_status(name):
  LOG.info("Request to retrieve the Slice Status with Name: " + str(name))
  sliceStatus = worker.get_slice_status(str(name))

  return jsonify(sliceStatus[0]), sliceStatus[1]




