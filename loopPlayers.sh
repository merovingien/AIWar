#!/bin/bash

if [ $# = "0" ];then
    echo ""
    echo "NAME : loopPlayers.sh - launch 'loopColors.sh' for each players in the configuration file 'config.xml' without the player itself."
    echo ""
    echo "SYNOPSIS : loopPlayers.sh Player roundToPlay [verbose]"
    echo ""
    echo "DESCRIPTION : "
    echo "   Player      : Name of the player"
    echo "   roundToPlay : Number of rounds to play with each colors and each maps and against each players"
    echo "   verbose     : Customize the trace on terminal."
    echo "                 This is used when loopPlayes.sh is called from a parent bash script."
    echo "                 If missing, everything is written to the terminal."
    echo "                 Can be 2 values : 'nolog' or 'noheader'."
    echo "                  - nolog        = nothing is written to the terminal"
    echo "                  - onlyFileName = only fileName of output are written to the terminal"
    echo ""
else
    # Variables externes
    export templatePath_Rounds
    export filePath_Rounds
    export descriptionAIWarVersion_Rounds
    export installerRGraph_Rounds
    export jsonTail_Rounds

    export mapsList1_Maps
    export mapsList2_Maps
    export heightHBAR_Maps

    export descriptionVersionPlayer1_Colors
    export player1ScoreTotal_Colors
    export player2ScoreTotal_Colors
    export drawScoreTotal_Colors
    export mapsScoreList_Colors_RGraph
    export mapsScoreList_Colors_ChartJs_Player1
    export mapsScoreList_Colors_ChartJs_Player2
    export mapsScoreList_Colors_ChartJs_Draw
    export player2Score_Colors
    export player1Score_Colors
    export drawScore_Colors
    export jsonBody_Colors
    
    # Variables exportees
    descriptionVersionPlayer2_Players=""
    player1ScoreTotal_Players=0
    player2ScoreTotal_Players=0
    drawScoreTotal_Players=0
    player2List_Players=""
    player2Name_Players[0]=""
    player1ScoreSousTotal_Players[0]=0
    player2ScoreSousTotal_Players[0]=0
    drawScoreSousTotal_Players[0]=0
    player1BlueScore_Players[0]=0
    player1RedScore_Players[0]=0
    player2BlueScore_Players[0]=0
    player2RedScore_Players[0]=0
    drawScore1_Players[0]=0
    drawScore2_Players[0]=0
    mapsScoreList1_Players_RGraph[0]=0
    mapsScoreList2_Players_RGraph[0]=0
    mapsScoreList1_Players_ChartJs_Player1[0]=0
    mapsScoreList2_Players_ChartJs_Player1[0]=0
    mapsScoreList1_Players_ChartJs_Player2[0]=0
    mapsScoreList2_Players_ChartJs_Player2[0]=0
    mapsScoreList1_Players_ChartJs_Draw[0]=0
    mapsScoreList2_Players_ChartJs_Draw[0]=0
    jsonHead_Players=""
    jsonBody_Players=""
    
    # Variables locales
    player1_Players=$1
    rounds=$2
    fileName=""
    descriptionDate=""
    descriptionHour=""
    descriptionType=""
    BODY_ITERATION1_RGraph=""
    BODY_ITERATION2_RGraph=""
    BODY_ITERATION1_ChartJs=""
    BODY_ITERATION2_ChartJs=""
    
    indicePlayers=0
    for player2_Players in `grep -A 1 "<player>" config.xml | grep "<name>" | cut -f 2 -d ">" | cut -f 1 -d "<"`;
    do
        if [ "${player1_Players}" != "${player2_Players}" ];then
            if [ "$#" -lt "3" ] || [ "$3" != "nolog" ] && [ "$3" != "onlyFileName" ];then
                . ./loopColors.sh ${player1_Players} ${player2_Players} $rounds noversion
            elif [ "$#" -ge "3" ] && [ "$3" == "nolog" ];then
                . ./loopColors.sh ${player1_Players} ${player2_Players} $rounds nolog
            elif [ "$#" -ge "3" ] && [ "$3" == "onlyFileName" ];then
                echo "        `date +%d/%m/%Y` `date +%Hh%M` : playing against ${player2_Players}..."
                . ./loopColors.sh ${player1_Players} ${player2_Players} $rounds nolog
            fi
            player2Name_Players[$indicePlayers]=${player2_Players}
            player1ScoreSousTotal_Players[$indicePlayers]=$player1ScoreTotal_Colors
            player2ScoreSousTotal_Players[$indicePlayers]=$player2ScoreTotal_Colors
            drawScoreSousTotal_Players[$indicePlayers]=$drawScoreTotal_Colors
            player1BlueScore_Players[$indicePlayers]=${player1Score_Colors[0]}
            player1RedScore_Players[$indicePlayers]=${player1Score_Colors[1]}
            player2BlueScore_Players[$indicePlayers]=${player2Score_Colors[1]}
            player2RedScore_Players[$indicePlayers]=${player2Score_Colors[0]}
            drawScore1_Players[$indicePlayers]=${drawScore_Colors[0]}
            drawScore2_Players[$indicePlayers]=${drawScore_Colors[1]}
            mapsScoreList1_Players_RGraph[$indicePlayers]=${mapsScoreList_Colors_RGraph[0]}
            mapsScoreList2_Players_RGraph[$indicePlayers]=${mapsScoreList_Colors_RGraph[1]}
            mapsScoreList1_Players_ChartJs_Player1[$indicePlayers]=${mapsScoreList_Colors_ChartJs_Player1[0]}
            mapsScoreList2_Players_ChartJs_Player1[$indicePlayers]=${mapsScoreList_Colors_ChartJs_Player1[1]}
            mapsScoreList1_Players_ChartJs_Player2[$indicePlayers]=${mapsScoreList_Colors_ChartJs_Player2[0]}
            mapsScoreList2_Players_ChartJs_Player2[$indicePlayers]=${mapsScoreList_Colors_ChartJs_Player2[1]}
            mapsScoreList1_Players_ChartJs_Draw[$indicePlayers]=${mapsScoreList_Colors_ChartJs_Draw[0]}
            mapsScoreList2_Players_ChartJs_Draw[$indicePlayers]=${mapsScoreList_Colors_ChartJs_Draw[1]}
            let "player1ScoreTotal_Players += player1ScoreTotal_Colors"
            let "player2ScoreTotal_Players += player2ScoreTotal_Colors"
            let "drawScoreTotal_Players += drawScoreTotal_Colors"

            # Enregistrer le resultat JSON
            if [ -n "$jsonBody_Players" ];then
                jsonBody_Players=`echo "${jsonBody_Players},"; echo "${jsonBody_Colors}"`
            else
                jsonBody_Players=`echo "${jsonBody_Colors}"`
            fi

            let "indicePlayers += 1"
        fi
    done
    if [ "$#" -lt "3" ] || [ "$3" != "nolog" ] && [ "$3" != "onlyFileName" ];then
        echo ""
        echo "   Ver.AIWar = $descriptionAIWarVersion_Rounds"
        echo "$installerRGraph_Rounds"
        echo ""
    elif [ "$#" -ge "3" ] && [ "$3" == "nolog" ];then
        echo ""
    elif [ "$#" -ge "3" ] && [ "$3" == "onlyFileName" ] && [ -n "$installerRGraph_Rounds" ];then
        echo ""
        echo "$installerRGraph_Rounds"
        echo ""
    fi
    
    
    # Creation du fichier resultat HTML **RGraph** / **ChartJs**
    # length array = ${#ArrayName[@]}
    descriptionDate="`date +%d-%m-%Y`"
    descriptionHour="`date +%Hh%M`"
    descriptionType="X rounds, all maps, all colors, all opponents."
    fileName="loopPlayers_`date +%Y%m%d`_${descriptionHour}_${player1_Players}_Vs_TheWorld"
    
    indicePlayers=0
    # Creation des elements iteres
    for player2_Players in `grep -A 1 "<player>" config.xml | grep "<name>" | cut -f 2 -d ">" | cut -f 1 -d "<"`;
    do
        if [ "$player1_Players" != "$player2_Players" ];then
            descriptionVersionPlayer2_Players=`grep -A 3 "$player2_Players" config.xml | grep "<params>" | cut -f 2 -d ">" | cut -f 1 -d "<"`
            # player2List_Players
            if [ -n "$player2List_Players" ];then
                player2List_Players=`echo "${player2List_Players}, ${player2_Players}($descriptionVersionPlayer2_Players)"`
            else
                player2List_Players=`echo "${player2_Players}($descriptionVersionPlayer2_Players)"`
            fi
            
            
            # BODY ITERATION 1 **RGraph**
            BODY_ITERATION_tmp=`cat "${templatePath_Rounds}template_RGraph_loopPlayers_BODY_ITERATION1.html" | sed "s/##Player1##/$player1_Players/g" | sed "s/##Player2##/${player2Name_Players[$indicePlayers]}/g" | sed "s/##heightHBAR##/$heightHBAR_Maps/g"`
            BODY_ITERATION1_RGraph=`echo "${BODY_ITERATION1_RGraph}${BODY_ITERATION_tmp}"`
            
            # BODY ITERATION 2 **RGraph**
            BODY_ITERATION_tmp=`cat "${templatePath_Rounds}template_RGraph_loopPlayers_BODY_ITERATION2.html" | sed "s/##Player1##/$player1_Players/g" | sed "s/##Player2##/${player2Name_Players[$indicePlayers]}/g" | sed "s/##Player1ScoreTotal##/${player1ScoreSousTotal_Players[$indicePlayers]}/g" | sed "s/##Player2ScoreTotal##/${player2ScoreSousTotal_Players[$indicePlayers]}/g" | sed "s/##DrawScoreTotal##/${drawScoreSousTotal_Players[$indicePlayers]}/g" | sed "s/##Player1BlueScore##/${player1BlueScore_Players[$indicePlayers]}/g" | sed "s/##Player1RedScore##/${player1RedScore_Players[$indicePlayers]}/g" | sed "s/##Player2BlueScore##/${player2BlueScore_Players[$indicePlayers]}/g" | sed "s/##Player2RedScore##/${player2RedScore_Players[$indicePlayers]}/g" | sed "s/##DrawScore1##/${drawScore1_Players[$indicePlayers]}/g" | sed "s/##DrawScore2##/${drawScore2_Players[$indicePlayers]}/g" | sed "s/##MapsScoreList1##/${mapsScoreList1_Players_RGraph[$indicePlayers]}/g" | sed "s/##MapsScoreList2##/${mapsScoreList2_Players_RGraph[$indicePlayers]}/g"`
            BODY_ITERATION2_RGraph=`echo "${BODY_ITERATION2_RGraph}${BODY_ITERATION_tmp}"`
            
            
            # BODY ITERATION 1 **ChartJs**
            BODY_ITERATION_tmp=`cat "${templatePath_Rounds}template_ChartJs_loopPlayers_BODY_ITERATION1.html" | sed "s/##Player1##/$player1_Players/g" | sed "s/##Player2##/${player2Name_Players[$indicePlayers]}/g" | sed "s/##heightHBAR##/$heightHBAR_Maps/g" | sed "s/##Player1ScoreTotal##/${player1ScoreSousTotal_Players[$indicePlayers]}/g" | sed "s/##Player2ScoreTotal##/${player2ScoreSousTotal_Players[$indicePlayers]}/g" | sed "s/##Player1BlueScore##/${player1BlueScore_Players[$indicePlayers]}/g" | sed "s/##Player1RedScore##/${player1RedScore_Players[$indicePlayers]}/g" | sed "s/##Player2BlueScore##/${player2BlueScore_Players[$indicePlayers]}/g" | sed "s/##Player2RedScore##/${player2RedScore_Players[$indicePlayers]}/g"`
            BODY_ITERATION1_ChartJs=`echo "${BODY_ITERATION1_ChartJs}${BODY_ITERATION_tmp}"`
            
            # BODY ITERATION 2 **ChartJs**
            BODY_ITERATION_tmp=`cat "${templatePath_Rounds}template_ChartJs_loopPlayers_BODY_ITERATION2.html" | sed "s/##Player1##/$player1_Players/g" | sed "s/##Player2##/${player2Name_Players[$indicePlayers]}/g" | sed "s/##Player1ScoreTotal##/${player1ScoreSousTotal_Players[$indicePlayers]}/g" | sed "s/##Player2ScoreTotal##/${player2ScoreSousTotal_Players[$indicePlayers]}/g" | sed "s/##DrawScoreTotal##/${drawScoreSousTotal_Players[$indicePlayers]}/g" | sed "s/##Player1BlueScore##/${player1BlueScore_Players[$indicePlayers]}/g" | sed "s/##Player1RedScore##/${player1RedScore_Players[$indicePlayers]}/g" | sed "s/##Player2BlueScore##/${player2BlueScore_Players[$indicePlayers]}/g" | sed "s/##Player2RedScore##/${player2RedScore_Players[$indicePlayers]}/g" | sed "s/##DrawScore1##/${drawScore1_Players[$indicePlayers]}/g" | sed "s/##DrawScore2##/${drawScore2_Players[$indicePlayers]}/g" | sed "s/##MapsScoreList1_Player1##/${mapsScoreList1_Players_ChartJs_Player1[$indicePlayers]}/g" | sed "s/##MapsScoreList1_Player2##/${mapsScoreList1_Players_ChartJs_Player2[$indicePlayers]}/g" | sed "s/##MapsScoreList1_Draw##/${mapsScoreList1_Players_ChartJs_Draw[$indicePlayers]}/g" | sed "s/##MapsScoreList2_Player1##/${mapsScoreList2_Players_ChartJs_Player1[$indicePlayers]}/g" | sed "s/##MapsScoreList2_Player2##/${mapsScoreList2_Players_ChartJs_Player2[$indicePlayers]}/g" | sed "s/##MapsScoreList2_Draw##/${mapsScoreList2_Players_ChartJs_Draw[$indicePlayers]}/g" | sed "s/##MapsList2##/$mapsList2_Maps/g" `
            BODY_ITERATION2_ChartJs=`echo "${BODY_ITERATION2_ChartJs}${BODY_ITERATION_tmp}"`
            
            let "indicePlayers += 1"
        fi
    done
    
    # Affichage des iteration
    #echo " *** BODY_ITERATION1_RGraph = ${BODY_ITERATION1_RGraph}"
    #echo
    #echo " *** BODY_ITERATION2_RGraph = ${BODY_ITERATION2_RGraph}"
    
    # creation de la page complete avec insertion des elements iteres **RGraph**
    cat "${templatePath_Rounds}template_RGraph_loopPlayers_head.html" | sed "s/##DescriptionDate##/$descriptionDate/g" | sed "s/##DescriptionHour##/$descriptionHour/g" | sed "s/##DescriptionType##/$descriptionType/g" | sed "s/##DescriptionVersionPlayer1##/$descriptionVersionPlayer1_Colors/g" | sed "s/##PlayersList##/$player2List_Players/g"  | sed "s/##Player1##/$player1_Players/g" | sed "s/##Rounds##/$rounds/g" | sed "s/##Player1ScoreTotal##/$player1ScoreTotal_Players/g" | sed "s/##Player2ScoreTotal##/$player2ScoreTotal_Players/g" | sed "s/##DrawScoreTotal##/$drawScoreTotal_Players/g" | sed "s/##MapsList1##/$mapsList1_Maps/g" | sed "s/##MapsList2##/$mapsList2_Maps/g" >> ${filePath_Rounds}RGraph_${fileName}.html
    
    echo "${BODY_ITERATION1_RGraph}" >> ${filePath_Rounds}RGraph_${fileName}.html
    
    cat "${templatePath_Rounds}template_RGraph_loopPlayers_body1.html" | sed "s/##Player1##/$player1_Players/g" | sed "s/##Player1ScoreTotal##/$player1ScoreTotal_Players/g" | sed "s/##Player2ScoreTotal##/$player2ScoreTotal_Players/g" | sed "s/##DrawScoreTotal##/$drawScoreTotal_Players/g" | sed "s/##MapsList2##/$mapsList2_Maps/g" >> ${filePath_Rounds}RGraph_${fileName}.html

    echo "${BODY_ITERATION2_RGraph}" >> ${filePath_Rounds}RGraph_${fileName}.html

    cat "${templatePath_Rounds}template_RGraph_loopPlayers_tail.html" >> ${filePath_Rounds}RGraph_${fileName}.html
    
    if [ "$#" -lt "3" ] || [ "$3" != "nolog" ] && [ "$3" != "onlyFileName" ];then
        echo "Fichier HTML RGraph = file://`pwd`/${filePath_Rounds}RGraph_${fileName}.html"
    elif [ "$#" -ge "3" ] && [ "$3" == "nolog" ];then
        echo ""
    elif [ "$#" -ge "3" ] && [ "$3" == "onlyFileName" ];then
        echo "Fichier HTML RGraph = file://`pwd`/${filePath_Rounds}RGraph_${fileName}.html"
    fi



    # creation de la page complete avec insertion des elements iteres **ChartJs**
    cat "${templatePath_Rounds}template_ChartJs_loopPlayers_head.html" | sed "s/##DescriptionDate##/$descriptionDate/g" | sed "s/##DescriptionHour##/$descriptionHour/g" | sed "s/##DescriptionType##/$descriptionType/g" | sed "s/##DescriptionVersionPlayer1##/$descriptionVersionPlayer1_Colors/g" | sed "s/##PlayersList##/$player2List_Players/g"  | sed "s/##Player1##/$player1_Players/g" | sed "s/##Rounds##/$rounds/g" | sed "s/##Player1ScoreTotal##/$player1ScoreTotal_Players/g" | sed "s/##Player2ScoreTotal##/$player2ScoreTotal_Players/g" | sed "s/##DrawScoreTotal##/$drawScoreTotal_Players/g" | sed "s/##MapsList1##/$mapsList1_Maps/g" | sed "s/##MapsList2##/$mapsList2_Maps/g" >> ${filePath_Rounds}ChartJs_${fileName}.html
    
    echo "${BODY_ITERATION1_ChartJs}" >> ${filePath_Rounds}ChartJs_${fileName}.html
    
    cat "${templatePath_Rounds}template_ChartJs_loopPlayers_body1.html" | sed "s/##Player1##/$player1_Players/g" | sed "s/##Player1ScoreTotal##/$player1ScoreTotal_Players/g" | sed "s/##Player2ScoreTotal##/$player2ScoreTotal_Players/g" | sed "s/##DrawScoreTotal##/$drawScoreTotal_Players/g" | sed "s/##MapsList2##/$mapsList2_Maps/g" >> ${filePath_Rounds}ChartJs_${fileName}.html

    echo "${BODY_ITERATION2_ChartJs}" >> ${filePath_Rounds}ChartJs_${fileName}.html

    cat "${templatePath_Rounds}template_ChartJs_loopPlayers_tail.html" >> ${filePath_Rounds}ChartJs_${fileName}.html
    
    if [ "$#" -lt "3" ] || [ "$3" != "nolog" ] && [ "$3" != "onlyFileName" ];then
        echo "Fichier HTML ChartJs = file://`pwd`/${filePath_Rounds}ChartJs_${fileName}.html"
    elif [ "$#" -ge "3" ] && [ "$3" == "nolog" ];then
        echo ""
    elif [ "$#" -ge "3" ] && [ "$3" == "onlyFileName" ];then
        echo "Fichier HTML ChartJs = file://`pwd`/${filePath_Rounds}ChartJs_${fileName}.html"
    fi



    # Creation de la structure JSON
    jsonHead_Players=`cat "${templatePath_Rounds}template_JSON_head.json" | sed "s/##DescriptionDate##/$descriptionDate/g" | sed "s/##DescriptionHour##/$descriptionHour/g" | sed "s/##DescriptionType##/$descriptionType/g" | sed "s/##DescriptionAIWarVersion##/$descriptionAIWarVersion_Rounds/g"`


    # Creation du fichier resultat JSON
    echo "$jsonHead_Players" >> ${filePath_Rounds}JSON_${fileName}.json
    echo "$jsonBody_Players"  >> ${filePath_Rounds}JSON_${fileName}.json
    echo "$jsonTail_Rounds" >> ${filePath_Rounds}JSON_${fileName}.json
    
    if [ "$#" -lt "3" ] || [ "$3" != "nolog" ] && [ "$3" != "onlyFileName" ];then
        echo "Fichier JSON = file://`pwd`/${filePath_Rounds}JSON_${fileName}.json"
    elif [ "$#" -ge "3" ] && [ "$3" == "nolog" ];then
        echo ""
    elif [ "$#" -ge "3" ] && [ "$3" == "onlyFileName" ];then
        echo "Fichier JSON = file://`pwd`/${filePath_Rounds}JSON_${fileName}.json"
    fi

fi
