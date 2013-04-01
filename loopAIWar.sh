#!/bin/bash

#set -x

if [ $# = "0" ];then
    echo ""
    echo "NAME : loopAIWar.sh - launch AIWar for many rounds."
    echo ""
    echo "SYNOPSIS : loopAIWar.sh [bluePlayer redPlayer mapFile] roundToPlay"
    echo "           (take configuration of 'config.xml' if all [bluePlayer redPlayer mapFile] missing)"
    echo ""
    echo "DESCRIPTION : "
    echo "   bluePlayer  : Name of the blue player"
    echo "   redPlayer   : Name of the red player"
    echo "   mapFile     : Name of the map"
    echo "   roundToPlay : Number of rounds to play"
    echo ""
else
    blueScore=0
    redScore=0
    blueError=0
    redError=0
    draw=0
    error=0
    
    nbCore=`grep -c ^processor /proc/cpuinfo`
    nbThread=0

    # Nombre de travaux a faire
    if [ $# = "1" ];then
        nbTravaux=$1
    else
        nbTravaux=$4
    fi

    # Commencer par lancer une Thread sur le coeur 1
    if [ "$nbTravaux" -gt "0" ];then
        if [ "$#" = "1" ];then
            ./AIWar --file config.xml --renderer dummy  >/dev/null 2>&1 &
        else
            ./AIWar --blue $1 --red $2 --map $3 --renderer dummy  >/dev/null 2>&1 &
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
                    ./AIWar --blue $1 --red $2 --map $3 --renderer dummy  >/dev/null 2>&1 &
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
                        let "draw += 1"
                elif [ $resultat = "1" ];then
                        let "blueScore += 1"
                elif [ $resultat = "2" ];then
                        let "redScore += 1"
                elif [ $resultat = "11" ];then
                        let "blueError += 1"
                elif [ $resultat = "12" ];then
                        let "redError += 1"
                elif [ $resultat = "255" ];then
                        let "error += 1"
                fi
                
                unset pid[$i]
                let "nbTravaux -= 1"
            fi
        done
    done

    # Afficher les logs
    if [ "$#" -lt "5" ] || [ "$5" != "nolog" ];then
        echo "Resultat final:  *** $1 Vs $2 ***"
        echo "   Map          : $3"
        echo "   Joueur bleu  : $1 = $blueScore"
        echo "   Joueur rouge : $2 = $redScore"
        echo ""
        echo "   Egalite   = $draw"
        echo "   Bug bleu  = $blueError"
        echo "   Bug rouge = $redError"
        echo "   Erreur    = $error"
        echo ""
        echo "   Ver.AIWar = \"`git show | head -n 1`\""
    fi

    #echo "blueScore=$blueScore - redScore=$redScore - draw=$draw - error/blue/red=$error/$redScore/$error"
fi
