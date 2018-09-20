from aloe import world
from iota import Iota
from util import static_vals

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



def prepare_api_call(nodeName):
    logger.info('Preparing api call')
    host = world.machine['nodes'][nodeName]['host']
    port = world.machine['nodes'][nodeName]['ports']['api']
    address ="http://"+ host + ":" + str(port)
    api = Iota(address)
    logger.info('API call prepared for %s',address)
    return api


def check_responses_for_call(apiCall):
    steps = import_steps()
    if len(steps.responses[apiCall]) > 0:
        return True
    else:
        return False
    
def fetch_response(apiCall):
    steps = import_steps()
    return steps.responses[apiCall]


def fetch_config(key):
    steps = import_steps()
    return steps.config[key]


def check_neighbors(step,node):
    steps = import_steps()
    api = prepare_api_call(node)
    response = api.getNeighbors()
    logger.info('Response: %s',response)
    containsNeighbor = [False,False]
    
    for i in response:
        expectedNeighbors = step.hashes
        if type(response[i]) != int:
            for x in range(len(response[i])):    
                if expectedNeighbors[0]['neighbors'] == response[i][x]['address']:
                    containsNeighbor[0] = True  
                if expectedNeighbors[1]['neighbors'] == response[i][x]['address']:
                    containsNeighbor[1] = True  
    
    return containsNeighbor

def import_steps():
    import tests.features.steps.api_test_steps as steps
    return steps


def prepare_options(args,optionList):
    for x in range(len(args)):
        if len(args) != 0:
            key = args[x]['keys']
            value = args[x]['values']
            arg_type = args[x]['type']

            if arg_type == "int":
                value = int(value)
            elif arg_type == "nodeAddress":
                host = world.machine['nodes'][value]['host']
                port = world.machine['nodes'][value]['ports']['gossip-udp']
                address = "udp://" + host + ":" + str(port)
                value = [address.decode()]
            elif arg_type == "staticValue":
                value = getattr(static_vals,value)
            elif arg_type == "staticList":
                address = getattr(static_vals,value)
                value = [address]

            optionList[key] = value

