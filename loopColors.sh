#!/bin/bash

if [ $# = "0" ];then
    echo ""
    echo "NAME : loopColors.sh - launch 'loopMaps.sh' twice and switch colors of players."
    echo ""
    echo "SYNOPSIS : loopColors.sh Player1 Player2 roundToPlay [verbose]"
    echo ""
    echo "DESCRIPTION : "
    echo "   Player1     : Name of the player 1"
    echo "   Player2     : Name of the player 2"
    echo "   roundToPlay : Number of rounds to play with each colors and each maps"
    echo "   verbose     : Customize the trace on terminal."
    echo "                 This is used when loopColors.sh is called from a parent bash script."
    echo "                 If missing, everything is written to the terminal."
    echo "                 Can be 2 values : 'nolog' or 'noheader'."
    echo "                  - nolog     = nothing is written to the terminal"
    echo "                  - noheader  = no header and no tailer are written to the terminal"
    echo "                  - noversion = no version is written to the terminal"
    echo ""
else
    # Variables externes
    export templatePath_Rounds
    export filePath_Rounds
    export descriptionVersionPlayer1_Rounds
    export descriptionVersionPlayer2_Rounds
    export descriptionAIWarVersion_Rounds
    export installerRGraph_Rounds
    export jsonTail_Rounds

    export blueScoreTotal_Maps
    export redScoreTotal_Maps
    export drawScoreTotal_Maps
    export mapsList1_Maps
    export mapsList2_Maps
    export mapsScoreList_Maps_RGraph
    export mapsScoreList_Maps_ChartJs_Player1
    export mapsScoreList_Maps_ChartJs_Player2
    export mapsScoreList_Maps_ChartJs_Draw
    export heightHBAR_Maps
    export jsonBody_Maps


    # Variables exportees
    descriptionVersionPlayer1_Colors=""
    descriptionVersionPlayer2_Colors=""
    player1ScoreTotal_Colors=0
    player2ScoreTotal_Colors=0
    drawScoreTotal_Colors=0
    mapsScoreList_Colors_RGraph[0]=0
    mapsScoreList_Colors_ChartJs_Player1[0]=0
    mapsScoreList_Colors_ChartJs_Player2[0]=0
    mapsScoreList_Colors_ChartJs_Draw[0]=0
    player2Score_Colors[0]=0
    player1Score_Colors[0]=0
    drawScore_Colors[0]=0
    jsonHead_Colors=""
    jsonBody_Colors=""

    # Variables locales
    player1_Colors=$1
    player2_Colors=$2
    rounds=$3
    fileName=""
    descriptionDate=""
    descriptionHour=""
    descriptionType=""
    
    
    if [ "$#" -lt "4" ] || [ "$4" != "noheader" ] && [ "$4" != "nolog" ];then
        echo "Resultat final par map (bi-couleur) :  *** $player1_Colors Vs $player2_Colors ***"
    fi
    
    if [ "$#" -lt "4" ] || [ "$4" != "noheader" ] && [ "$4" != "nolog" ];then
        . ./loopMaps.sh ${player1_Colors} ${player2_Colors} $rounds noheader
    elif [ "$#" -ge "4" ] || [ "$4" == "nolog" ];then
        . ./loopMaps.sh ${player1_Colors} ${player2_Colors} $rounds nolog
    elif [ "$#" -ge "4" ] || [ "$4" == "noheader" ];then
        . ./loopMaps.sh ${player1_Colors} ${player2_Colors} $rounds noheader
    fi
    descriptionVersionPlayer1_Colors=$descriptionVersionPlayer1_Rounds
    descriptionVersionPlayer2_Colors=$descriptionVersionPlayer2_Rounds
    mapsScoreList_Colors_RGraph[0]=$mapsScoreList_Maps_RGraph
    mapsScoreList_Colors_ChartJs_Player1[0]=$mapsScoreList_Maps_ChartJs_Player1
    mapsScoreList_Colors_ChartJs_Player2[0]=$mapsScoreList_Maps_ChartJs_Player2
    mapsScoreList_Colors_ChartJs_Draw[0]=$mapsScoreList_Maps_ChartJs_Draw
    player1Score_Colors[0]=$blueScoreTotal_Maps
    player2Score_Colors[0]=$redScoreTotal_Maps
    drawScore_Colors[0]=$drawScoreTotal_Maps
    let "player1ScoreTotal_Colors += blueScoreTotal_Maps"
    let "player2ScoreTotal_Colors += redScoreTotal_Maps"
    let "drawScoreTotal_Colors += drawScoreTotal_Maps"
    # Enregistrer le resultat JSON
    if [ -n "$jsonBody_Colors" ];then
        jsonBody_Colors=`echo "${jsonBody_Colors},"; echo "${jsonBody_Maps}"`
    else
        jsonBody_Colors=`echo "${jsonBody_Maps}"`
    fi

    
    if [ "$#" -lt "4" ] || [ "$4" != "noheader" ] && [ "$4" != "nolog" ];then
        echo
    fi
    
    if [ "$#" -lt "4" ] || [ "$4" != "noheader" ] && [ "$4" != "nolog" ];then
        . ./loopMaps.sh ${player2_Colors} ${player1_Colors} $rounds noheader
    elif [ "$#" -ge "4" ] || [ "$4" == "nolog" ];then
        . ./loopMaps.sh ${player2_Colors} ${player1_Colors} $rounds nolog
    elif [ "$#" -ge "4" ] || [ "$4" == "noheader" ];then
        . ./loopMaps.sh ${player2_Colors} ${player1_Colors} $rounds noheader
    fi
    mapsScoreList_Colors_RGraph[1]=$mapsScoreList_Maps_RGraph
    mapsScoreList_Colors_ChartJs_Player1[1]=$mapsScoreList_Maps_ChartJs_Player1
    mapsScoreList_Colors_ChartJs_Player2[1]=$mapsScoreList_Maps_ChartJs_Player2
    mapsScoreList_Colors_ChartJs_Draw[1]=$mapsScoreList_Maps_ChartJs_Draw
    player2Score_Colors[1]=$blueScoreTotal_Maps
    player1Score_Colors[1]=$redScoreTotal_Maps
    drawScore_Colors[1]=$drawScoreTotal_Maps
    
    let "player2ScoreTotal_Colors += blueScoreTotal_Maps"
    let "player1ScoreTotal_Colors += redScoreTotal_Maps"
    let "drawScoreTotal_Colors += drawScoreTotal_Maps"
    # Enregistrer le resultat JSON
    if [ -n "$jsonBody_Colors" ];then
        jsonBody_Colors=`echo "${jsonBody_Colors},"; echo "${jsonBody_Maps}"`
    else
        jsonBody_Colors=`echo "${jsonBody_Maps}"`
    fi

    # Resultat total
    if [ "$#" -lt "4" ] || [ "$4" != "noheader" ] && [ "$4" != "nolog" ];then
        if [ $player1ScoreTotal_Colors -eq $player2ScoreTotal_Colors ];then
            echo " *** EGALITE *** (par $player1ScoreTotal_Colors a $player2ScoreTotal_Colors)"
        elif [ $player1ScoreTotal_Colors -gt $player2ScoreTotal_Colors ];then
            echo " *** VAINQUEUR === ${player1_Colors} *** (par $player1ScoreTotal_Colors a $player2ScoreTotal_Colors)"
        else
            echo " *** VAINQUEUR === ${player2_Colors} ***  (par $player2ScoreTotal_Colors a $player1ScoreTotal_Colors)"
        fi
    fi
    
    if [ "$#" -lt "4" ] || [ "$4" != "noheader" ] &&  [ "$4" != "noversion" ] && [ "$4" != "nolog" ];then
        echo ""
        echo "   Ver.AIWar = $descriptionAIWarVersion_Rounds"
        echo "$installerRGraph_Rounds"
        echo ""
    fi

    # Initialisation de la description pour les fichier resultat HTML
    descriptionDate="`date +%d-%m-%Y`"
    descriptionHour="`date +%Hh%M`"
    descriptionType="X rounds, all maps, all colors, 1 opponent."
    fileName="loopColors_`date +%Y%m%d`_${descriptionHour}_${player1_Colors}_Vs_${player2_Colors}"
    
    # Creation du fichier resultat HTML **RGraph**
    if [ "$#" -lt "4" ] || [ "$4" != "noheader" ] &&  [ "$4" != "noversion" ] && [ "$4" != "nolog" ];then
        cat "${templatePath_Rounds}template_RGraph_loopColors.html" | sed "s/##DescriptionDate##/$descriptionDate/g" | sed "s/##DescriptionHour##/$descriptionHour/g" | sed "s/##DescriptionType##/$descriptionType/g" | sed "s/##DescriptionVersionPlayer1##/$descriptionVersionPlayer1_Colors/g" | sed "s/##DescriptionVersionPlayer2##/$descriptionVersionPlayer2_Colors/g" | sed "s/##Player1##/${player1_Colors}/g" | sed "s/##Player2##/${player2_Colors}/g" | sed "s/##Rounds##/$rounds/g" | sed "s/##Player1ScoreTotal##/$player1ScoreTotal_Colors/g" | sed "s/##Player2ScoreTotal##/$player2ScoreTotal_Colors/g" | sed "s/##DrawScoreTotal##/$drawScoreTotal_Colors/g" | sed "s/##MapsList1##/$mapsList1_Maps/g" | sed "s/##MapsList2##/$mapsList2_Maps/g" | sed "s/##heightHBAR##/$heightHBAR_Maps/g" | sed "s/##Player1BlueScore##/${player1Score_Colors[0]}/g" | sed "s/##Player1RedScore##/${player1Score_Colors[1]}/g" | sed "s/##Player2BlueScore##/${player2Score_Colors[1]}/g" | sed "s/##Player2RedScore##/${player2Score_Colors[0]}/g" | sed "s/##DrawScore1##/${drawScore_Colors[0]}/g" | sed "s/##DrawScore2##/${drawScore_Colors[1]}/g" | sed "s/##MapsScoreList1##/${mapsScoreList_Colors_RGraph[0]}/g" | sed "s/##MapsScoreList2##/${mapsScoreList_Colors_RGraph[1]}/g" >> ${filePath_Rounds}RGraph_${fileName}.html
        
        echo "Fichier HTML RGraph = file://`pwd`/${filePath_Rounds}RGraph_${fileName}.html"
    fi



    # Creation du fichier resultat HTML **ChartJs**
    if [ "$#" -lt "4" ] || [ "$4" != "noheader" ] &&  [ "$4" != "noversion" ] && [ "$4" != "nolog" ];then
        cat "${templatePath_Rounds}template_ChartJs_loopColors.html" | sed "s/##DescriptionDate##/$descriptionDate/g" | sed "s/##DescriptionHour##/$descriptionHour/g" | sed "s/##DescriptionType##/$descriptionType/g" | sed "s/##DescriptionVersionPlayer1##/$descriptionVersionPlayer1_Colors/g" | sed "s/##DescriptionVersionPlayer2##/$descriptionVersionPlayer2_Colors/g" | sed "s/##Player1##/${player1_Colors}/g" | sed "s/##Player2##/${player2_Colors}/g" | sed "s/##Rounds##/$rounds/g" | sed "s/##Player1ScoreTotal##/$player1ScoreTotal_Colors/g" | sed "s/##Player2ScoreTotal##/$player2ScoreTotal_Colors/g" | sed "s/##DrawScoreTotal##/$drawScoreTotal_Colors/g" | sed "s/##MapsList1##/$mapsList1_Maps/g" | sed "s/##MapsList2##/$mapsList2_Maps/g" | sed "s/##heightHBAR##/$heightHBAR_Maps/g" | sed "s/##Player1BlueScore##/${player1Score_Colors[0]}/g" | sed "s/##Player1RedScore##/${player1Score_Colors[1]}/g" | sed "s/##Player2BlueScore##/${player2Score_Colors[1]}/g" | sed "s/##Player2RedScore##/${player2Score_Colors[0]}/g" | sed "s/##DrawScore1##/${drawScore_Colors[0]}/g" | sed "s/##DrawScore2##/${drawScore_Colors[1]}/g" | sed "s/##MapsScoreList1_Player1##/${mapsScoreList_Colors_ChartJs_Player1[0]}/g" | sed "s/##MapsScoreList2_Player1##/${mapsScoreList_Colors_ChartJs_Player1[1]}/g" | sed "s/##MapsScoreList1_Player2##/${mapsScoreList_Colors_ChartJs_Player2[0]}/g" | sed "s/##MapsScoreList2_Player2##/${mapsScoreList_Colors_ChartJs_Player2[1]}/g" | sed "s/##MapsScoreList1_Draw##/${mapsScoreList_Colors_ChartJs_Draw[0]}/g" | sed "s/##MapsScoreList2_Draw##/${mapsScoreList_Colors_ChartJs_Draw[1]}/g" >> ${filePath_Rounds}ChartJs_${fileName}.html
        
        echo "Fichier HTML ChartJs = file://`pwd`/${filePath_Rounds}ChartJs_${fileName}.html"
    fi



    # Creation de la structure JSON
    jsonHead_Colors=`cat "${templatePath_Rounds}template_JSON_head.json" | sed "s/##DescriptionDate##/$descriptionDate/g" | sed "s/##DescriptionHour##/$descriptionHour/g" | sed "s/##DescriptionType##/$descriptionType/g" | sed "s/##DescriptionAIWarVersion##/$descriptionAIWarVersion_Rounds/g"`


    # Creation du fichier resultat JSON
    if [ "$#" -lt "4" ] || [ "$4" != "noheader" ] &&  [ "$4" != "noversion" ] && [ "$4" != "nolog" ];then
        echo "$jsonHead_Colors" >> ${filePath_Rounds}JSON_${fileName}.json
        echo "$jsonBody_Colors"  >> ${filePath_Rounds}JSON_${fileName}.json
        echo "$jsonTail_Rounds" >> ${filePath_Rounds}JSON_${fileName}.json
        
        echo "Fichier JSON = file://`pwd`/${filePath_Rounds}JSON_${fileName}.json"
    fi

fi
