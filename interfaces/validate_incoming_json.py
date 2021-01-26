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

import datetime, logging
from uuid import UUID
from logger import TangoLogger

# Global variables
returnData = {}

#Log definition to make the slice logs idetified among the other possible 5GTango components.
LOG = TangoLogger.getLogger(__name__, log_level=logging.DEBUG, log_json=True)
TangoLogger.getLogger("resistoApi:json_validator", logging.DEBUG, log_json=True)
LOG.setLevel(logging.DEBUG)

# Checks if the uuid has the right format (uuidv4)
def is_valid_uuid(uuid_to_test, version=4):
    try:
        uuid_obj = UUID(uuid_to_test, version=version)
    except:
        return False
    return str(uuid_obj) == uuid_to_test

# Validates the incoming json to create Slice.
def validate_create_slice (jsonData):
  if 'sliceName' in jsonData and 'sliceTemplateId' in jsonData:
    returnData["missing_field"] = "Everything is OK!!"
    return (returnData, 200)
  else:
      returnData["missing_field"] = "Check if you request has a sliceTemplateId and a sliceName."
      LOG.info('FormValidator NBI_Error: ' + str(returnData))
      return (returnData, 400)

# Validates the incoming json to create Slice Subnet.
def validate_create_slice_subnet (jsonData):
  if 'sliceSubnetName' in jsonData and 'sliceSubnetTemplateId' in jsonData:
    returnData["missing_field"] = "Everything is OK!!"
    return (returnData, 200)
  else:
      returnData["missing_field"] = "Check if you request has a sliceSubnetTemplateId and a sliceSubnetName."
      LOG.info('FormValidator NBI_Error: ' + str(returnData))
      return (returnData, 400)

# Validates the incoming json to add Slice Subnet.
def validate_add_slice_subnet (jsonData):
  if 'sliceSubnetName' in jsonData:
    returnData["missing_field"] = "Everything is OK!!"
    return (returnData, 200)
  else:
      returnData["missing_field"] = "Check if you request has a sliceSubnetName."
      LOG.info('FormValidator NBI_Error: ' + str(returnData))
      return (returnData, 400)

# Validates the registration.
def validate_registration (jsonData):
  if 'sliceSubnet' in jsonData:
    returnData["missing_field"] = "Everything is OK!!"
    return (returnData, 200)
  else:
      returnData["missing_field"] = "Check if you request has a sliceSubnet."
      LOG.info('FormValidator NBI_Error: ' + str(returnData))
      return (returnData, 400)

# Validates the handover.
def validate_handover (jsonData):
  if 'sliceSubnetSrc' in jsonData and 'sliceSubnetDst' in jsonData:
    returnData["missing_field"] = "Everything is OK!!"
    return (returnData, 200)
  else:
      returnData["missing_field"] = "Check if you request has a sliceSubnetSrc and a sliceSubnetDst."
      LOG.info('FormValidator NBI_Error: ' + str(returnData))
      return (returnData, 400)

# Validates the incoming json to remove Slice Subnet.
def validate_remove_slice_subnet (jsonData):
  if 'sliceSubnetName' in jsonData:
    returnData["missing_field"] = "Everything is OK!!"
    return (returnData, 200)
  else:
      returnData["missing_field"] = "Check if you request has a sliceSubnetName."
      LOG.info('FormValidator NBI_Error: ' + str(returnData))
      return (returnData, 400)

# Validates the incoming json to delete Slice Subnet.
def validate_delete_slice_subnet (jsonData):
  if 'sliceSubnetName' in jsonData:
    returnData["missing_field"] = "Everything is OK!!"
    return (returnData, 200)
  else:
      returnData["missing_field"] = "Check if you request has a sliceSubnetName."
      LOG.info('FormValidator NBI_Error: ' + str(returnData))
      return (returnData, 400)

# Validates the incoming json to delete Slice.
def validate_delete_slice (jsonData):
  if 'sliceName' in jsonData:
    returnData["missing_field"] = "Everything is OK!!"
    return (returnData, 200)
  else:
      returnData["missing_field"] = "Check if you request has a sliceName."
      LOG.info('FormValidator NBI_Error: ' + str(returnData))
      return (returnData, 400)
