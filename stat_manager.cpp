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

#include "stat_manager.hpp"

#include "base.hpp"
#include "miningship.hpp"
#include "fighter.hpp"
#include "missile.hpp"
#include "mineral.hpp"

#include <iostream>
#include <iomanip>
#include <stdexcept>

using namespace aiwar::core;


StatManager::StatManager() : _round(0)
{
}

StatManager::~StatManager()
{
}

void StatManager::nextRound()
{
    _round++;
}
 
unsigned int StatManager::round() const
{
    return _round;
}

void StatManager::baseCreated(const Base* b)
{
    TeamInfo &info = _teamMap[b->team()];
    info.nb_base++;
    info.nb_base_max++;
}

void StatManager::baseDestroyed(const Base* b)
{
    TeamInfo &info = _teamMap[b->team()];
    info.nb_base--;
}

unsigned int StatManager::baseCurrent(const Team& t) const
{
    return _teamMap.find(t)->second.nb_base;
}

unsigned int StatManager::baseMax(const Team& t) const
{
    return _teamMap.find(t)->second.nb_base_max;
}

void StatManager::miningShipCreated(const MiningShip* m)
{
    TeamInfo &info = _teamMap[m->team()];
    info.nb_miningShip++;
    info.nb_miningShip_max++;
}

void StatManager::miningShipDestroyed(const MiningShip* m)
{
    TeamInfo &info = _teamMap[m->team()];
    info.nb_miningShip--;
}

unsigned int StatManager::miningShipCurrent(const Team& t) const
{
    return _teamMap.find(t)->second.nb_miningShip;
}

unsigned int StatManager::miningShipMax(const Team& t) const
{
    return _teamMap.find(t)->second.nb_miningShip_max;
}

void StatManager::fighterCreated(const Fighter* f)
{
    TeamInfo &info = _teamMap[f->team()];
    info.nb_fighter++;
    info.nb_fighter_max++;
}

void StatManager::fighterDestroyed(const Fighter* f)
{
    TeamInfo &info = _teamMap[f->team()];
    info.nb_fighter--;
}

unsigned int StatManager::fighterCurrent(const Team& t) const
{
    return _teamMap.find(t)->second.nb_fighter;
}

unsigned int StatManager::fighterMax(const Team& t) const
{
    return _teamMap.find(t)->second.nb_fighter_max;
}

void StatManager::missileCreated(const Team& t, unsigned int nb)
{
    TeamInfo &info = _teamMap[t];
    info.nb_missile_created += nb;
}

void StatManager::missileLaunched(const Team& t, unsigned int nb)
{
    TeamInfo &info = _teamMap[t];
    info.nb_missile_launched += nb;
}

void StatManager::mineralSaved(const Team &t, unsigned int m)
{
    TeamInfo &info = _teamMap[t];
    info.nb_mineral_saved += m;
}

void StatManager::mineralSpent(const Team &t, unsigned int m)
{
    TeamInfo &info = _teamMap[t];
    info.nb_mineral_spent += m;
}

void StatManager::itemDestroyed(const Item* item)
{
    const aiwar::core::MiningShip *miningShip;
    const aiwar::core::Base *base;
    const aiwar::core::Fighter *fighter;

    if((fighter = dynamic_cast<const aiwar::core::Fighter*>(item)))
        fighterDestroyed(fighter);
    else if((miningShip = dynamic_cast<const aiwar::core::MiningShip*>(item)))
        miningShipDestroyed(miningShip);
    else if((base = dynamic_cast<const aiwar::core::Base*>(item)))
        baseDestroyed(base);
}

std::string StatManager::dump() const
{
    std::ostringstream oss;
    TeamMap::const_iterator cit;
    aiwar::core::Config &cfg = aiwar::core::Config::instance();
    
    oss << "*******************ROUND " << std::setfill('*') << std::setw(21) << std::left << _round << "\n";
    oss << "----------------------------------------------\n";
    for(cit = _teamMap.begin() ; cit != _teamMap.end() ; ++cit)
    {
        if(cit->first == BLUE_TEAM)
        {
            oss << "Blue team: " << cfg.players[cfg.blue].name << "\n";
        }
        else if(cit->first == RED_TEAM)
        {
            oss << "Red team: " << cfg.players[cfg.red].name << "\n";
        }
        else
        {
            oss << "No team\n";
        }
        oss << "\tBases (current/max):         " << cit->second.nb_base << " / " << cit->second.nb_base_max << "\n"
            << "\tMiningShips (current/max):   " << cit->second.nb_miningShip << " / " << cit->second.nb_miningShip_max << "\n"
            << "\tFighters (current/max):      " << cit->second.nb_fighter << " / " << cit->second.nb_fighter_max << "\n"
            << "\tMissiles (created/launched): " << cit->second.nb_missile_created << " / " << cit->second.nb_missile_launched << "\n"
            << "\tMinerals (spent/saved):      " << cit->second.nb_mineral_spent << " / " << cit->second.nb_mineral_saved << "\n"
            << "----------------------------------------------\n";

    }
    return oss.str();
}

void StatManager::print() const
{
    std::cout << dump();
}


StatManager::TeamInfo::TeamInfo()
    : nb_base(0), nb_base_max(0),
      nb_miningShip(0), nb_miningShip_max(0),
      nb_fighter(0), nb_fighter_max(0),
      nb_missile_created(0), nb_missile_launched(0),
      nb_mineral_saved(0), nb_mineral_spent(0)
{
}
