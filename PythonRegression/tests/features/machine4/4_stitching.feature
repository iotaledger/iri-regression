Feature: Ensure node reliability while stitching a side tangle 
	A stitching tangle transaction needs to be issued to the tangle referencing
	a transaction from the main tangle, and a transaction from the side tangle
	and check consistency needs to be called to ensure the transaction does not 
	crash the node. If the node responds to the api call, it has not crashed. A
	transaction will then need to be cast referencing the stitching transaction
	should also not crash the node. 
	
	Scenario: Check consistency on a stitching transaction responds
		
		Given a stitching transaction is issued on "nodeA" with the tag "STITCHING"
		And check_consistency is called on this transaction
		Then the response should return "False"	
		
	Scenario: A transaction referencing the stitch should not crash the node
	
		Given a transaction is issued referencing the stitching transaction
		And "getNodeInfo" is called on "nodeA"
		Then a response with the following is returned: 
		|keys								|
		|appName							|	
		|appVersion							|
		|duration							|
		|jreAvailableProcessors				|
		|jreFreeMemory						|
		|jreMaxMemory						|
		|jreTotalMemory						|
		|jreVersion							|		
		|latestMilestone					|
		|latestMilestoneIndex				|
		|latestSolidSubtangleMilestone		|
		|latestSolidSubtangleMilestoneIndex |
		|milestoneStartIndex				|
		|neighbors							|
		|packetsQueueSize					|
		|time								|
		|tips								|
		|transactionsToRequest				| 
		
		
	@now 	
	Scenario: Promote stitching transactions
	
		Given a stitching transaction is issued on "nodeA" with the tag "PROMOTE9STITCH"
		When that transaction is promoted on "nodeB" after a delay of 10 seconds
		And this process is repeated 3 more times		
		Then the promoted transaction responses should not return an error
		
		
		
		
		