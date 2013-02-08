/*
 * Copyright (C) 2012 Paul Grégoire
 *
 * This file is part of AIWar.
 *
 * AIWar is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * AIWar is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with AIWar.  If not, see <http://www.gnu.org/licenses/>.
 */

#include "game_manager.hpp"

#include "base.hpp"
#include "miningship.hpp"
#include "fighter.hpp"
#include "missile.hpp"
#include "mineral.hpp"
#include "item_manager.hpp"
#include "stat_manager.hpp"

#include <iostream>
#include <stdexcept>

using namespace aiwar::core;


GameManager::GameManager() : _im(NULL), _sm(NULL)
{
    _im = new ItemManager(*this);
    _sm = new StatManager();
}

GameManager::~GameManager()
{
    if(_im)
    {
        delete _im;
        _im = NULL;
    }

    if(_sm)
    {
        delete _sm;
        _sm = NULL;
    }
}

bool GameManager::init()
{
    return _im->init();
}

ItemManager& GameManager::getItemManager()
{
    return *_im;
}

const ItemManager& GameManager::getItemManager() const
{
    return *_im;
}

StatManager& GameManager::getStatManager()
{
    return *_sm;
}

const StatManager& GameManager::getStatManager() const
{
    return *_sm;
}

void GameManager::update(unsigned int ticks)
{
    _sm->nextRound();
    _im->update(ticks);
    _sm->checkActivity();
}

void GameManager::registerTeam(Team team, PlayFunction& pfBase, PlayFunction& pfMiningShip, PlayFunction& pfFighter)
{
    TeamInfo t(pfBase, pfMiningShip, pfFighter);
    _teamMap.insert(std::pair<Team, TeamInfo>(team, t));
}

PlayFunction& GameManager::getBasePF(Team team) const
{
    return _getTeamInfo(team).play_base;
}

PlayFunction& GameManager::getMiningShipPF(Team team) const
{
    return _getTeamInfo(team).play_miningShip;
}

PlayFunction& GameManager::getFighterPF(Team team) const
{
    return _getTeamInfo(team).play_fighter;
}

bool GameManager::gameOver() const
{
    int nbLivingTeam = 0;

    TeamMap::const_iterator cit;
    for(cit = _teamMap.begin() ; cit != _teamMap.end() ; ++cit)
    {
        if(getStatManager().baseCurrent(cit->first) > 0)
            nbLivingTeam++;
    }

    return (nbLivingTeam < 2) || _sm->inactiveRounds() > 50; // 50 consecutive inactive rounds lead to draw
}

Team GameManager::getWinner() const
{
    Team winner = NO_TEAM;
    int nbLivingTeam = 0;

    TeamMap::const_iterator cit;
    for(cit = _teamMap.begin() ; cit != _teamMap.end() ; ++cit)
    {
        if(getStatManager().baseCurrent(cit->first) > 0)
        {
            nbLivingTeam++;
            winner = cit->first;
        }
    }

    if(nbLivingTeam != 1) // game not over, or draw !
        return NO_TEAM;
    else
        return winner;
}

const GameManager::TeamInfo& GameManager::_getTeamInfo(Team team) const
{
    TeamMap::const_iterator it = _teamMap.find(team);
    if(it != _teamMap.end())
        return it->second;
    else
        throw std::runtime_error("Team is not registered");
}


GameManager::TeamInfo::TeamInfo(PlayFunction& pfb, PlayFunction& pfm, PlayFunction& pff)
    : play_base(pfb), play_miningShip(pfm), play_fighter(pff)
{
}
