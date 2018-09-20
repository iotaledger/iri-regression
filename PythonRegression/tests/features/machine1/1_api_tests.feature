Feature: Test API calls on Machine 1
	Test various api calls to make sure they are responding
	correctly.

	Scenario: GetNodeInfo is called

		#All api calls will be formatted as following, any arguments should be
		#listed below the call in table format
		#Example:
		# "<Api Call name here>" is called on "<insert node name here>" with:
		#|keys      |values             |type           |
		#|<arg key> |<arg val>          |<arg type>     |
		#
		#See tests/features/steps/api_test_steps.py for further details
		#

		Given "getNodeInfo" is called on "nodeA" with:
		|keys       |values                 |type   |

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
		Given "getNeighbors" is called on "nodeA" with:
		|keys       |values                 |type   |

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

	    Given "addNeighbors" is called on "nodeA" with:
	    |keys       |values                 |type           |
        |uris       |nodeB                  |nodeAddress    |

	    Then a response with the following is returned:
	    |keys                               |
	    |addedNeighbors                     |
	    |duration                           |

	    When "removeNeighbors" is called on "nodeA" with:
        |keys       |values                 |type           |
        |uris       |nodeB                  |nodeAddress    |


	    Then a response with the following is returned:
	    |keys                               |
	    |duration                           |
	    |removedNeighbors                   |


	Scenario: GetTips is called
		Given "getTips" is called on "nodeA" with:
		|keys       |values                 |type           |

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
		Given "getTransactionsToApprove" is called on "nodeA" with:
		|keys       |values                 |type           |
        |depth      |3                      |int            |

		Then a response with the following is returned: 
		|keys								|
		|branchTransaction					|
		|duration							|
		|trunkTransaction					|


    #Values can be found in util/static_vals.py
    Scenario: GetInclusionStates is called
	    Given "getInclusionStates" is called on "nodeA" with:
        |keys           |values             |type               |
        |transactions   |TEST_HASH          |staticValue        |
        |tips           |TEST_TIP_LIST      |staticValue        |

        Then a response with the following is returned:
        |keys                               |
        |duration                           |
        |states                             |


    #Address can be found in util/static_vals.py
    Scenario: GetBalances is called
        Given "getBalances" is called on "nodeA" with:
        |keys       |values                 |type               |
        |addresses  |TEST_EMPTY_ADDRESS     |staticValue        |
        |threshold  |100                    |int                |


        Then a response with the following is returned:
        |keys                               |
        |balances                           |
        |duration                           |
        |milestoneIndex                     |
        |references                         |


    Scenario: WereAddressesSpentFrom is called
        Given "wereAddressesSpentFrom" is called on "nodeA" with:
        |keys       |values                 |type               |
        |addresses  |TEST_EMPTY_ADDRESS     |staticValue        |

    	Then a response with the following is returned:
    	|keys                               |
    	|duration                           |
    	|states                             |



    @now
    Scenario: Create, attach, store and find a transaction
        Generate a transaction, attach it to the tangle, and store it locally. Then find
        that transaction via its address.

        Given a transaction is generated and attached on "nodeA" with:
        |keys       |values                 |type           |
        |address    |TEST_STORE_ADDRESS     |staticValue    |
        |value      |0                      |int            |

        Then a response with the following is returned:
        |keys                               |
        |trytes                             |

        When "storeTransactions" is called on "nodeA" with:
        |keys       |values                 |type           |
        |trytes     |TEST_STORE_TRANSACTION |staticValue    |

        And "findTransactions" is called on "nodeA" with:
        |keys       |values                 |type           |
        |addresses  |TEST_STORE_ADDRESS     |staticList     |

        Then a response with the following is returned:
        |keys                               |
        |hashes                             |



	Scenario: Broadcast a test transacion
		Send a test transaction from one node in a machine with a unique tag, and find that transaction
		through a different node in the same machine
		
 		Given "nodeA" and "nodeB" are neighbors
		When a transaction with the tag "TEST9TAG9ONE" is sent from "nodeA"
		And findTransaction is called with the same tag on "nodeB" 
		Then the transaction should be found 

