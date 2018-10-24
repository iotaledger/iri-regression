from aloe import *
from iota import ProposedTransaction,Address,Tag,TryteString,ProposedBundle,Transaction


from util import static_vals
from util.test_logic import api_test_logic as api_utils
from util.transaction_bundle_logic import transaction_logic as transactions
from util.threading_logic import pool_logic as pool
from util.neighbor_logic import neighbor_logic as neighbors
from time import sleep, time

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

testAddress = static_vals.TEST_ADDRESS

world.config = {}
world.responses = {}


@step(r'"([^"]+)" is called on "([^"]+)" with:')
def api_method_is_called(step,apiCall,nodeName):
    """
    This is the general api calling function. There are 3 inputs

    :param apiCall:     The api call that will be requested
    :param nodeName:    The name identifying the node you would like to make this request on
    :param table:       A gherkin table outlining any arguments needed for the call
                        (See tests/features/machine1/1_api_tests.feature for examples)

        The table parameter is unique in that there are several input types available depending on the call
        being made.
            :type string: Basic string argument, will be taken as is
            :type int: Basic integer argument, will be converted to int before call is made
            :type nodeAddress: Node name identifier, will create address from node configuration
            :type staticValue: Static name identifier, will fetch value from util/static_vals.py
            :type staticList: Same as staticValue, except it places the results into a list
            :type responseValue: Identifier for api call response value
            :type responseList: Same as responseValue, ecept it places the results into a list
            :type bool: Bool argument, returns True or False

    """
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


# This method is identical to the method above, but creates a new thread
@step(r'"([^"]+)" is called in parallel on "([^"]+)" with:')
def threaded_call(step,apiCall,node):
    logger.info("Creating thread for {}".format(apiCall))
    world.config['apiCall'] = apiCall
    world.config['nodeId'] = node
    arg_list = step.hashes

    options = {}
    api_utils.prepare_options(arg_list, options)
    api = api_utils.prepare_api_call(node)

    def make_call(node, arg_list):
        response = api_utils.fetch_call(apiCall, arg_list['api'], arg_list['options'])
        arg_list['responses'][apiCall] = {}
        arg_list['responses'][apiCall][node] = response
        return response

    args = {node: {'api': api,'options': options,'responses': world.responses}}
    future_results = pool.start_pool(make_call,1,args)

    if 'future_results' not in world.config:
        world.config['future_results'] = {}
    world.config['future_results'][apiCall] = future_results

    
@step(r'we wait "(\d+)" second/seconds')
def wait_for_step(step,time):
    logger.info('Waiting for {} seconds'.format(time))
    sleep(int(time))


@step(r'the "([^"]+)" parallel call should return with:')
def compare_thread_return(step,apiCall):
    """Prepare response list for comparison"""
    logger.debug(world.responses)
    future_results = world.config['future_results'][apiCall]

    for result in future_results:
        response_list = pool.fetch_results(result,1)
        # Exclude duration from response list
        if 'duration' in response_list:
            del response_list['duration']
        response_keys = response_list.keys()

        expected_values = {}
        api_utils.prepare_options(step.hashes,expected_values)
        keys = expected_values.keys()

        # Confirm that the lists are of equal length before comparing
        assert len(keys) == len(response_keys), 'Response: {} does not contain the same number of arguments: {}'.format(keys,response_keys)

        for count in range(len(keys)):
            response_key = response_keys[count]
            response_value = response_list[response_key]
            expected_value = expected_values[response_key]
            assert response_value == expected_value, \
                'Returned: {} does not match the expected value: {}'.format(response_value,expected_value)


@step(r'"([^"]*)" is called (\d+) times on "([^"]*)" with:')
def spam_call(step,apiCall,numTests,node):
    """Spams getTransactionsToApprove calls a number of times among available nodes in a cluster"""
    start = time()
    world.config['apiCall'] = apiCall
    arg_list = step.hashes
    nodes = {}
    responseVal = []

    api2 = api_utils.prepare_api_call('nodeA')
    logger.info(api2.get_node_info())

    options = {}
    api_utils.prepare_options(arg_list, options)

    # See if call will be made on one node or all
    if node == 'all nodes':
        for current_node in world.machine['nodes']:
            api = api_utils.prepare_api_call(current_node)
            nodes[current_node] = api
        node = next(iter(world.machine['nodes']))
        world.config['nodeId'] = node
    else:
        api = api_utils.prepare_api_call(node)
        nodes[node] = api
        world.config['nodeId'] = node


    def run_call(node,api):
        logger.debug('Running Thread on {}'.format(node))
        response = api.get_transactions_to_approve(depth=3)
        return response


    args = (nodes)
    future_results = pool.start_pool(run_call,numTests,args)

    instance = 0
    for result in future_results:
        instance += 1
        if instance % 25 == 0:
            logger.info('Fetching result: {}/{}'.format(instance,numTests))
        response = pool.fetch_results(result,30)
        responseVal.append(response)
        
    world.responses[apiCall] = {}
    world.responses[apiCall][node] = responseVal

    end = time()
    time_spent = end - start
    logger.info('Time spent on loop: {}'.format(time_spent))


###
# Transaction Generator
@step(r'a transaction is generated and attached on "([^"]+)" with:')
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

    assert len(transaction['trytes']) > 0
    world.responses['attachToTangle'] = {}
    world.responses['attachToTangle'][node] = transaction
    logger.info('Transaction Sent')

    setattr(static_vals, "TEST_STORE_TRANSACTION", transaction.get('trytes'))


@step(r'an inconsistent transaction is generated on "([^"]+)"')
def create_inconsistent_transaction(step,node):
    """
    Creates an inconsistent transaction by generating a zero value transaction that references
    a non-existent transaction as its branch and trunk, thus not connecting with any other part
    of the tangle.
    """
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

    logger.info(transaction_hash.hash)

    if 'inconsistentTransactions' not in world.responses:
        world.responses['inconsistentTransactions'] = {}

    world.responses['inconsistentTransactions'][node] = transaction_hash.hash

    if 'inconsistentTransactions' not in world.responses:
        world.responses['inconsistentTransactions'] = {}


###
# Test transactions
@step(r'"([^"]+)" and "([^"]+)" are neighbors')
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
                                 neighbor_info[node2]['node_neighbors'], neighbor_info[node1]['address'])


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
