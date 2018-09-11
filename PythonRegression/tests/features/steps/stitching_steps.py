from aloe import step
from util.test_logic import api_test_logic as tests
from util.transaction_utils import transaction_logic as transactions
from time import sleep,time

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

config = {}
responses = {}

side_tangle_address = b'SIDE9TANGLE9999999999999999999999999999999999999999999999999999999999999999999999'
stitching_addresss = b'STITCHING9TRANSACTIONS99999999999999999999999999999999999999999999999999999999999'
referencing_address = b'REFERENCES9STITCHING9TRANSACTION9999999999999999999999999999999999999999999999999'
promoting_address = b'PROMOTING9STITCH99999999999999999999999999999999999999999999999999999999999999999'


@step(r'a stitching transaction is issued on "([^"]*)" with the tag "([^"]*)"')
def issue_stitching_transaction(step,node,tag):
    config['nodeId'] = node
    config['tag'] = tag

    api = tests.prepare_api_call(node)
    logger.info('Finding Transactions for Stitching')
    side_tangle_transactions = api.find_transactions(addresses = [side_tangle_address])
    gtta_transactions = api.get_transactions_to_approve(depth=3)

    hash_index = len(side_tangle_transactions['hashes']) - 1    
    trunk = side_tangle_transactions['hashes'][hash_index]
    branch = gtta_transactions['branchTransaction']
    
    logger.debug('Trunk: ' + str(trunk))
    logger.debug('Branch: ' + str(branch))
    
    bundle = transactions.create_transaction_bundle(stitching_addresss,tag,0)
    trytes = bundle[0].as_tryte_string()

    sent_transaction = api.attach_to_tangle(trunk, branch, [trytes], 14)
    api.broadcast_and_store(sent_transaction.get('trytes'))
    
    logger.info('Stitching Transaction Sent')
    
@step(r'check_consistency is called on this transaction')
def check_stitch_consistency(step):
    logger.info('Checking consistency of stitching transaction')
    node = config['nodeId']
    tag = config['tag']
    
    api = tests.prepare_api_call(node)

    stitch_transactions = api.find_transactions(tags=[tag]) 
    hash_index = len(stitch_transactions['hashes']) - 1
    transaction = stitch_transactions['hashes'][hash_index]
    response = api.check_consistency(tails=[transaction])
    
    logger.debug('Response: {}'.format(response))
    
    responses['checkConsistency'] = response
    responses['stitchTransaction'] = transaction
    
    
@step(r'the response should return "([^"]*)"')
def check_response_return_value(step,return_val):
    logging.info('Checking Return ')
    response = str(responses['checkConsistency']['state'])
    logger.debug(response)
    assert response == return_val, "Response does not equal {}. Response: {}".format(return_val,response)
    

@step(r'a transaction is issued referencing the stitching transaction')
def reference_stitch_transaction(step):
    node = config['nodeId']
    stitch = responses['stitchTransaction']
    
    api = tests.prepare_api_call(node)
    gtta_response = api.get_transactions_to_approve(depth=3)
    branch = gtta_response['branchTransaction']
    
    bundle = transactions.create_transaction_bundle(referencing_address,'REFERENCING9STITCH', 0)    
    
    trytes = bundle[0].as_tryte_string()
    
    sent_transaction = api.attach_to_tangle(stitch, branch, [trytes], 14)
    api.broadcast_and_store(sent_transaction.get('trytes'))
    
    
@step(r'that transaction is promoted on "([^"]*)" after a delay of (\d+) seconds')
def promote_transaction(step,node,delay):
    logger.info('Promoting Transaction')
    start = time() 
    tag = config['tag']
    api = tests.prepare_api_call(node)
    
    #Determines if a findStitching key exists in the responses dict
    #If not, it creates an empty array
    if 'findStitching' not in responses:
        responses['findStitching'] = []
        logger.info('Created findStitching')
    
    stitch_transaction = api.find_transactions(tags = [tag])
    
    stop = time()
    time_spent= stop - start
    
    #Ensures the delay time is consistent for each iteration
    if time_spent < int(delay): 
        time_left = int(delay) - time_spent
        logger.info(time_left)
        sleep(time_left)
    
    hashes = stitch_transaction['hashes']
    for hash in range(len(hashes)):
        if hashes[hash] not in responses['findStitching']:
            logger.info('Promote {}'.format(hashes[hash]))
            responses['findStitching'].append(hashes[hash])
            transaction = transactions.promote_transaction(hashes[hash], promoting_address, "PROMOTING9STITCH", api)
    
    
@step(r'this process is repeated (\d+) more times')
def repeat_promotion_steps(step,number_of_repeats):
    for repeat in range(int(number_of_repeats)):
        issue_stitching_transaction(step,"nodeA", config['tag'])
        promote_transaction(step,config['nodeId'], 20)
        

@step(r'the promoted transaction responses should not return an error')
def check_promotion_responses(step):
    logger.info('Checking responses')
     
