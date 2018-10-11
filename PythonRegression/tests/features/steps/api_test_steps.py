from aloe import *
from iota import ProposedTransaction,Address,Tag,TryteString,ProposedBundle,Transaction

from util import static_vals
from util.test_logic import api_test_logic as api_utils
from util.threading_logic import thread_logic as threads
from util.transaction_bundle_logic import transaction_logic as transactions
from util.neighbor_logic import neighbor_logic as neighbors
from time import sleep

import logging 
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

testAddress = static_vals.TEST_ADDRESS

world.config = {}
world.responses = {}


'''
This is the general api calling function. There are 3 inputs

@param apiCAll:     The api call that will be requested
@param nodeName:    The name identifying the node you would like to make this request on
@param table:       A gherkin table outlining any arguments needed for the call
                    (See tests/features/machine1/1_api+tests.feature for examples) 

    The table parameter is unique in that there are several input types available depending on the call
    being made. 
    Types:
        string:         Basic string argument, will be taken as is
        list:           Places string in list 
        int:            Basic integer argument, will be converted to int before call is made
        nodeAddress:    Node name identifier, will create address from node configuration 
        staticValue:    Static name identifier, will fetch value from util/static_vals.py 
        staticList:     Same as staticValue, except it places the results into a list 
        responseValue:  Identifier for api call response value
        responseList:   Same as responseValue, ecept it places the results into a list
        bool:           Bool argument, returns True or False
         
'''
@step(r'"([^"]*)" is called on "([^"]*)" with:')
def api_method_is_called(step,apiCall,nodeName):
    logger.info('%s is called on %s',apiCall,nodeName)
    world.config['apiCall'] = apiCall
    world.config['nodeId'] = nodeName
    arg_list = step.hashes

    options = {}
    api_utils.prepare_options(arg_list, options)

    api = api_utils.prepare_api_call(nodeName)
    response = api_utils.fetch_call(apiCall, api, options)

    assert type(response) is dict, 'There may be something wrong with the response format: {}'.format(response)
    
    world.responses[apiCall] = {}
    world.responses[apiCall][nodeName] = response

#This method is identical to the method above, but creates a new thread
@step(r'"([^"]*)" is called in parallel on "([^"]*)" with:')
def threaded_api_call(step,apiCall,node):
    logger.info("Creating thread for {}".format(apiCall))
    world.config['apiCall'] = apiCall
    world.config['nodeId'] = node
    arg_list = step.hashes

    options = {}
    api_utils.prepare_options(arg_list, options)
    api = api_utils.prepare_api_call(node)

    q = threads.populate_queue(world.responses,world.config)
    threads.make_thread(api_utils.make_api_call,api,options,q)
    #Wait 3 seconds to give node time to respond
    sleep(1)


'''
This method makes an apiCall a specified number of times and stores the responses in the aloe.world object.

@param apiCall:     The api call that you wish to make
@param numTests:    The number of times you would like to make the call
@param node:        The node you'd like to make the calls on
@param table:       Gherkin table with api call arguments
'''

@step(r'"([^"]*)" is called (\d+) times on "([^"]*)" with:')
def spam_call_gtta(step,apiCall,numTests,node):
    world.config['apiCall'] = apiCall
    world.config['nodeId'] = node
    arg_list = step.hashes

    options = {}
    api_utils.prepare_options(arg_list, options)

    api = api_utils.prepare_api_call(node)
    logging.info('Calls being made to %s',node)
    responseList = []

    for i in range(int(numTests)):
        logging.debug("Call %d made", i+1)
        response = api_utils.fetch_call(apiCall,api,options)
        responseList.append(response)
        
    world.responses[apiCall] = {}
    world.responses[apiCall][node] = responseList


###
#Transaction Generator
@step(r'a transaction is generated and attached on "([^"]*)" with:')
def generate_transaction_and_attach(step,node):
    arg_list = step.hashes
    world.config['nodeId'] = node
    world.config['apiCall'] = 'attachToTangle'

    options = {}
    api = api_utils.prepare_api_call(node)
    api_utils.prepare_options(arg_list, options)

    transaction_args = {}
    for key in options:
        transaction_args[key] = options.get(key)
    api_utils.prepare_transaction_arguments(transaction_args)

    transaction = transactions.create_and_attach_transaction(api,transaction_args)
    api.broadcast_and_store(transaction.get('trytes'))

    world.responses['attachToTangle'] = {}
    world.responses['attachToTangle'][node] = transaction
    logger.info('Transaction Sent')

    setattr(static_vals, "TEST_STORE_TRANSACTION", transaction.get('trytes'))



'''
Creates an inconsistent transaction by generating a zero value transaction that references 
a non-existent transaction as its branch and trunk, thus not connecting with any other part 
of the tangle.
'''
@step(r'an inconsistent transaction is generated on "([^"]*)"')
def create_inconsistent_transaction(step,node):
    world.config['nodeId'] = node
    api = api_utils.prepare_api_call(node)
    trunk = getattr(static_vals,"NULL_HASH")
    branch = trunk
    trytes = getattr(static_vals,"EMPTY_TRANSACTION_TRYTES")

    argument_list = {'trunk_transaction': trunk, 'branch_transaction': branch,
                     'trytes': [trytes], 'min_weight_magnitude': 14}

    transaction = transactions.attach_store_and_broadcast(api,argument_list)
    transaction_trytes = transaction.get('trytes')
    transaction_hash = Transaction.from_tryte_string(transaction_trytes[0])

    if 'inconsistentTransactions' not in world.responses:
        world.responses['inconsistentTransactions'] = {}

    world.responses['inconsistentTransactions'][node] = transaction_hash.hash


###
#Test transactions
@step(r'"([^"]*)" and "([^"]*)" are neighbors')
def make_neighbors(step,node1,node2):
    neighbor_candidates = [node1,node2]
    neighbor_info = {}

    for node in range(len(neighbor_candidates)):
        node = neighbor_candidates[node]
        host = world.machine['nodes'][node]['podip']
        port = world.machine['nodes'][node]['clusterip_ports']['gossip-udp']
        api = api_utils.prepare_api_call(node)
        response = api.get_neighbors()
        neighbor_info[node] = {
            'api': api,
            'node_neighbors': list(response['neighbors']),
            'address': str(host) + ":" + str(port)
        }

    logger.info('Checking neighbors for {}'.format(node1))
    neighbors.check_if_neighbors(neighbor_info[node1]['api'],
                                 neighbor_info[node1]['node_neighbors'], neighbor_info[node2]['address'])

    logger.info('Checking neighbors for {}'.format(node2))
    neighbors.check_if_neighbors(neighbor_info[node2]['api'],
                                 neighbor_info[node1]['node_neighbors'], neighbor_info[node2]['address'])



def check_responses_for_call(apiCall):
    if len(world.responses[apiCall]) > 0:
        return True
    else:
        return False

def fill_response(apiCall,response):
    world.responses[apiCall] = response

def fill_config(key,value):
    world.config[key] = value

def fetch_config(key):
    return world.config[key]
    
def fetch_response(apiCall):
    return world.responses[apiCall]


