#!/bin/bash

if [ $# = "0" ];then
    echo ""
    echo "NAME : loopMaps.sh - launch 'loopAIWar.sh' for all maps in directory './maps'."
    echo ""
    echo "SYNOPSIS : loopMaps.sh bluePlayer redPlayer roundToPlay [verbose]"
    echo ""
    echo "DESCRIPTION : "
    echo "   bluePlayer  : Name of the blue player"
    echo "   redPlayer   : Name of the red player"
    echo "   roundToPlay : Number of rounds to play on each map"
    echo "   verbose     : Customize the trace on terminal."
    echo "                 This is used when loopMaps.sh is called from a parent bash script."
    echo "                 If missing, everything is written to the terminal."
    echo "                 Can be 2 values : 'nolog' or 'noheader'."
    echo "                  - nolog    = nothing is written to the terminal"
    echo "                  - noheader = no header and no tailer written to the terminal"
    echo ""
else
    export blueScore
    export redScore
    export draw
    export error

    blueScoreTotal=0
    redScoreTotal=0

    # Afficher les logs
    if [ "$#" -lt "4" ] || [ "$4" != "noheader" ] && [ "$4" != "nolog" ];then
        echo "Resultat final par map :  *** $1 Vs $2 ***"
    fi

    indice=0
    for map in `ls maps/*.xml`;
    do
        . ./loopAIWar.sh $1 $2 $map $3 nolog
        let "blueScoreTotal += blueScore"
        let "redScoreTotal += redScore"
        #match=($blueScore $redScore $draw $error)
        #resultat[$indice]=${match[*]}

        if [ "$#" -lt "4" ] || [ "$4" != "nolog" ];then
            echo "   [Bleu]$1=$blueScore""  [Rouge]$2=$redScore""  Egalite=$draw""  Erreur=$error""  [Map]$map"
        fi

        let "indice += 1"
    done

    # Resultat total
    if [ "$#" -lt "4" ] || [ "$4" != "noheader" ] && [ "$4" != "nolog" ];then
        if [ $blueScoreTotal -eq $redScoreTotal ];then
            echo " *** EGALITE *** (par $blueScoreTotal a $redScoreTotal)"
        elif [ $blueScoreTotal -gt $redScoreTotal ];then
            echo " *** VAINQUEUR === $1 *** (par $blueScoreTotal a $redScoreTotal)"
        else
            echo " *** VAINQUEUR === $2 ***  (par $redScoreTotal a $blueScoreTotal)"
        fi
    fi
fi
