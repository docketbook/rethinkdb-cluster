DOCKER_PROJECT_NAME=docketbook
DOCKER_GATEWAY_IP:=$$(docker network inspect $(DOCKER_PROJECT_NAME) | awk '/Gateway/ { gsub("\"", ""); split($$2,array,"/"); print array[1] }')
CONSUL_ADDRESS=discovery.development.services.docketbook.io
DOCKER_NODE_HOST_ARGS=--add-host $(CONSUL_ADDRESS):$(DOCKER_GATEWAY_IP) --net="$(DOCKER_PROJECT_NAME)" -e "CONSUL_ADDRESS=$(CONSUL_ADDRESS):8500"
DOCKER_NODE_STD_ARGS=-it --rm -p 8000
DOCKER_NODE_IMAGE=rethinkdb-node

ensureNetwork:
	docker network create $(DOCKER_PROJECT_NAME) > /dev/null 2>&1 || true;

startRethink: ensureNetwork
	export COMPOSE_PROJECT_NAME=$(DOCKER_PROJECT_NAME) && \
	export DISCOVERY_ADDRESS=$(DOCKER_GATEWAY_IP) && \
	docker-compose up rethinkdb;

run: ensureNetwork
	export COMPOSE_PROJECT_NAME=$(DOCKER_PROJECT_NAME) && \
	export DISCOVERY_ADDRESS=$(DOCKER_GATEWAY_IP) && \
	docker run $(DOCKER_NODE_STD_ARGS) $(DOCKER_NODE_HOST_ARGS) $(DOCKER_NODE_IMAGE)
devstop:
	export COMPOSE_PROJECT_NAME=$(DOCKER_PROJECT_NAME) && \
	export DISCOVERY_ADDRESS=$(DOCKER_GATEWAY_IP) && \
	docker-compose stop;

devclean: devstop
	docker-compose rm
