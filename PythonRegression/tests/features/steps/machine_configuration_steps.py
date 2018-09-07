from aloe import before,world, after
from yaml import load, Loader
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



config = {}

#Configuration
@before.each_feature
def configuration(feature):
    logger.info('Configuring machine nodes')
    machine = []   
         
    yamlPath = './output.yml'
    stream = open(yamlPath,'r')
    yamlFile = load(stream,Loader=Loader)
    world.seeds = yamlFile.get('seeds')
    
    nodes = {}
    keys = yamlFile.keys()  
    for key in keys:
        if key != 'seeds' and key != 'defaults':
            nodes[key] = yamlFile[key]

        machine = nodes
          
    world.machine = machine
    logger.debug('Machine: ')
    logger.debug(world.machine)
    
@after.each_feature
def deconfiguration(feature):
    logger.info('Deconstructing machine configuration')
    world.machine = []
    logger.debug('Machine: ')
    logger.debug(world.machine)    
    
