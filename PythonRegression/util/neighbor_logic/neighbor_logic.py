from util.test_logic import api_test_logic as api_utils
from aloe import world
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


'''
This method is used to determine if a node contains the neighbors specified in the steps feature list

@returns a list of two bools 

If the return contains a False response, then the neighbor associated with that bool will be added in the remaining
methods in the step.  
'''
def check_if_neighbors(api,neighbors,expectedNeighbor):
    isNeighbor = False
    for key in range(len(neighbors)):
        if expectedNeighbor == neighbors[key]['address']:
            logger.info("Already a neighbor")
            isNeighbor = True
        else:
            logger.info('Adding neighbor')

    if isNeighbor is False:
        udp_address = "udp://" + expectedNeighbor
        logger.info('Adding {} as neighbor'.format(udp_address))
        api.add_neighbors([udp_address.decode()])



