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
    statistics = createStatistics_maps(args)
    #publishStatistics_maps(args, statistics)
    
    # Publish statistics : players
    #statistics = createStatistics_players(args)
    #publishStatistics_players(args, statistics)

def TU_createStatistics_overview():
    listOfResultFile = ['H:\\Jeux\\AIWar_V0.4.0_win32\\www\\loopAIWar\\TESTS-loopAIWar_results-list.json']
    publish_data = { \
        'list-results-files': ['H:\\Jeux\\AIWar_V0.4.0_win32\\www\\loopAIWar\\TESTS-loopAIWar_results-list.json'], \
        'statistics-path': 'H:\\Jeux\\AIWar_V0.4.0_win32\\www\\loopAIWar', \
        'list-maps': ('map.xml', 'map_BackToBack.xml', 'map_FollowTheWhiteRabbit.xml', 'map_NoRulZ.xml', 'map_test.xml', 'map_ToInfinityAndBeyond.xml'), \
        'list-players': ('TEAM_DUMMY', 'PYTHON_TEAM', 'Merovingien-3', 'Merovingien-2', 'Antoine', 'Clement', 'Shuriken-0', 'GuiGui-6', 'GuiGui-1', 'GuiGui-2', 'GuiGui-3', 'GuiGui-4', 'GuiGui-5') \
        }
    result = createStatistics_overview(publish_data)
    print(result)
    return result
    
def TU_createStatistics_maps():
    listOfResultFile = ['H:\\Jeux\\AIWar_V0.4.0_win32\\www\\loopAIWar\\TESTS-loopAIWar_results-list.json']
    publish_data = { \
        'list-results-files': ['H:\\Jeux\\AIWar_V0.4.0_win32\\www\\loopAIWar\\TESTS-loopAIWar_results-list.json'], \
        'statistics-path': 'H:\\Jeux\\AIWar_V0.4.0_win32\\www\\loopAIWar', \
        'list-maps': ('map.xml', 'map_BackToBack.xml', 'map_FollowTheWhiteRabbit.xml', 'map_NoRulZ.xml', 'map_test.xml', 'map_ToInfinityAndBeyond.xml'), \
        'list-players': ('TEAM_DUMMY', 'PYTHON_TEAM', 'Merovingien-3', 'Merovingien-2', 'Antoine', 'Clement', 'Shuriken-0', 'GuiGui-6', 'GuiGui-1', 'GuiGui-2', 'GuiGui-3', 'GuiGui-4', 'GuiGui-5') \
        }
    result = createStatistics_maps(publish_data)
    print(result)
    return result
    
def createStatistics_overview(args):
    "Create statistics 'overview'. return list of statistics."
    sp = dict()
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
                if name not in sp.keys():
                    sp[name] = {'name': name, 'win':0, 'lose':0, 'draw':0}
                sp[name]['win'] += win
                sp[name]['lose'] += lose
                sp[name]['draw'] += draw

    # (rank, {name, win, lose, draw})
    overview = [(n, infos) for n, (name, infos) in enumerate(sorted(
        sp.items(),key=lambda kv: 10*kv[1]['win']+kv[1]['lose']+3*kv[1]['draw'],reverse=True), 1)]

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

def createStatistics_maps(args):
    "Create statistics 'maps'. return list of statistics."
    
    # Blue/Red ratio winner
    # {mapName, blue, red}
    brRatio = dict()
    
    # Duration of game
    # {mapName, samples:[{duration, number}]}
    duration = dict()
    
    # ranking of players
    # {mapName, players:[{playerName, rank, blue, red}]}
    ranking = dict()
    sp = dict()
    
    # Read each Result-File
    for f in args['list-results-files']:
        if f:
            resultFile = readResultFile(f);
            
            # Count win/lose for each player
            for map_ in args['list-maps']:
                if map_ not in brRatio.keys():
                    brRatio[map_] = {'mapName': map_, 'blue':0, 'red':0}
                if map_ not in duration.keys():
                    duration[map_] = {'mapName': map_, 'samples': list()}
                    # '[{duration, number}]' added later
                if map_ not in ranking.keys():
                    ranking[map_] = {'mapName': map_, 'players': list()}
                    # '[{playerName, rank, blue, red}]' added later
                
                # Blue/Red ratio winner
                brRatio[map_]['blue'] += len([g for g in resultFile if g['map'] == map_ and (g['result'] == 'blue wins' or g['result'] == 'red error') ])
                brRatio[map_]['red'] += len([g for g in resultFile if g['map'] == map_ and (g['result'] == 'red wins' or g['result'] == 'blue error') ])
                
                # Duration of game
                durationList = [int(g['end']-g['start']) for g in resultFile if g['map'] == map_]
                duration[map_]['samples'] += [{'duration': d, 'number': durationList.count(d)} for d in set(durationList)]
                
                # loop on each player
                for name in args['list-players']:
                    #print('for p in args[list-players]: name : {}'.format(name))
                    playerGames = [g for g in resultFile if g['map'] == map_ and (g['blue']['name'] == name or g['red']['name'] == name) ]
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
                    if map_ not in sp.keys():
                        sp[map_] = dict()
                    if name not in sp[map_].keys():
                        sp[map_][name] = {'map': map_, 'name': name, 'win':0, 'lose':0, 'draw':0}
                    sp[map_][name]['win'] += win
                    sp[map_][name]['lose'] += lose
                    sp[map_][name]['draw'] += draw
    
    for map_ in args['list-maps']:
        # {map:(rank, {name, win, lose, draw})}
        ranking[map_]['players'] = [(n, infos) for n, (name, infos) in enumerate(sorted(
            sp[map_].items(),key=lambda kv: 10*kv[1]['win']+kv[1]['lose']+3*kv[1]['draw'],reverse=True), 1)]

    # Write to file Statistics-Overview
    overview = {'ratio-blue-red': brRatio, 'duration': duration, 'ranking': ranking}
    statFile = os.path.join( args['statistics-path'], 'statistics-Maps.json')
    writeStatisticsOverview(statFile, overview)
    return overview



#TU_createStatistics_overview()
#TU_createStatistics_maps()