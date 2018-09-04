Feature: Ensure consistency of stitching transactions
	A side tangle transaction needs to be issued to the tangle referencing
	a transaction from the main tangle, and a transaction from the side tangle
	and check consistency needs to be called to ensure the transaction does not 
	crash the node.
	
	Scenario: Check consistency of stitching transaction
		
		Given a stitching transaction is issued on "nodeA"
		And check_consistency is called on this transaction
		Then the results should return "true"		