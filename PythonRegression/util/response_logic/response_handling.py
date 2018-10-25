import logging
from util.threading_logic import pool_logic as pool

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def find_in_response(key,response):
    """
    Searches through layers of the response to determine if a given key is present.
    Used for api response testing mainly.

    :param key: The key you would like to determine is present in the response
    :param response: The response you would like to find the key in
    """
    isPresent = False
    for k in response:
        if k == key:
            isPresent = True
            break

        elif isinstance(response[k], dict):
            if key in response[k]:
                isPresent = True
                break

        elif isinstance(response[k],list):
            for d in range(len(response[k])):
                logger.info(response[k][d])
                if type(response[k][d]) != bool and key in response[k][d]:
                    isPresent = True
                    break
            if isPresent == True:
                break

    assert isPresent is True, '{} does not appear to be present in the response: {}'.format(key,response)


def fetch_future_results(future_results, numTests, responseVals):
    """
    Fetches the results of a given set of future reference points and stores them in the provided list.

    :param future_results: The list containing the future_result references for response fetching.
    :param numTests: The maximum number of tests.
    :param responseVals: The list to place the response values in.
    """

    instance = 0
    for result in future_results:
        instance += 1
        if instance % 25 == 0:
            logger.info('Fetching result: {}/{}'.format(instance,numTests))
        response = pool.fetch_results(result,30)
        responseVals.append(response)
