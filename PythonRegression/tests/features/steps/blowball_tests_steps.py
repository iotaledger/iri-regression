from aloe import world, step 
from util.test_logic import api_test_logic

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

tests = api_test_logic

world.test_vars = {}


@step(r'the returned GTTA transactions will be compared with the milestones')
def compare_gtta_with_milestones(step):
    """Compares the getTransactionsToApprove response values with the collected milestone issuing address"""
    logger.info("Compare GTTA response with milestones")
    gtta_responses = tests.fetch_response('getTransactionsToApprove')
    find_transactions_responses = tests.fetch_response('findTransactions')
    milestones = list(find_transactions_responses['hashes'])
    node = world.config['nodeId']
    world.config['max'] = len(gtta_responses[node])
    
    transactions = []
    transactions_count = []
    milestone_transactions = []
    milestone_transactions_count = []
    world.test_vars['milestone_count'] = 0
    
    for node in gtta_responses:
        if type(gtta_responses[node]) is list:
            for response in range(len(gtta_responses[node])):
                branch_transaction = gtta_responses[node][response]['branchTransaction']
                trunk_transaction = gtta_responses[node][response]['trunkTransaction']
                
                compare_responses(branch_transaction,milestones,transactions,transactions_count,
                                  milestone_transactions,milestone_transactions_count)
                compare_responses(trunk_transaction,milestones,transactions,transactions_count,
                                  milestone_transactions,milestone_transactions_count)
    
        logger.info("Milestone count: " + str(world.test_vars['milestone_count']))
    
    f = open('blowball_log.txt','w')
    for transaction in range(len(transactions)):
        transaction_string = 'Transaction: ' + str(transactions[transaction]) + " : " + str(transactions_count[transaction])
        logger.debug(transaction_string)
        f.write(transaction_string + "\n")
        
    for milestone in range(len(milestone_transactions)):
        milestone_string = 'Milestone: ' + str(milestone_transactions[milestone]) + \
        " : " + str(milestone_transactions_count[milestone])
        logger.debug(milestone_string)
        f.write(milestone_string + "\n")
    
    f.close()
    logger.info('Transactions logged in /tests/features/machine3/blowball_logs.txt')    
    

@step(r'less than (\d+) percent of the returned transactions should reference milestones')
def less_than_max_percent(step,max_percent):
    """
    Checks the number of returned milestones and ensures that the total number of milestones returned is below a
    given threshold
    """
    percentage = (float(world.test_vars['milestone_count'])/(world.config['max'] * 2)) * 100.00
    logger.info(str(percentage) + "% milestones")
    assert percentage < float(max_percent)
    

        
def compare_responses(value,milestone_list,transaction_list,transaction_counter_list,
                      milestone_transaction_list,milestone_transaction_count):
    """
    A comparison method to check a given response value with a list of collected milestones. It checks if the value is
    present in the milestone list. If it is present in the milestone list, it then determines if this is the first time
    this transaction has been returned, and adjusts the milestone_transaction_list and milestone_transaction_count lists
    accordingly. The overall milestone count is incremented each time a value is found in the milestone list. If the
    value is not present in the milestone list, then it does the same check for the transaction_list and
    transaction_counter_list. These lists will be used later for logging the responses and the number of times a given
    response has been returned.

    :param value: The value you would like to check against the lists
    :param milestone_list: The list of found milestones you will compare the value to
    :param transaction_list: A list of recorded transaction values that have been found
    :param transaction_counter_list: A list of the number of times a value has been returned
    :param milestone_transaction_list: A list of returned milestone values that have been found
    :param milestone_transaction_count: A list of the number of times a milestone value has been returned
    """

    if value in milestone_list:
        if value in milestone_transaction_list:
            milestone_transaction_count[milestone_transaction_list.index(value)] += 1
        else:
            milestone_transaction_list.append(value)
            milestone_transaction_count.append(1)
            logger.debug('added transaction "{}" to milestone list'.format(value))
            
        world.test_vars['milestone_count'] += 1
        logger.debug('"{}" is a milestone'.format(value))    
    else: 
        if value in transaction_list:
            transaction_counter_list[transaction_list.index(value)] += 1    
        else: 
            transaction_list.append(value) 
            transaction_counter_list.append(1)
            logger.debug('added transaction "{}" to transaction list'.format(value))                                
        
    