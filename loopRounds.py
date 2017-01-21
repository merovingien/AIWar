from __future__ import print_function
import sys          # argv
import os           # listdir(), path.join()
import subprocess   # Popen()
import time         # time(), sleep()
import logging
import xml.etree.ElementTree as ET
import json         # dump(), load()

from multiprocessing import cpu_count as get_nb_core

class AIwarError(Exception):
    pass

# Reading 'config.xml' to extract blue/red players and map name.
# Use global var 'readConfig_static' to prevent multiple XML parsing
readConfig_static = None
def readConfig( config ):
    "Read the config file to return players and map name as a tuple."
    global readConfig_static
    tree = ET.parse(config)
    root = tree.getroot()
    if(readConfig_static == None or readConfig_static['ref'] != config):
        blue = root.find("options/blue").text
        red = root.find("options/red").text
        mapName = root.find("options/map").text
        players = tuple(p.text for p in root.findall('players/player/name'))
        playersParams = tuple(p.text for p in root.findall('players/player/params'))
        renderers = tuple(p.text for p in root.findall('renderers/renderer/name'))
        logging.info(
            'Reading config file "{config}" : players(blue/red): "{blue}"/"{red}" on map "{mapName}".'.format(
            config=config, blue=blue, red=red, mapName=mapName ) )
        logging.info(
            'Reading config file "{config}" : list of players "{players}".'.format(
            config=config, players=players ) )
        readConfig_static = dict()
        readConfig_static['ref'] = config
        readConfig_static['data'] = (blue, red, mapName, players, playersParams, renderers)
    return readConfig_static['data']

# Use global var 'readMaps_static' to prevent multiple os.listdir()
readMaps_static = None
def readMaps( mapDirectory ):
    "Read the list of map and return as a tuple."
    global readMaps_static
    if(readMaps_static == None or readMaps_static['ref'] != mapDirectory):
        readMaps_static = dict()
        readMaps_static['ref'] = mapDirectory
        readMaps_static['data'] = tuple(m for m in os.listdir(mapDirectory) if m[-4:].lower() == '.xml')
        logging.info( 'Reading list of maps' )
        for i, m in enumerate(readMaps_static['data']):
            logging.info( 
                'Map {index} : {mapName}.'.format(
                index=i, mapName=m ) )
    return readMaps_static['data']

def verifyArgs( args ):
    "Verify arguments to launch a job. Raise exception if error."
    # Verify players exist
    if not args[2] in readConfig(configFile)[3]:
        logging.critical( 'Unknown player : {}'.format(args[2]) )
        raise AIwarError('Unknown player', args[2])
    if not args[4] in readConfig(configFile)[3]:
        logging.critical( 'Unknown player : {}'.format(args[4]) )
        raise AIwarError('Unknown player', args[4])
    
    # Verify map exists
    if not os.path.basename(args[6]) in readMaps(configMapDirectory):
        logging.critical( 'Unknown map : {}'.format(os.path.basename(args[6])) )
        raise AIwarError('Unknown map', os.path.basename(args[6]))
    
    # Verify renderer exists
    if not args[8] in readConfig(configFile)[5]:
        logging.critical( 'Unknown renderer : {}'.format(i['args'][8]) )
        raise AIwarError('Unknown renderer', i['args'][8])

def newJob( blue, red, mapName ):
    "Create 1 new job to add to the job list. Returns dictionnary for job without 'number'"
    # Verify players exist
    if not blue in readConfig(configFile)[3]:
        logging.critical( 'Unknown player : {}'.format(blue) )
        raise AIwarError('Unknown player', blue)
    if not red in readConfig(configFile)[3]:
        logging.critical( 'Unknown player : {}'.format(red) )
        raise AIwarError('Unknown player', red)
    
    # Verify map exists
    if not mapName in readMaps(configMapDirectory):
        logging.critical( 'Unknown map : {}'.format(mapName) )
        raise AIwarError('Unknown map', mapName)
    
    return {'blue': blue, 'red':red, 'mapName': mapName}


def newRounds( blue, red, mapName, repeat = 1 ):
    "Create N rounds to add to the job list. Returns list of dictionnary for job without 'number'"
    return [newJob( blue, red, mapName ) for r in range(repeat)]

def newMaps( blue, red, repeat = 1):
    "Create N rounds by map to add to the job list. Returns list of dictionnary for job without 'number'"
    r = []
    for m in readMaps(configMapDirectory):
        r += newRounds( blue, red, m, repeat )
    return r

def newColors( blue, red, repeat = 1):
    "Create N rounds by map and color to add to the job list. Returns list of dictionnary for job without 'number'"
    return newMaps( blue, red, repeat ) + newMaps( red, blue, repeat )

def newPlayers( player, repeat = 1 ):
    "Create N rounds for 1 player against the world by map and color to add to the job list. Returns list of dictionnary for job without 'number'"
    r = []
    for p in readConfig(configFile)[3]:
        if p != player:
            r += newColors( player, p, repeat )
    return r

def newComplete( repeat = 1 ):
    "Create N rounds for all players by map and color to add to the job list. Returns list of dictionnary for job without 'number'"
    r = []
    for p in readConfig(configFile)[3]:
        r += newPlayers( p, repeat )
    return r

