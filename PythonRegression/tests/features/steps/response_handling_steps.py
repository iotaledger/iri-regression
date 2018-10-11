from aloe import world, step
from util.test_logic import api_test_logic as api_utils
from util.response_logic import response_handling as response_handling

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@step(r'the "([^"]*)" parallel call should return with:')
def compare_thread_return(step,apiCall):
    #Prepare response list for comparison
    response_list = world.responses[apiCall][world.config['nodeId']]
    #Exclude duration from response list
    if 'duration' in response_list:
        del response_list['duration']
    response_keys = response_list.keys()

    #Prepare expected values list for comparison
    expected_values = {}
    args = step.hashes
    api_utils.prepare_options(args,expected_values)
    keys = expected_values.keys()

    #Confirm that the lists are of equal length before comparing
    assert len(keys) == len(response_keys), \
        'Response: {} does not contain the same number of arguments: {}'.format(keys,response_keys)

    for count in range(len(keys)):
        response_key = response_keys[count]
        response_value = response_list[response_key]
        expected_value = expected_values[response_key]

        assert response_value == expected_value, \
            'Returned: {} does not match the expected value: {}'.format(response_value,expected_value)

    logger.info('Responses match')



@step(r'a response for "([^"]*)" should exist')
def response_exists(step,apiCall):
    response = world.responses[apiCall][world.config['nodeId']]
    empty_values = {}
    for key in response:
        if key != 'duration':
            isEmpty = api_utils.check_if_empty(response[key])
            if isEmpty == True:
                empty_values[key] = response[key]

    assert len(empty_values) == 0, "There was an empty value in the response {}".format(empty_values)




@step(r'the response for "([^"]*)" should return with:')
def check_response_for_value(step,apiCall):
    response_values = world.responses[apiCall][world.config['nodeId']]
    expected_values = {}
    args = step.hashes
    api_utils.prepare_options(args,expected_values)

    for expected_value_key in expected_values:
        if expected_value_key in response_values:
            expected_value = expected_values[expected_value_key]
            response_value = response_values[expected_value_key]

            if type(response_value) is list:
                response_value = response_value[0]

            assert expected_value == response_value, \
                "The expected value {} does not match the response value: {}".format(expected_value,response_value)

    logger.info('Response contained expected values')



@step(r'a response with the following is returned:')
def compare_response(step):
    logger.info('Validating response')
    keys = step.hashes
    nodeId = world.config['nodeId']
    apiCall = world.config['apiCall']

    response = world.responses[apiCall][nodeId]
    keyList = []

    for key in range(len(keys)):
        keyList.append(keys[key]['keys'])


    for key in range(len(keyList)):
        response_handling.find_in_response(keyList[key],response)

