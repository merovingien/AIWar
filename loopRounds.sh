#!/bin/bash

#set -x

if [ $# = "0" ];then
    echo ""
    echo "NAME : loopRounds.sh - launch AIWar for many rounds."
    echo ""
    echo "SYNOPSIS : loopRounds.sh [bluePlayer redPlayer mapFile] roundToPlay  [verbose]"
    echo "           (take configuration of 'config.xml' if all [bluePlayer redPlayer mapFile] missing)"
    echo ""
    echo "DESCRIPTION : "
    echo "   bluePlayer  : Name of the blue player"
    echo "   redPlayer   : Name of the red player"
    echo "   mapFile     : Name of the map"
    echo "   roundToPlay : Number of rounds to play"
    echo "   verbose     : Customize the trace on terminal."
    echo "                 This is used when loopRounds.sh is called from a parent bash script."
    echo "                 If missing, everything is written to the terminal."
    echo "                 Can be 1 value : 'nolog'."
    echo "                  - nolog    = nothing is written to the terminal"
    echo ""
else
    # Variables exportees
    templatePath_Rounds="./www/template/"
    filePath_Rounds="./www/results/"
    blueScore_Rounds=0
    redScore_Rounds=0
    blueError_Rounds=0
    redError_Rounds=0
    draw_Rounds=0
    error_Rounds=0
    descriptionVersionPlayer1_Rounds=""
    descriptionVersionPlayer2_Rounds=""
    descriptionAIWarVersion_Rounds=`git show | head -n 1`
    installerRGraph_Rounds=""
    jsonHead_Rounds=""
    jsonBody_Rounds=""
    jsonTail_Rounds=""
         
    # Variables locales
    nbCore=`grep -c ^processor /proc/cpuinfo`
    nbThread=0
    nbTravaux=0
    resultat=0
    map_nopath=""
    fileName=""
    descriptionDate="`date +%d-%m-%Y`"
    descriptionHour="`date +%Hh%M`"
    descriptionType="X rounds, 1 map, 1 color, 1 opponent."
    rounds_Rounds=0
    bluePlayer_Rounds=""
    redPlayer_Rounds=""
    map_Rounds=""

    # Nombre de travaux a faire
    if [ $# = "1" ];then
        rounds_Rounds=$1
        # Recuperer les infos de config.xml
        bluePlayer_Rounds=`grep "<blue>" config.xml | cut -f 2 -d ">" | cut -f 1 -d "<" |head -n 1`
        redPlayer_Rounds=`grep "<red>" config.xml | cut -f 2 -d ">" | cut -f 1 -d "<" |head -n 1`
        map_Rounds=`grep "<map>" config.xml | cut -f 2 -d ">" | cut -f 1 -d "<" |head -n 1`
    else
        bluePlayer_Rounds=$1
        redPlayer_Rounds=$2
        map_Rounds=$3
        rounds_Rounds=$4
    fi
    nbTravaux=$rounds_Rounds
    fileName="loopRounds_`date +%Y%m%d`_${descriptionHour}_${bluePlayer_Rounds}_Vs_${redPlayer_Rounds}"
    descriptionVersionPlayer1_Rounds=`grep -A 3 "$bluePlayer_Rounds" config.xml | grep "<params>" | cut -f 2 -d ">" | cut -f 1 -d "<"`
    descriptionVersionPlayer2_Rounds=`grep -A 3 "$redPlayer_Rounds" config.xml | grep "<params>" | cut -f 2 -d ">" | cut -f 1 -d "<"`
    
    # Commencer par lancer une Thread sur le coeur 1
    if [ "$nbTravaux" -gt "0" ];then
        if [ "$#" = "1" ];then
            ./AIWar --file config.xml --renderer dummy  >/dev/null 2>&1 &
        else
            ./AIWar --blue $bluePlayer_Rounds --red $redPlayer_Rounds --map $map_Rounds --renderer dummy  >/dev/null 2>&1 &
        fi
        pid[1]=$!
   fi
   
    # Boucler pour chaque travaux
    while [ "$nbTravaux" -gt "0" ];do

        # Nombre de taches a produire
        if [ "$nbTravaux" -ge "$nbCore" ];then
            nbThread=$nbCore
        else
            nbThread=$nbTravaux
        fi
        
        for i in `seq 1 $nbCore`; do
            if [ -n "${pid[*]}" ];then
                nbLiveThread=`ps -p "${pid[*]}" -o pid= | wc -l`
            else
                nbLiveThread=0
            fi

            # Lancer un thread sur chaque coeur libre
            if [ -z "${pid[*]}" ] || [ -n "${pid[*]}" ] && [ -z "${pid[$i]}" ] && [ "$nbTravaux" -gt "$nbLiveThread" ];then

                if [ "$#" = "1" ];then
                    ./AIWar --file config.xml --renderer dummy  >/dev/null 2>&1 &
                else
                    ./AIWar --blue $bluePlayer_Rounds --red $redPlayer_Rounds --map $map_Rounds --renderer dummy  >/dev/null 2>&1 &
                fi
                pid[i]=$!
            fi
        done

        # S'il y a autant de Thread actifs que de Thread lances, on s'endort.
        while [ "`ps -p \"${pid[*]}\" -o pid= | wc -l`" -eq "$nbThread" ];do
            sleep $nbThread
        done

        for i in `seq 1 $nbCore`; do
            # Identifier les Thread termines
            if [ "${pid[$i]}" != "" ] && [ "`ps -p \"${pid[$i]}\" -o pid=`" = "" ];then
                # Recuperer la valeur de retour, liberer le coeur et supprimer un travail
                wait ${pid[$i]}
                resultat=$?
                
                if [ $resultat = "0" ];then
                        let "draw_Rounds += 1"
                elif [ $resultat = "1" ];then
                        let "blueScore_Rounds += 1"
                elif [ $resultat = "2" ];then
                        let "redScore_Rounds += 1"
                elif [ $resultat = "11" ];then
                        let "blueError_Rounds += 1"
                elif [ $resultat = "12" ];then
                        let "redError_Rounds += 1"
                elif [ $resultat = "255" ];then
                        let "error_Rounds += 1"
                fi
                
                unset pid[$i]
                let "nbTravaux -= 1"
            fi
        done
    done

    # Afficher les logs
    if [ ! -d "$templatePath_Rounds/../lib/RGraph" ]; then
        installerRGraph_Rounds=`echo "";echo "";echo " !!! WARNING !!! Please install RGRaph (http://www.rgraph.net/). Unzip stable archive in directory \"$templatePath_Rounds../lib/\". After unzip, you have the directory \"$templatePath_Rounds../lib/RGraph\" and can see charts on HTML results files.";echo " ";echo " "`
    fi
    if [ "$#" -lt "5" ] || [ "$5" != "nolog" ];then
        echo "Resultat final:  *** $bluePlayer_Rounds Vs $redPlayer_Rounds ***"
        echo "   Map          : $map_Rounds"
        echo "   Joueur bleu  : $bluePlayer_Rounds = $blueScore_Rounds"
        echo "   Joueur rouge : $redPlayer_Rounds = $redScore_Rounds"
        echo ""
        echo "   Egalite    = $draw_Rounds"
        echo "   Bug bleu   = $blueError_Rounds"
        echo "   Bug rouge  = $redError_Rounds"
        echo "   Bug config = $error_Rounds"
        echo ""
        echo "   Ver.AIWar = $descriptionAIWarVersion_Rounds"
        echo "$installerRGraph_Rounds"
    fi

    #echo "blueScore=$blueScore - redScore=$redScore - draw=$draw - error/blue/red=$error/$redScore/$error"
    
    # Creation du repertoire "results"
    if [ ! -d "${filePath_Rounds}" ]; then
        mkdir -p ${filePath_Rounds}
    fi
    
    # Creation du fichier resultat HTML **RGraph**
    if [ "$#" -lt "5" ] || [ "$5" != "nolog" ];then
        map_nopath=`echo "$map_Rounds" | cut -f 2 -d "/"`
        
        cat "${templatePath_Rounds}template_RGraph_loopRounds.html" | sed "s/##DescriptionDate##/$descriptionDate/g" | sed "s/##DescriptionHour##/$descriptionHour/g" | sed "s/##DescriptionType##/$descriptionType/g" | sed "s/##DescriptionVersionPlayer1##/$descriptionVersionPlayer1_Rounds/g" | sed "s/##DescriptionVersionPlayer2##/$descriptionVersionPlayer2_Rounds/g" | sed "s/##Player1##/$bluePlayer_Rounds/g" | sed "s/##Player2##/$redPlayer_Rounds/g" | sed "s/##Maps##/$map_nopath/g" | sed "s/##Rounds##/$rounds_Rounds/g" | sed "s/##BlueScore##/$blueScore_Rounds/g" | sed "s/##RedScore##/$redScore_Rounds/g" | sed "s/##DrawScore##/$draw_Rounds/g" >> ${filePath_Rounds}RGraph_${fileName}.html
        
        echo "Fichier HTML RGraph = file://`pwd`/${filePath_Rounds}RGraph_${fileName}.html"
    fi
    

    # Creation du fichier resultat HTML **ChartJs**
    if [ "$#" -lt "5" ] || [ "$5" != "nolog" ];then
        map_nopath=`echo "$map_Rounds" | cut -f 2 -d "/"`
        
        cat "${templatePath_Rounds}template_ChartJs_loopRounds.html" | sed "s/##DescriptionDate##/$descriptionDate/g" | sed "s/##DescriptionHour##/$descriptionHour/g" | sed "s/##DescriptionType##/$descriptionType/g" | sed "s/##DescriptionVersionPlayer1##/$descriptionVersionPlayer1_Rounds/g" | sed "s/##DescriptionVersionPlayer2##/$descriptionVersionPlayer2_Rounds/g" | sed "s/##Player1##/$bluePlayer_Rounds/g" | sed "s/##Player2##/$redPlayer_Rounds/g" | sed "s/##Maps##/$map_nopath/g" | sed "s/##Rounds##/$rounds_Rounds/g" | sed "s/##BlueScore##/$blueScore_Rounds/g" | sed "s/##RedScore##/$redScore_Rounds/g" | sed "s/##DrawScore##/$draw_Rounds/g" >> ${filePath_Rounds}ChartJs_${fileName}.html
        
        echo "Fichier HTML ChartJs = file://`pwd`/${filePath_Rounds}ChartJs_${fileName}.html"
    fi
    

    # Creation de la structure JSON
    map_nopath=`echo "$map_Rounds" | cut -f 2 -d "/"`
    jsonHead_Rounds=`cat "${templatePath_Rounds}template_JSON_head.json" | sed "s/##DescriptionDate##/$descriptionDate/g" | sed "s/##DescriptionHour##/$descriptionHour/g" | sed "s/##DescriptionType##/$descriptionType/g" | sed "s/##DescriptionAIWarVersion##/$descriptionAIWarVersion_Rounds/g"`
    
    jsonBody_Rounds=`cat "${templatePath_Rounds}template_JSON_body.json" | sed "s/##Player1##/$bluePlayer_Rounds/g" | sed "s/##DescriptionVersionPlayer1##/$descriptionVersionPlayer1_Rounds/g" | sed "s/##Player2##/$redPlayer_Rounds/g" | sed "s/##DescriptionVersionPlayer2##/$descriptionVersionPlayer2_Rounds/g" | sed "s/##Maps##/$map_nopath/g" | sed "s/##Rounds##/$rounds_Rounds/g" | sed "s/##BlueScore##/$blueScore_Rounds/g" | sed "s/##RedScore##/$redScore_Rounds/g" | sed "s/##DrawScore##/$draw_Rounds/g" | sed "s/##BlueError##/$blueError_Rounds/g" | sed "s/##RedError##/$redError_Rounds/g" | sed "s/##ConfigError##/$error_Rounds/g"`
    
    jsonTail_Rounds=`cat "${templatePath_Rounds}template_JSON_tail.json"`


    # Creation du fichier resultat JSON
    if [ "$#" -lt "5" ] || [ "$5" != "nolog" ];then
        echo "$jsonHead_Rounds" >> ${filePath_Rounds}JSON_${fileName}.json
        echo "$jsonBody_Rounds" >> ${filePath_Rounds}JSON_${fileName}.json
        echo "$jsonTail_Rounds" >> ${filePath_Rounds}JSON_${fileName}.json
        
        echo "Fichier JSON = file://`pwd`/${filePath_Rounds}JSON_${fileName}.json"
    fi
    
fi
