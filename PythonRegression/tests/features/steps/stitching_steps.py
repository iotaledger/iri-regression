from aloe import step
from util.test_logic import api_test_logic
from iota import ProposedTransaction, Address, Tag, ProposedBundle
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

tests = api_test_logic

config = {}
responses = {}

side_tangle_address = b'SIDE9TANGLE9999999999999999999999999999999999999999999999999999999999999999999999'
stitching_addresss = b'STITCHING9TRANSACTIONS99999999999999999999999999999999999999999999999999999999999'
referencing_address = b'REFERENCES9STITCHING9TRANSACTION9999999999999999999999999999999999999999999999999'

@step(r'a stitching transaction is issued on "([^"]*)" with the tag "([^"]*)"')
def issue_stitching_transaction(step,node,tag):
    config['nodeId'] = node
    config['stitchTag'] = tag

    api = tests.prepare_api_call(node)
    logger.info('Finding Transactions')
    side_tangle_transactions = api.find_transactions(addresses = [side_tangle_address])
    gtta_transactions = api.get_transactions_to_approve(depth=3)

    max = len(side_tangle_transactions['hashes']) - 1    
    trunk = side_tangle_transactions['hashes'][max]
    branch = gtta_transactions['branchTransaction']
    
    logger.debug('Trunk: ' + str(trunk))
    logger.debug('Branch: ' + str(branch))
    
    stitching_transaction = ProposedTransaction(
            address = Address(stitching_addresss),
            tag = Tag(tag),
            value = 0
        )
    bundle = ProposedBundle()
    bundle.add_transaction(stitching_transaction)
    bundle.finalize()
    
    trytes = bundle[0].as_tryte_string()

    sent_transaction = api.attach_to_tangle(trunk, branch, [trytes], 14)
    transaction = api.broadcast_and_store(sent_transaction.get('trytes'))
    
@step(r'check_consistency is called on this transaction')
def check_stitch_consistency(step):
    logger.info('Checking consistency of stitching transaction')
    node = config['nodeId']
    tag = config['stitchTag']
    
    api = tests.prepare_api_call(node)

    stitch_transactions = api.find_transactions(tags=[tag]) 
    max = len(stitch_transactions['hashes']) - 1
    transaction = stitch_transactions['hashes'][max]
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
    
    txn = ProposedTransaction(
        address = Address(referencing_address),
        tag = Tag('REFERENCING9STITCH'),
        value = 0
        )    
    
    bundle = ProposedBundle()
    bundle.add_transaction(txn)
    bundle.finalize()
    
    trytes = bundle[0].as_tryte_string()
    
    sent_transaction = api.attach_to_tangle(stitch, branch, [trytes], 14)
    api.broadcast_and_store(sent_transaction.get('trytes'))
    
