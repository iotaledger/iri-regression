from aloe import step
from util.test_logic import api_test_logic

tests = api_test_logic

@step(r'a stitching transaction is issued on "([^"]*)"')
def issue_stitching_transaction(step,node):
    api = tests.prepare_api_call(node)
    
    side_tangle_transaction = api.find_transactions(addresses = ['SIDETANGLE9ROCKS99999999999999999999999999999999999999999999999999999999999999999KQFTEKOXX'])
    
    
