import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def find_in_response(key,response):
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
