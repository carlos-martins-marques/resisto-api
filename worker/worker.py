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

import logging, datetime, uuid, time, json
from threading import Thread, Lock

import interfaces.sbi as sbi
import database.database as database
from logger import TangoLogger

from slice_manager.client_script_ssm_slice import client_ssm_thread

import threading

# INFORMATION
# mutex used to ensure one single access to ddbb (repositories) for the nsi records creation/update/removal
mutex_slice2db_access = Lock()

#Log definition to make the slice logs idetified among the other possible 5GTango components.
LOG = TangoLogger.getLogger(__name__, log_level=logging.DEBUG, log_json=True)
TangoLogger.getLogger("resistoApi:worker", logging.DEBUG, log_json=True)
LOG.setLevel(logging.DEBUG)

db = database.slice_database()

################################## THREADs to manage slice requests #################################
# SEND NETWORK SLICE (NS) INSTANTIATION REQUEST
## Objctive: send request 2 GTK to instantiate 
## Params: NSI - parameters given by the user.
class thread_ns_instantiate(Thread):
  def __init__(self, nsi_json):
    Thread.__init__(self)
    self.NSI = {}
    self.req = nsi_json
  
  # Creates the json structure to request a NS instantiation.
  def send_instantiation_request(self):
    LOG.info("Instantiating Slice: " + self.req['sliceName'])
    
    # NS requests information
    data = {}
    data['name'] = self.req['sliceName']
    data['nst_id'] = self.req['sliceTemplateId']
    data['request_type'] = 'CREATE_SLICE'
    if self.req['instantiation_params']:
      data['instantiation_params'] = self.req['instantiation_params']
  
    # Calls the function towards the GTK
    LOG.info("NS Instantiation request JSON: " + str(data))
    instantiation_response = sbi.net_serv_instantiate(data)
    return instantiation_response
    #return ({},201)

 
  def run(self):

    # Store slice subnet / slice
    if 'slice' in self.req:
      db.add_slice_subnet(self.req['sliceName'],self.req['slice'])
    else:
      db.add_slice(self.req['sliceName'])



    # acquires mutex to have unique access to the nsi (repositories)
    mutex_slice2db_access.acquire()
    
    instantiation_resp = self.send_instantiation_request()
    if instantiation_resp[1] != 201:
      self.NSI['nsi-status'] = 'ERROR'
      self.NSI['errorLog'] = 'ERROR when instantiating '
      # Change status
      if 'slice' in self.req:
        db.update_status_slice_subnet("ERROR",self.req['sliceName'],self.req['slice'])
      else:
        db.update_status_slice("ERROR",self.req['sliceName'])

    else:
      self.NSI['id'] = self.req['sliceName']
      self.NSI['nsi-status'] = 'INSTANTIATING'
      # Change status
      if 'slice' in self.req:
        db.update_status_slice_subnet("CREATING",self.req['sliceName'],self.req['slice'])
      else:
        db.update_status_slice("CREATING",self.req['sliceName'])
      
      

    # releases mutex for any other thread to acquire it
    mutex_slice2db_access.release()
    
    if self.NSI['nsi-status'] != 'ERROR':
      # Waits until the NS is instantiated/ready or error
      deployment_timeout = 30 * 60   # 30 minutes

      nsi_instantiated = False
      while deployment_timeout > 0:

        if self.NSI['id'] == self.req['sliceName']:
          uuid = sbi.get_nsi_id_from_name(self.req['sliceName'])
          if (uuid):
            self.NSI['id'] = uuid
          
        if self.NSI['id'] != self.req['sliceName']:
          # Check ns instantiation status
          nsi = sbi.get_saved_nsi(self.NSI['id'])
          if "uuid" in nsi:
            self.NSI = nsi
            self.NSI["id"] = self.NSI["uuid"]
            del self.NSI["uuid"]
          
          if self.NSI['nsi-status'] in ["INSTANTIATED", "ERROR", "READY"]:
            nsi_instantiated = True
          
          # if all services are instantiated, ready or error, break the while loop to notify the GTK
          if nsi_instantiated:
            LOG.info("Network Slice Instantiation request processed for Network Slice with ID: "+str(self.NSI['id']))
            # Change status
            if 'slice' in self.req:
              db.update_status_slice_subnet("CREATED",self.req['sliceName'],self.req['slice'])
            else:
              db.update_status_slice("CREATED",self.req['sliceName'])
            break
    
        time.sleep(15)
        deployment_timeout -= 15
    
      if not nsi_instantiated:
        self.NSI['nsi-status'] = 'ERROR'
        self.NSI['errorLog'] = 'ERROR when terminating with timeout'
        # Change status
        if 'slice' in self.req:
          db.update_status_slice_subnet("ERROR",self.req['sliceName'],self.req['slice'])
        else:
          db.update_status_slice("ERROR",self.req['sliceName'])
    


