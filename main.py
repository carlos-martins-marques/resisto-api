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

import os, logging, json

from tornado import websocket, web, ioloop, httpserver

from interfaces.nbi import app

from slice_manager.script_ssm_slice import app_ssm

from logger import TangoLogger

import threading

import asyncio

#Log definition to make the slice logs idetified among the other possible 5GTango components.
LOG = TangoLogger.getLogger(__name__, log_level=logging.DEBUG, log_json=True)
TangoLogger.getLogger("resistoApi:main", logging.DEBUG, log_json=True)
LOG.setLevel(logging.DEBUG)

def app_ssm_thread():
  asyncio.set_event_loop(asyncio.new_event_loop())
  http_server = httpserver.HTTPServer(app_ssm)
  http_server.listen(4001)
  ioloop.IOLoop.instance().start()

########################################### MAIN SERVER FUNCTION ############################################
if __name__ == '__main__':

  # RUN APP SLICE SSM THREAD
  #http_server = httpserver.HTTPServer(app_ssm)
  #http_server.listen(4001)
  #ioloop.IOLoop.instance().start()
  threading.Thread(target=app_ssm_thread).start()

  # RUN API MAIN SERVER THREAD
  app.run(debug=True, host='0.0.0.0', port=os.environ.get("RESISTO_API_PORT"))