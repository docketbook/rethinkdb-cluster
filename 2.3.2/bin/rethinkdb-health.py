from __future__ import print_function
import fcntl
import json
import logging
import os
import signal
import socket
import struct
import sys
import time

import rethinkdb
import consul as pyconsul

logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s %(message)s',
                    stream=sys.stdout,
                    level=logging.getLevelName(
                        os.environ.get('LOG_LEVEL', 'DEBUG')))
requests_logger = logging.getLogger('requests')
requests_logger.setLevel(logging.WARN)


log = logging.getLogger('rethinkdb-containerpilot')
# consul = pyconsul.Consul(host=os.environ.get('CONSUL_ADDRESS', 'consul'))
consulHost = os.environ.get('CONSUL_ADDRESS')
log.debug(consulHost[0:consulHost.index(':')])
# consul = pyconsul.Consul(host='172.18.0.2')
consul = pyconsul.Consul(host=consulHost[0:consulHost.index(':')])
config = None


class ContainerPilot(object):
    """
    ContainerPilot config is where we rewrite ContainerPilot's own config
    so that we can dynamically alter what service we advertise
    """

    def __init__(self, node):
        # TODO: we should make sure we can support JSON-in-env-var
        # the same as ContainerPilot itself
        self.node = node
        self.path = os.environ.get('CONTAINERPILOT').replace('file://', '')
        with open(self.path, 'r') as f:
            self.config = json.loads(f.read())

    def update(self):
        state = self.node.get_state()
        if state and self.config['services'][0]['name'] != state:
            self.config['services'][0]['name'] = state
            self.render()
            return True

    def render(self):
        new_config = json.dumps(self.config)
        log.info(new_config)
        with open(self.path, 'w') as f:
            f.write(new_config)

    def reload(self):
        """ force ContainerPilot to reload its configuration """
        log.info('Reloading ContainerPilot configuration.')
        os.kill(1, signal.SIGHUP)

# ---------------------------------------------------------
# Top-level functions called by ContainerPilot or forked by this program

def on_start():
    """
    Set up this node as the primary (if none yet exists), or the
    standby (if none yet exists), or replica (default case)
    """
    primary = get_nodes()
    if not primary or primary == get_name():
        log.debug('This is the first node')
        return
    else:
        log.debug('got nodes')
        log.debug("hosts")
        log.debug(primary)
        run_cluster(list(primary))
        return

def health():
    """
    Run a simple health check. Also acts as a check for whether the
    ContainerPilot configuration needs to be reloaded (if it's been
    changed externally), or if we need to make a backup because the
    backup TTL has expired.
    """
    log.debug('health check fired.')
    try:
        r = rethinkdb.connect('localhost', 28015)
        rethinkdb.db('rethinkdb').table('server_status').run(r)
        log.debug('I am a health check, beep boop');
        sys.exit(0)
    except Exception as ex:
        log.exception(ex)
        sys.exit(1)

def run_cluster(addresses):
    log.debug('Writing addresses to RethinkDB conf')

    with open('/etc/rethink.conf', 'w') as f:
        for host in addresses:
            join = 'join=%s:29015\n' % host
            f.write(join)
    return

def get_nodes(timeout=10):
    log.debug('get_primary_node')
    while timeout > 0:
        try:
            nodes = consul.catalog.nodes()
            nodeId = nodes[1][0]['Node']
            curr = consul.catalog.node(nodeId)
            checks = consul.health.node(nodeId)[1]
            services = curr[1]['Services']
            healthy = []
            for v in checks:
                if os.environ.get('SERVICE_NAME') in v['Name'] and v['Status'] == 'passing':
                    healthy.append(v['Name']);
            nodes = [ v['Address'] for k,v in services.items() if 'rethinkdb' in k and k in healthy]
            if len(nodes) > 0:
                log.debug('not primary - run config with joins')
                return nodes

            return None
        except Exception as ex:
            timeout = timeout - 1
            time.sleep(1)
    raise ex

def get_ip(iface='eth0'):
    """
    Use Linux SIOCGIFADDR ioctl to get the IP for the interface.
    ref http://code.activestate.com/recipes/439094-get-the-ip-address-associated-with-a-network-inter/
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    return socket.inet_ntoa(fcntl.ioctl(
        sock.fileno(),
        0x8915, # SIOCGIFADDR
        struct.pack('256s', iface[:15])
    )[20:24])

def get_name():
    return 'mysql-{}'.format(socket.gethostname())

# ---------------------------------------------------------

if __name__ == '__main__':

    if len(sys.argv) > 1:
        try:
            locals()[sys.argv[1]]()
        except KeyError:
            # log.error('Invalid command %s', sys.argv[1])
            sys.exit(1)
    else:
        # default behavior will be to start mysqld, running the
        # initialization if required
        on_start()
