# rethinkdb-cluster - Autopilot Container for RethinkDB

## Available Tags

* ```2.3.2```,```latest``` (2.3.2/Dockerfile)

## Description
Implements the auto-pilot pattern for RethinkDB. The container will automatically communuicate with Consul to determine whether it is the first node for the cluster and behave accordingly. Once operational, the node will be registered into Consul

## Environment Variables
This image can utilise the following variables

* ```CONSUL_ADDRESS``` sets the address of the Consul instance to register against. This should be in the form of ```hostname:8500``` such as ```discovery.provider.com:8500```. 
* ```SERVICE_NAME``` the name of the service that will be registered into Consul.

## Important Ports

* ```tcp/8080``` Web UI/Administration console
* ```tcp/28015``` Client/Data port
* ```tcp/29015``` Intra-cluster communications

## Data Directories

* ```/data``` Designated as a separate volume in which Redis stores any persistent data