def createResultName( blue, red ):
    "Create a result_name list by customisation of 'result_txt' list with players names. return dict."
    # insert player name in result_txt to have result_name
    name = dict()
    for k, v in result_txt.iteritems():
        if 'blue' in v:
            name[k] = v.replace('blue', blue) + " against " + red
        elif 'red' in v:
            name[k] = v.replace('red', red) + " against " + blue
        else:
            name[k] = v
    logging.debug( 'result_name={}'.format(name) )
    return name


#############
# Init
configFile = 'config.xml'
configMapDirectory = './maps'
prefixFileName = os.path.splitext(os.path.basename(sys.argv[0]))[0]+'_'
nbRound = 0
#get_nb_core()
#logging.basicConfig(level=logging.DEBUG)
#logging.basicConfig(level=logging.INFO)
logging.basicConfig(filename=prefixFileName+'logs.log', level=logging.ERROR)

#msg='test'
#logging.info(msg)
#logging.warning(msg)
#logging.error(msg)
#logging.critical(msg)
#logging.exception(msg)
#logging.log(level, msg)


result_txt = {0: "draw", 1: "blue wins", 2: "red wins",
              11: "blue error", 12: "red error", 255: "error"}
result_int = {value: key for (key, value) in result_txt.iteritems()}
logging.debug( 'result_txt={}'.format(result_txt) )
logging.debug( 'result_int={}'.format(result_int) )

bluePlayer, redPlayer, mapName, _, _, _ = readConfig(configFile)


# Reading of arguments
#
# TROUVER MODULE DEDIE ET IMPLEMENTER
#

#############
# Build list of jobs

try:
    jobs = newRounds('GuiGui', 'Shuriken', 'map.xml', 1 )
    jobs += newRounds('Merovingien', 'Clement', 'map_FollowTheWhiteRabbit.xml', 2 )

    #jobs = newMaps( 'GuiGui', 'Shuriken' )
    #jobs += newMaps('Merovingien', 'Clement', 2 )

    #jobs = newColors( 'GuiGui', 'Shuriken' )
    #jobs += newColors('Merovingien', 'Clement', 2 )

    #jobs = newPlayers( 'GuiGui' )
    #jobs += newPlayers( 'Clement', 2 )

    #jobs = newComplete(1)
    #jobs += newComplete(3)
except AIwarError as e:
    txt = 'Error when create new jobs. Stopping work.' + str(e)
    logging.exception( txt )
    print( txt )
    exit()

# Save to file the job's list
with open(prefixFileName+'job-list.json', 'w') as outfile:
    json.dump(jobs, outfile)


# Add data used for manage job processing
for enum, i in enumerate(jobs):
    i['number'] = enum
    i['popen']  = None
    i['state']  = None
    i['ret']    = None
    i['time']   = 0
    i['args']   = ("AIWar",
                   "--blue", i['blue'],
                   "--red", i['red'],
                   "--map", os.path.join(configMapDirectory, i['mapName']),
                   "--renderer", "dummy")


#logging.debug( 'jobs={}'.format(jobs) )

#import pprint; pp = pprint.PrettyPrinter(indent=4); pp.pprint(jobs)
#exit()



#############
# Unstack a job to each core

while [ j for j in jobs if j['popen'] is None or j['state'] ]:
    for i in jobs:
        if i['popen'] is None:
            # Launch job
            logging.debug( 'i={}'.format(i) )
            try:
                verifyArgs(i['args'])
            except AIwarError as e:
                txt = 'job {number} : Error when launching job "{args}". Ignoring and go to next one.'.format( number=i['number'], args=" ".join( i['args'] ) )
                logging.exception( txt )
                print( txt )
                i['popen'] = 0
                i['state'] = False
                continue
            i['popen'] = subprocess.Popen(i['args'])
            i['state'] = True
            i['time'] = time.time()
            logging.info( 'job {number} : Starting...'.format( number=i['number'] ) )
            print('job {number} : Starting "{blue}" Vs "{red}" on map "{mapName}".'.format(
                number=i['number'], blue=i['blue'], red=i['red'], mapName=i['mapName'] ))
            # Sleep to randomize each game
            time.sleep(1)
            
        if i['state']:
            logging.debug( 'i={} ### i["popen"].poll()={}'.format(i, i['popen'].poll()) )
            if i['popen'].poll() is None:
                # Job not over.
                if int(time.time()-i['time']) % 10 == 0:
                    logging.debug( "i['popen'].poll()={} ; i['popen'].returncode={}".format( i['popen'].poll(), i['popen'].returncode) )
                    logging.info( 'job {number} : T={time} sec. : still fighting...'.format( number=i['number'], time=int(time.time()-i['time']) ) )
            else:
                i['state'] = False
                i['ret'] = i['popen'].returncode
                result_name = createResultName(blue=i['blue'], red=i['red'])
                logging.debug( "i['popen'].returncode={}".format( i['popen'].poll(), i['popen'].returncode) )
                logging.info( 'job {number} : T={time} sec. : {result}'.format( number=i['number'], result=result_name[ i['ret'] ], time=int(time.time()-i['time']) ) )
                print('job {number} : T={time} sec. : {result}'.format( number=i['number'], result=result_name[ i['ret'] ], time=int(time.time()-i['time']) ) )
    time.sleep(1)


#############
# Build charts



print("fin")
