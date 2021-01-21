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

import os, requests, json, logging
from logger import TangoLogger

JSON_CONTENT_HEADER = {'Content-Type':'application/json'}

#Log definition to make the slice logs idetified among the other possible 5GTango components.
LOG = TangoLogger.getLogger(__name__, log_level=logging.DEBUG, log_json=True)
TangoLogger.getLogger("resistoApi:sbi", logging.DEBUG, log_json=True)
LOG.setLevel(logging.DEBUG)


######################################### URLs PREPARATION #########################################
# Returns the last URL version to send requests to the Catalogues Docker
def get_url_catalogues():
  ip_address = os.environ.get("SONATA_CAT")
  port = os.environ.get("SONATA_CAT_PORT")
  #ip_address = "193.136.92.119"
  #port = "4011"
  base_url = 'http://'+ip_address+':'+port
  return base_url
    
# Prepares the URL_requests to manage Network Services instantiations belonging to the NST/NSI
def get_url_sp_gtk():
  ip_address = os.environ.get("SONATA_GTK_SP")
  port = os.environ.get("SONATA_GTK_SP_PORT")
  #ip_address = "193.136.92.119"
  #port = "5000"
  base_url = 'http://'+ip_address+':'+port
  return base_url

# Returns the last URL version to send requests to the Repositories Docker
def get_url_repositories():
    ip_address = os.environ.get("SONATA_REP")
    port = os.environ.get("SONATA_REP_PORT")
    #ip_address = "193.136.92.119"
    #port = "4012"
    base_url = 'http://'+ip_address+':'+port
    return base_url


##################################### VIM NETWORKS MANAGEMENT REQUESTS ##############################
'''
Objective: Request to get all registered VIMs information
  Params: null
  Request payload: null
  Return:
  {
    vim_list: [
      {
        vim_uuid: String,
        type: String,
        vim_city: String,
        vim_domain: String,
        vim_name: String,
        vim_endpoint: String,
        memory_total: int,
        memory_used: int,
        core_total: int,
        core_used: int
      }
    ],
    nep_list: [
      {
        nep_uuid: String,
        type: String,
        nep_name: String
      }
    ]
  } 
'''
def get_vims_info():
  LOG.info("Requesting VIMs information.")
  url = get_url_sp_gtk() + '/slices/vims'
  response = requests.get(url, headers=JSON_CONTENT_HEADER)
  
  if (response.status_code == 200):
      jsonresponse = json.loads(response.text)
  else:
      jsonresponse = {'http_code': response.status_code,'message': response.reason}
      LOG.info(" Retrieving VIMs information FAILED: " +str(jsonresponse))

  return jsonresponse
################################ NETWORK SERVICES REQUESTS/RECORDS ##################################
# POST /requests to INSTANTIATE Network Slice instance
def net_serv_instantiate(slice_data):
  url = get_url_sp_gtk() + '/requests'
  data_json = json.dumps(slice_data)
  response = requests.post(url, data=data_json, headers=JSON_CONTENT_HEADER)
  jsonresponse = json.loads(response.text)
  
  return jsonresponse, response.status_code

# POST /requests to TERMINATE Network Slice instance
def net_serv_terminate(slice_data):
  url = get_url_sp_gtk() + "/requests"
  data_json = json.dumps(slice_data)
  response = requests.post(url, data=data_json, headers=JSON_CONTENT_HEADER)
  
  if (response.status_code == 200) or (response.status_code == 201):
    jsonresponse = json.loads(response.text)
  else:
    jsonresponse = {'http_code': response.status_code,'message': response.json()}
  return jsonresponse, response.status_code

  
# GET /requests to pull the information of all requests
def get_all_nsr():
  url = get_url_sp_gtk() + "/requests"
  response = requests.get(url, headers=JSON_CONTENT_HEADER)
  
  if (response.status_code == 200):
      jsonresponse = json.loads(response.text)
  else:
      jsonresponse = {'http_code': response.status_code,'message': response.json()}
  return jsonresponse

# GET /requests/<request_uuid> to pull the information of a single request id
def get_nsr(request_uuid):
  url = get_url_sp_gtk() + "/requests/" + str(request_uuid)
  response = requests.get(url, headers=JSON_CONTENT_HEADER)
  
  if (response.status_code == 200):
      jsonresponse = json.loads(response.text)
  else:
      jsonresponse = {'http_code': response.status_code,'message': response.json()}
  return jsonresponse

# GET all NSI items from the repositories
def get_all_saved_nsi():
    url = get_url_repositories() + '/records/nsir/ns-instances'
    response = requests.get(url, headers=JSON_CONTENT_HEADER)
    jsonresponse = json.loads(response.text)
    
    if(response.status_code != 200):
        jsonresponse = {'http_code': response.status_code,'message': response.json()}
        LOG.info("Retrieving all Network Slice Instance records FAILED: " + str(jsonresponse))
    
    return jsonresponse


# GET specific NSI item from the repositories
def get_saved_nsi(nsiId):
    url = get_url_repositories() + '/records/nsir/ns-instances/' + nsiId
    response = requests.get(url, headers=JSON_CONTENT_HEADER)

    if(response.status_code != 200):
        jsonresponse = {'http_code': response.status_code,'message': response.reason}
        LOG.info("Retrieving Network Slice Instance record with ID: " +str(nsiId)+ " FAILED.")
    else:
        jsonresponse = json.loads(response.text)

    return jsonresponse

# GET NSI Id from name (from the repositories)
def get_nsi_id_from_name(name):
    nsi_list = get_all_saved_nsi()
    if (nsi_list):
      for nsi_item in nsi_list:
        if nsi_item['name'] == name:
          return nsi_item['uuid']


################################# NETWORK SLICE DESCRIPTORS #####################################

# GET the specific NST item from the catalogues
def get_saved_nst(nstId):
    LOG.info("Requesting Network Slice Template Descriptor with ID: " +str(nstId))
    url = get_url_catalogues() + '/api/catalogues/v2/nsts/' + nstId
    response = requests.get(url, headers=JSON_CONTENT_HEADER)
    jsonresponse = json.loads(response.text)
    
    if (response.status_code != 200):
        jsonresponse = json.loads(response.text)
        jsonresponse['http_code'] = response.status_code
        LOG.info("Retrieveing Network Slice Template Descriptor FAILED: " + str(jsonresponse))
    
    return jsonresponse
    
  