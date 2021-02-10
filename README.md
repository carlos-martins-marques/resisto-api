

# 5GTango Resisto Api (tng-resisto-api)
* Description: 5GTANGO Resisto Api
* Version: 1.0
* Actions:
    * Api for Resisto use case .


## Installing / Getting Started
It is **strongly recommended** to install this component with the whole SONATA SP. In order to install this component, please follow the procedure described in the official [5GTango](https://5gtango.eu/software/documentation.html) Documentation webpage.

If you still want to to install this component alone, just run the following command:

    python setup.py install

once installed, to start the component:

    python3 main.py

## Developing
To contribute to the development of this 5GTANGO component, you may use the very same development workflow as for any other 5GTANGO Github project:
1) you have to fork the repository and create pull requests.
2) you pull requests will be verified and merged once a reviewer accepts it.


### Built With
As the SONATA Service Platform is composed by multiple modules and all of them using Dockers, the Resisto Api environment and its dependencies are already installed within the Docker. This component uses the following dependencies:
* Flask (0.12.2)
* flask-restful
* python-dateutil
* python-uuid
* requests
* xmlrunner (1.7.7)

**INFORMATION NOTE:** these are minimum versions, it is not tested with the newest versions probably they should be fine. If there's no specific version, the newest versions should work fine but it is not tested.

### Prerequisits, Setting up Dev, Building and Deploying / Publishing
In order to have a full functionality, it is necessary to install the all the SONATA SP modules, further information in the [5GTango](https://5gtango.eu/software/documentation.html) Documentation webpage.

## Versioning
This is the V1.0 of this component, which work with SONATA SP 5.1 (developed by the EU 5GTango project)

## Configuration
No configuration is necessary, as the port where this component listens (8089) is already defined and agreed with the other SONATA SP components.


## API Reference
Each SONATA component has its API definition, the next sub-setions present a basic **tng-resisto-api** API information. Further information about the 5GTANGO software, click in the [Global SONATA API Webpage](https://sonata-nfv.github.io/tng-doc/?urls.primaryName=5GTANGO%20SDK%20Packager%20API%20v1).

#### APIs

| Action  | HTTP method  | Endpoint |
|---|---|---|
<!-- | CREATE A NETWORK SLICE IDENTIFIER  | POST  | /api/v1/ns  |
| INSTANTIATE A NETWORK SLICE | PUT  | /api/v1/ns/`<nsiId>`/action/instantiate  |
| REQUEST THE INFORMATION OF A NETWORK SLICE INSTANTIATION  | GET  | /api/v1/ns/`<nsiId>`|
| REQUEST THE INFORMATION OF ALL NETWORK SLICE INSTANTIATIONS  | GET  | /api/v1/ns  |
| TERMINATE A NETWORK SLICE INSTANTIATION  | PUT  | /api/v1/ns/`<nsiId>`/action/terminate| -->


## Database
This component uses the [tng-cat](https://github.com/sonata-nfv/tng-cat) and [tng-rep](https://github.com/sonata-nfv/tng-rep) as its database references. By using them, the Sonata Adapter data objects are kept in databases managed by thes two components.

## Licensing
This 5GTANGO component is published under Apache 2.0 license. Please see the [LICENSE](https://github.com/sonata-nfv/tng-sonata-adapter/blob/master/LICENSE) file for more details.

### Lead Developers
The following lead developers are responsible for this repository and have admin rights. They can, for example, merge pull requests.

  * Carlos Marques