# SEND NETWORK SLICE (NS) TERMINATION REQUEST
## Objctive: send the ns termination request 2 GTK
## Params: nsiId (uuid within the incoming request URL)
class thread_ns_terminate(Thread):
  def __init__(self, NSI, nsi_json):
    Thread.__init__(self)
    self.NSI = NSI
    self.req = nsi_json
  
  def send_termination_requests(self):
    LOG.info("Terminating Slice: ")

    data = {}
    data["instance_uuid"] = self.NSI['id']
    data["request_type"] = "TERMINATE_SLICE"

    # calls the function towards the GTK
    termination_response = sbi.net_serv_terminate(data)

    return termination_response[0], termination_response[1]
    #return ({},201)
  
  def run(self):

    # acquires mutex to have unique access to the nsi (rpositories)
    mutex_slice2db_access.acquire()
    
    # Change status
    if 'slice' in self.req:
      db.update_status_slice_subnet("DELETING",self.req['sliceName'],self.req['slice'])
    else:
      db.update_status_slice("DELETING",self.req['sliceName'])

    # sends each of the termination requests
    LOG.info("Termination Step: Terminating Network Slice Instantiation.")

    # requests to terminate a NSI
    termination_resp = self.send_termination_requests()
    if termination_resp[1] != 201:
      self.NSI['nsi-status'] = 'ERROR'
      self.NSI['errorLog'] = 'ERROR when terminating '
      # Change status
      if 'slice' in self.req:
        db.update_status_slice_subnet("ERROR",self.req['sliceName'],self.req['slice'])
      else:
        db.update_status_slice("ERROR",self.req['sliceName'])

    
    # releases mutex for any other thread to acquire it
    mutex_slice2db_access.release()

    if self.NSI['nsi-status'] != 'ERROR':
      # Waits until the NS is terminated or error
      deployment_timeout = 30 * 60   # 30 minutes

      nsi_terminated = False
      while deployment_timeout > 0:
        # Check ns instantiation status
        self.NSI = sbi.get_saved_nsi(self.NSI['id'])
      
        self.NSI["id"] = self.NSI["uuid"]
        del self.NSI["uuid"]
        
        if self.NSI['nsi-status'] in ["TERMINATED", "ERROR"]:
          nsi_terminated = True
        
        # if slice is terminated or error, break the while loop to notify the GTK
        if nsi_terminated:
          LOG.info("Network Slice Termination request processed for Network Slice with ID: "+str(self.NSI['id']))
          # Change status
          if 'slice' in self.req:
            db.update_status_slice_subnet("DELETED",self.req['sliceName'],self.req['slice'])
          else:
            db.update_status_slice("DELETED",self.req['sliceName'])
            db.del_slice(self.req['sliceName'])
          break
    
        time.sleep(15)
        deployment_timeout -= 15
    
      if not nsi_terminated:
        self.NSI['nsi-status'] = 'ERROR'
        self.NSI['errorLog'] = 'ERROR when terminating with timeout'
        # Change status
        if 'slice' in self.req:
          db.update_status_slice_subnet("ERROR",self.req['sliceName'],self.req['slice'])
        else:
          db.update_status_slice("ERROR",self.req['sliceName'])


  
################################ SLICE CREATION SECTION ##################################

