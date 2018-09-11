from iota import ProposedTransaction,ProposedBundle,Address,Tag
from util.test_logic import api_test_logic as tests

def create_transaction_bundle(address, tag, value):
    txn = ProposedTransaction(
        address = Address(address),
        tag = Tag(tag),
        value = value
        )
    bundle = ProposedBundle()
    bundle.add_transaction(txn)
    bundle.finalize()
    
    return bundle

def promote_transaction(transaction_hash, address, tag, api):
    nodeInfo = api.get_node_info()
    milestone_hash = nodeInfo['latestMilestone']
    
    txn = ProposedTransaction(
        address = Address(address),
        tag = Tag(tag),
        value = 0
        )
    
    bundle = ProposedBundle()
    bundle.add_transaction(txn)
    bundle.finalize()
        
    sent_transaction = api.attach_to_tangle(transaction_hash,milestone_hash,bundle.as_tryte_strings(),14)
    transaction = api.broadcast_and_store(sent_transaction.get('trytes'))
    
    return sent_transaction 
    
    