from __future__ import print_function
import os           # listdir(), path.join()
import subprocess   # Popen()
import time         # time(), sleep()
#import subprocess, time, logging
import logging
import xml.etree.ElementTree as ET

from multiprocessing import cpu_count as get_nb_core



# Reading 'config.xml' to extract blue/red players and map name.
def readConfig( config ):
    "Read the config file to return players and map name as a tuple."
    tree = ET.parse(config)
    root = tree.getroot()
    blue = root.find("options/blue").text
    red = root.find("options/red").text
    mapName = root.find("options/map").text
    players = [p.text for p in root.findall('players/player/name')]
    logging.info(
        'Reading config file "{config}" : players(blue/red): "{blue}"/"{red}" on map "{mapName}".'.format(
        config=config, blue=blue, red=red, mapName=mapName ) )
    logging.info(
        'Reading config file "{config}" : list of players "{players}".'.format(
        config=config, players=players ) )
    return (blue, red, mapName, players)

def newJob( blue, red, mapName ):
    "Create 1 new job to add to the job list. Returns dictionnary for job without 'number'"
    # Construct args
    args = ("AIWar", "--blue", blue, "--red", red, "--map", os.path.join(mapDirectory, mapName), "--renderer", "dummy")
    return {'number': None,
            'blue': blue, 'red':red, 'mapName': mapName, 'args': args,
            'popen': None, 'state': None, 'ret': None, 'time': 0}

def newRounds( blue, red, mapName, repeat = 1 ):
    "Create N rounds to add to the job list. Returns list of dictionnary for job without 'number'"
    return [newJob( blue, red, mapName ) for r in range(repeat)]

def newMaps( blue, red, repeat = 1):
    "Create N rounds by map to add to the job list. Returns list of dictionnary for job without 'number'"
    r = []
    for m in os.listdir(mapDirectory):
        if m[-4:].lower() == '.xml':
            r += newRounds( blue, red, m, repeat )
    return r

def newColors( blue, red, repeat = 1):
    "Create N rounds by map and color to add to the job list. Returns list of dictionnary for job without 'number'"
    return newMaps( blue, red, repeat ) + newMaps( red, blue, repeat )

def newPlayers( player, repeat = 1 ):
    "Create N rounds for 1 player against the world by map and color to add to the job list. Returns list of dictionnary for job without 'number'"
    r = []
    for p in readConfig('config.xml')[3]:
        if p != player:
            r += newColors( player, p, repeat )
    return r

def newComplete( repeat = 1 ):
    "Create N rounds for all players by map and color to add to the job list. Returns list of dictionnary for job without 'number'"
    r = []
    for p in readConfig('config.xml')[3]:
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
mapDirectory = './maps'
nbRound = 0
#get_nb_core()
#logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.INFO)
#logging.basicConfig(filename='loopRounds.log', level=logging.DEBUG)

#args = ("AIWar", "--blue", bluePlayer, "--red", redPlayer, "--map", map, "--renderer", "dummy")
#args = ("AIWar", "--file", "config.xml", "--renderer", "dummy")
#args = ("AIWar", "--file", "config.xml")

result_txt = {0: "draw", 1: "blue wins", 2: "red wins",
              11: "blue error", 12: "red error", 255: "error"}
result_int = {value: key for (key, value) in result_txt.iteritems()}
logging.debug( 'result_txt={}'.format(result_txt) )
logging.debug( 'result_int={}'.format(result_int) )

bluePlayer, redPlayer, mapName, _ = readConfig('config.xml')


# Reading of arguments
#
# TROUVER MODULE DEDIE ET IMPLEMENTER
#

#############
# Build list of jobs

#jobs = newRounds('GuiGui', 'Shuriken', 'map.xml', 1 )
#jobs += newRounds('Merovingien', 'Clement', 'map_FollowTheWhiteRabbit.xml', 2 )

#jobs = newMaps( 'GuiGui', 'Shuriken' )
#jobs += newMaps('Merovingien', 'Clement', 2 )

#jobs = newColors( 'GuiGui', 'Shuriken' )
#jobs += newColors('Merovingien', 'Clement', 2 )

#jobs = newPlayers( 'GuiGui' )
#jobs += newPlayers( 'Clement', 2 )

jobs = newComplete()
jobs = newComplete(2)

# Adds 'number' in jobs
for enum, i in enumerate(jobs):
    i['number'] = enum

#logging.debug( 'jobs={}'.format(jobs) )

#import pprint; pp = pprint.PrettyPrinter(indent=4); pp.pprint(jobs)
exit()



#############
# Unstack a job to each core

while [ j for j in jobs if j['popen'] is None or j['state'] ]:
    for i in jobs:
        if i['popen'] is None:
            # Launch job
            logging.debug( 'i={}'.format(i) )
            i['popen'] = subprocess.Popen(i['args'])
            i['state'] = True
            i['time'] = time.time()
            logging.info( 'job {number} : Starting...'.format( number=i['number'] ) )
            print('job {number} : Starting "{blue}" Vs "{red}" on map "{mapName}".'.format(
                number=i['number'], blue=i['blue'], red=i['red'], mapName=i['mapName'] ))
            # Sleep to randomize each game
            time.sleep(1)
            
        if i['state']:
            logging.debug( 'i={}'.format(i) )
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