# Does all the process to Create the Slice
def create_slice(nsi_json):
  LOG.info("Check for NstID before instantiating it.")
  nstId = nsi_json['sliceTemplateId']
  catalogue_response = sbi.get_saved_nst(nstId)
  if catalogue_response.get('nstd'):
    nst_json = catalogue_response['nstd']
  else:
    return catalogue_response, catalogue_response['http_code']

  # validate if there is any NSTD
  if not catalogue_response:
    return_msg = {}
    return_msg['error'] = "There is NO Slice Template with this uuid in the DDBB."
    return return_msg, 400

  # check if exists another nsir with the same name (sliceName)
  nsirepo_jsonresponse = sbi.get_all_saved_nsi()
  if nsirepo_jsonresponse:
    for nsir_item in nsirepo_jsonresponse:
      if (nsir_item["name"] == nsi_json['sliceName']):
        return_msg = {}
        return_msg['error'] = "There is already an slice with this name."
        return (return_msg, 400)
     
    # Network Slice Placement
  LOG.info("Placement of the Network Service Instantiations.")
  new_nsi_json = nsi_placement(nsi_json, nst_json)

  if new_nsi_json[1] != 200:
    LOG.info("Error returning saved nsir.")
    return (new_nsi_json[0], new_nsi_json[1])
  
  # starts the thread to instantiate while sending back the response
  LOG.info("Network Slice Instance Record created. Starting the instantiation procedure.")
  thread_ns_instantiation = thread_ns_instantiate(new_nsi_json[0])
  thread_ns_instantiation.start()

  #return 202 for sliceSubnet and 201 for slice
  if 'slice' in nsi_json:
    return ({},202)
  else:
    return ({},201)
  
# does the NS placement based on the available VIMs resources & the required of each NS.
def nsi_placement(nsi_json, nst_json):

  # get the VIMs information registered to the SP
  vims_list = sbi.get_vims_info()

  # validates if the incoming vim_list is empty (return 500) or not (follow)
  if not 'vim_list' in vims_list:
    return_msg = {}
    return_msg['error'] = "Not found any VIM information, register one to the SP."
    return return_msg, 500

  # NSR PLACEMENT: placement based on the instantiation parameters...
  vimId = ""
  if 'location' in nsi_json:
    for vim_item in vims_list['vim_list']:
      if (vim_item['type'] == "vm" and vim_item['vim_uuid'] == nsi_json['location']):
        vimId = vim_item['vim_uuid']
        break 
  else:
    # TODO For when vimId is not specified in the api
    city = "IT"
    for vim_item in vims_list['vim_list']:
      if (vim_item['type'] == "vm" and vim_item['vim_city'] == city):
        vimId = vim_item['vim_uuid']
        break

  if vimId != "":
    instantiation_params_list = []
    for subnet_item in nst_json["slice_ns_subnets"]:
      service_dict = {}
      service_dict["vim_id"] = vimId
      service_dict["subnet_id"] = subnet_item["id"]
      instantiation_params_list.append(service_dict)
    nsi_json['instantiation_params'] = json.dumps(instantiation_params_list)
  
  return nsi_json, 200

# Does all the process to Create the Slice Subnet
def create_slice_subnet(nsi_json,sliceName):

  # TODO: For not give error when creating the subnet again
  # If already exist this subnet return 202
  slice_info=db.get_slice(sliceName)
  if "sliceSubnetIds" in slice_info:
    if nsi_json['sliceSubnetName'] in slice_info["sliceSubnetIds"]:
      return ({},202)

  LOG.info("Create Slice Subnet")

  new_nsi_json = {}
  new_nsi_json['slice'] = sliceName
  new_nsi_json['sliceName'] = nsi_json['sliceSubnetName']
  new_nsi_json['sliceTemplateId'] = nsi_json['sliceSubnetTemplateId']
  if 'location' in nsi_json:
    new_nsi_json['location']=nsi_json['location']

  return create_slice(new_nsi_json)

########################################## SLICE DELETION SECTION #######################################

