Feature: Test API calls on Machine 1
	Test various api calls to make sure they are responding
	correctly 
	
	Scenario: GetNodeInfo is called
		Given "getNodeInfo" is called on "nodeA" 
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


	Scenario: GetNeighbors is called
		Given "getNeighbors" is called on "nodeA"
		Then a response with the following is returned:
		|keys								|
		|address							|
		|numberOfAllTransactions			|
		|numberOfAllTransactionRequests		|
		|numberOfNewTransactions			|
		|numberOfInvalidTransactions		|
		|numberOfSentTransactions			|
		|connectionType						|	 
		
	Scenario: Add and Remove Neighbors
	    Adds nodeB as a neighbor to nodeA, and then removes it.

	    Given "addNeighbors" is called on "nodeA"
	    Then a response with the following is returned:
	    |keys                               |
	    |addedNeighbors                     |
	    |duration                           |

	    When "removeNeighbors" is called on "nodeA"
	    Then a response with the following is returned:
	    |keys                               |
	    |duration                           |
	    |removedNeighbors                   |


	Scenario: GetTips is called
		Given "getTips" is called on "nodeA"
		Then a response with the following is returned:
		|keys 								|
		|hashes								|
		|duration							|



    #Values can be found in util/static_vals.py
   	Scenario Outline: GetTrytes is called
		Given getTrytes is called with the hash <hash>
		Then the response should be equal to <trytes>
		
		Examples:
			|hash 		| trytes 		    |
			|TEST_HASH	| TEST_TRYTES	    |



	Scenario: GetTransactionsToApprove is called
		Given "getTransactionsToApprove" is called on "nodeA"
		Then a response with the following is returned: 
		|keys								|
		|branchTransaction					|
		|duration							|
		|trunkTransaction					|


    #Values can be found in util/static_vals.py
    Scenario: GetInclusionStates is called
	    Given getInclusionStates is called with the transaction "TEST_HASH" and tips "TEST_TIP_LIST" on "nodeA"
        Then a response with the following is returned:
        |keys                               |
        |duration                           |
        |states                             |


    #Address can be found in util/static_vals.py
    Scenario: GetBalances is called
        Given "getBalances" is called on "nodeA"
        Then a response with the following is returned:
        |keys                               |
        |balances                           |
        |duration                           |
        |milestoneIndex                     |
        |references                         |


    Scenario: WereAddressesSpentFrom is called
        Given "wereAddressesSpentFrom" is called on "nodeA"
    	Then a response with the following is returned:
    	|keys                               |
    	|duration                           |
    	|states                             |



	Scenario: Broadcast a test transacion
		Send a test transaction from one node in a machine with a unique tag, and find that transaction
		through a different node in the same machine
		
 		Given "nodeA" and "nodeB" are neighbors
		When a transaction with the tag "TEST9TAG9ONE" is sent from "nodeA"
		And findTransaction is called with the same tag on "nodeB" 
		Then the transaction should be found 
		