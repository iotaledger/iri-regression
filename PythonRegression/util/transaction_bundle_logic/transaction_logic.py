from iota import ProposedBundle,ProposedTransaction

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



def create_and_attach_transaction(api, arg_list):

    transaction = ProposedTransaction(**arg_list)

    bundle = ProposedBundle()
    bundle.add_transaction(transaction)
    bundle.finalize()
    trytes = str(bundle[0].as_tryte_string())

    gtta = api.get_transactions_to_approve(depth=3)
    branch = str(gtta['branchTransaction'])
    trunk = str(gtta['trunkTransaction'])

    sent = api.attach_to_tangle(trunk,branch,[trytes],9)
    return sent

def attach_store_and_broadcast(api,args_list):
    transaction = api.attach_to_tangle(**args_list)
    api.store_transactions(transaction.get('trytes'))
    api.broadcast_transactions(transaction.get('trytes'))
    logger.info('Done attaching, storing and broadcasting')
    return transaction