# Does all the process to delete the slice
def delete_slice(nsi_json):
  #LOG.info("Updating the Network Slice Record for the termination procedure.")
  mutex_slice2db_access.acquire()
  try:
    # Get the uuid form the name provided
    uuid = sbi.get_nsi_id_from_name(nsi_json['sliceName'])
    if (uuid):
      terminate_nsi = sbi.get_saved_nsi(uuid)
      if terminate_nsi:
        # if nsi is not in TERMINATING/TERMINATED
        if terminate_nsi['nsi-status'] in ["INSTANTIATED", "INSTANTIATING", "READY", "ERROR"]:
          terminate_nsi['id'] = terminate_nsi['uuid']
          del terminate_nsi['uuid']
        
          terminate_nsi['terminateTime'] = str(datetime.datetime.now().isoformat())
          #terminate_nsi['sliceCallback'] = TerminOrder['callback']
          terminate_nsi['nsi-status'] = "TERMINATING"

          # starts the thread to terminate while sending back the response
          LOG.info("Starting the termination procedure.")
          thread_ns_termination = thread_ns_terminate(terminate_nsi, nsi_json)
          thread_ns_termination.start()

          #return 202 for sliceSubnet and 204 for slice
          if 'slice' in nsi_json:
            terminate_value = 202
          else:
            terminate_value = 204
            
            
        else:
          terminate_nsi['errorLog'] = "This Slice is either terminated or being terminated."
          terminate_value = 404
      else:
        terminate_nsi['errorLog'] = "There is no Slice with this name in the db."
        terminate_value = 404
    else:
      terminate_nsi = {}
      terminate_nsi['errorLog'] = "There is no Slice with this name in the db."
      terminate_value = 404
  finally:
    mutex_slice2db_access.release()
    return (terminate_nsi, terminate_value)

# Does all the process to Delete the Slice Subnet
def delete_slice_subnet(nsi_json,sliceName):
  LOG.info("Delete Slice Subnet")

  new_nsi_json = {}
  new_nsi_json['slice'] = sliceName
  new_nsi_json['sliceName'] = nsi_json['sliceSubnetName']

  return delete_slice(new_nsi_json)

########################################## ADD SLICE SECTION #######################################

# Does all the process to add the slice to subnet
def add_slice_subnet(nsi_json, sliceName):
  LOG.info("Add Slice Subnet")

  # Change status
  db.update_status_slice_subnet("ADDING",nsi_json["sliceSubnetName"], sliceName)
  #TODO Order Configuration
  dict_message={"name":"api", "id":"", "action":"add","slice":sliceName,"subnetSlice":nsi_json["sliceSubnetName"]}
  #threading.Thread(target=client_ssm_thread,args=(dict_message,)).start()
  message = client_ssm_thread(dict_message)
  db.update_status_slice_subnet("ADDED",nsi_json["sliceSubnetName"], sliceName)

  return ({"message": message},202)

########################################## REMOVE SLICE SECTION #######################################

# Does all the process to remove the slice to subnet
def remove_slice_subnet(nsi_json, sliceName):
  LOG.info("Remove Slice Subnet")

  # Change status
  db.update_status_slice_subnet("REMOVING",nsi_json["sliceSubnetName"], sliceName)
  #TODO Order Configuration
  dict_message={"name":"api", "id":"", "action":"remove","slice":sliceName,"subnetSlice":nsi_json["sliceSubnetName"]}
  #threading.Thread(target=client_ssm_thread,args=(dict_message,)).start()
  message = client_ssm_thread(dict_message)
  db.update_status_slice_subnet("REMOVED",nsi_json["sliceSubnetName"], sliceName)

  return ({"message": message},202)

########################################## Registration SECTION #######################################

# Does all the process to registration the UE
def registration(nsi_json, sliceName):
  LOG.info("Registration UE")

  # Change status
  db.update_status_slice_subnet("UNDER_REGISTRATION",nsi_json["sliceSubnet"], sliceName)
  #TODO Order Registration
  dict_message={"name":"api", "id":"", "action":"registration","slice":sliceName,"subnet":nsi_json["sliceSubnet"]}
  #threading.Thread(target=client_ssm_thread,args=(dict_message,)).start()
  message = client_ssm_thread(dict_message)
  # Change status
  db.update_status_slice_subnet("FINISHED_REGISTRATION",nsi_json["sliceSubnet"], sliceName)
  return ({"message": message},202)

########################################## HANDOVER SECTION #######################################

