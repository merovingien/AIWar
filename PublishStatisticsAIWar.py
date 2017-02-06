from __future__ import print_function
import os           # listdir(), path.join()
import subprocess   # Popen()
import logging
import json         # dump(), load()
import datetime     # date.today().isoformat()


class AIwarError(Exception):
    pass

def readFile(filepath):
    data = list()
    # Read file
    if filepath and os.path.isfile(filepath):
        with open(filepath, 'r') as rf:
            data = json.load(rf)
    return data
    
def readResultFile(filepath):
    "Read jobs of Result-file of the current day. Return list and Result-file name."
    jobs_results = list()
    # Read results already saved from file
    if filepath and os.path.isfile(filepath):
        jobs_results = readFile(filepath)
        txt = 'Result file "{name}" : {jobs} job{plural}.'.format( name=os.path.basename(filepath), jobs=len(jobs_results), plural='s' if len(jobs_results) else '' )
        #logging.info( txt )
        print(txt)
    elif filepath:
        txt = 'Result file "{name}" : empty.'.format( name=os.path.basename(filepath) )
        #logging.info( txt )
        print(txt)
    return jobs_results

def readStatisticsFile(filepath):
    "Read jobs of Result-file of the current day. Return list and Result-file name."
    statistics = list()
    # Read results already saved from file
    if filepath and os.path.isfile(filepath):
        statistics = readFile(filepath)
        txt = 'Statistics file "{name}" : {jobs} data{plural}.'.format( name=os.path.basename(filepath), jobs=len(statistics), plural='s' if len(statistics) else '' )
        #logging.info( txt )
        print(txt)
    elif filepath:
        txt = 'Statistics file "{name}" : empty.'.format( name=os.path.basename(filepath) )
        #logging.info( txt )
        print(txt)
    return statistics

def writeStatisticsOverview(filepath, data):
    "Write statistics to file. Return nothing."
    # Save to file
    if filepath and data:
        with open(filepath, 'w') as f:
            json.dump(data, f)

def publish(args):
    "Create all statistics. return nothing."
    #print('publish() : ',args)
    
    # Args:
    #'list-results-files': list_results_files
    #'list-players': list_players
    #'list-maps': list_maps
    #'statistics-path': statistics_path
    
    # Publish statistics : overview
    statistics = createStatistics_overview(args)
    #publishStatistics_overview(args, statistics)
    
    # Publish statistics : maps
    #createStatistics_maps(args)
    # Publish statistics : players
    #createStatistics_players(args)

def createStatistics_overview(args):
    "Create statistics 'overview'. return nothing."
    overview = dict()
    # Read each Result-File
    for f in args['list-results-files']:
        if f:
            resultFile = readResultFile(f);
            #print('for f in args[list-results-files]: resultFile : ',resultFile[0],resultFile[-1])
            
            # Count win/lose for each player
            for name in args['list-players']:
                #print('for p in args[list-players]: name : {}'.format(name))
                playerGames = [g for g in resultFile if g['blue']['name'] == name or g['red']['name'] == name ]
                win = 0
                lose = 0
                draw = 0
                for g in playerGames:
                    if g['blue']['name'] == name and 'blue wins' in g['result']    \
                       or g['blue']['name'] == name and 'red error' in g['result'] \
                       or g['red']['name'] == name and 'red wins' in g['result']   \
                       or g['red']['name'] == name and 'blue error' in g['result']:
                        win += 1
                    elif g['blue']['name'] == name and 'red wins' in g['result']    \
                       or g['blue']['name'] == name and 'blue error' in g['result'] \
                       or g['red']['name'] == name and 'blue wins' in g['result']   \
                       or g['red']['name'] == name and 'red error' in g['result']:
                         lose += 1
                    elif 'draw' in g['result']:
                         draw += 1
                if 'Top-Players' not in overview.keys():
                    overview['Top-Players'] = dict()
                if name not in overview['Top-Players'].keys():
                    overview['Top-Players'][name] = {'win':0, 'lose':0, 'draw':0}
                overview['Top-Players'][name]['win'] += win
                overview['Top-Players'][name]['lose'] += lose
                overview['Top-Players'][name]['draw'] += draw

    # Write to file Statistics-Overview
    statFile = os.path.join( args['statistics-path'], 'statistics-Overview.json')
    writeStatisticsOverview(statFile, overview)
##    print('overview : ',overview)
##    for k, v in overview['Top-Players'].iteritems():
##        print("overview['Top-Players'] = ", k,':',v)
    return overview
    

##{
##    "blue": {"params": null, "name": "TEAM_DUMMY"},
##    "map": "map.xml",
##    "end": 1485990803.371, "start": 1485990762.356,
##    "result": "draw",
##    "red": {"params": "embtest", "name": "PYTHON_TEAM"}
##}