# Does all the process to handover the UE between Edges
def handover(nsi_json, sliceName):
  LOG.info("Handover UE")

  # Change status
  db.update_status_slice_subnet("UNDER_HANDOVER",nsi_json["sliceSubnetSrc"], sliceName)
  db.update_status_slice_subnet("UNDER_HANDOVER",nsi_json["sliceSubnetDst"], sliceName)
  #TODO Order Handover
  dict_message={"name":"api", "id":"", "action":"handover","slice":sliceName,"subnetSrc":nsi_json["sliceSubnetSrc"],"subnetDst":nsi_json["sliceSubnetDst"]}
  #threading.Thread(target=client_ssm_thread,args=(dict_message,)).start()
  message = client_ssm_thread(dict_message)
  # Change status
  db.update_status_slice_subnet("FINISHED_HANDOVER",nsi_json["sliceSubnetSrc"], sliceName)
  db.update_status_slice_subnet("FINISHED_HANDOVER",nsi_json["sliceSubnetDst"], sliceName)
  return ({"message": message},202)

# Status options
""" public enum Status {

	CREATING,
	CREATED,
	ADDING,
  ADDED,
  UNDER_REGISTRATION,
  FINISHED_REGISTRATION,
  UNDER_HANDOVER,
  FINISHED_HANDOVER,
  REMOVING,
  REMOVED,
	DELETING,
	DELETED,
	ERROR
	
} """

########################################## STATUS SECTION #######################################

# Does all the process to get the status
"""
Database model
{
  "<sliceName>": {
    "status": "<status>",
    "sliceSubnetIds": {
      "<sliceSubnetName>": {
        "status": "<status>"
      }
    }
  }
}

Return
{
  "sliceName": "<sliceName>",
  "status": "<status>",
  "sliceSubnetIds": [
    {
      "sliceSubnetName": "<sliceSubnetName>",
      "status": "<status>"
    },
    {
      "sliceSubnetName": "<sliceSubnetName>",
      "status": "<status>"
    },
    ...
  ]
}
"""

def get_slice_status(sliceName):
  LOG.info("Get Slice Status")
  slice_status = {}

  # Check if slice exists
  all_slice_info = db.get_all_slices()
  if not sliceName in all_slice_info:
    return (slice_status,404)

  # Get status for a specific slice
  slice_info = db.get_slice(sliceName)

  if slice_info:
    slice_status["sliceName"] = sliceName
    slice_status["status"] = slice_info["status"]
    if "sliceSubnetIds" in slice_info:
      slice_status["sliceSubnetIds"]= []
      for slice_subnet_name in slice_info["sliceSubnetIds"]:
        slice_subnet_info={}
        slice_subnet_info["sliceSubnetName"]= slice_subnet_name
        slice_subnet_info["status"]= slice_info["sliceSubnetIds"][slice_subnet_name]["status"]
        slice_status["sliceSubnetIds"].append(slice_subnet_info) 

  return (slice_status,200)

# Does all the process to get the status of all slices
"""
Database model
{
  "<sliceName>": {
    "status": "<status>",
    "sliceSubnetIds": {
      "<sliceSubnetName>": {
        "status": "<status>"
      }
    }
  }
}

Return
[
  {
    "sliceName": "<sliceName>",
    "status": "<status>",
    "sliceSubnetIds": [
      {
        "sliceSubnetName": "<sliceSubnetName>",
        "status": "<status>"
      },
      {
        "sliceSubnetName": "<sliceSubnetName>",
        "status": "<status>"
      }
    ]
  },
  ...
]
"""

def get_all_slice_status():
  LOG.info("Get All Slice Status")

  # Get status for all slices
  all_slice_status = []
  all_slice_info = db.get_all_slices()
  for slice_name in all_slice_info:

    slice_status = {}
    slice_info = all_slice_info[slice_name]

    slice_status["sliceName"] = slice_name
    slice_status["status"] = slice_info["status"]
    if "sliceSubnetIds" in slice_info:
      slice_status["sliceSubnetIds"]= []
      for slice_subnet_name in slice_info["sliceSubnetIds"]:
        slice_subnet_info={}
        slice_subnet_info["sliceSubnetName"]= slice_subnet_name
        slice_subnet_info["status"]= slice_info["sliceSubnetIds"][slice_subnet_name]["status"]
        slice_status["sliceSubnetIds"].append(slice_subnet_info)

    all_slice_status.append(slice_status)

  return (all_slice_status,200)
