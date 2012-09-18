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

#include "item_manager.hpp"

#include "item.hpp"
#include "living.hpp"
#include "missile.hpp"
#include "base.hpp"
#include "miningship.hpp"
#include "mineral.hpp"
#include "fighter.hpp"

#include <stdexcept>

using namespace aiwar::core;

ItemManager::~ItemManager()
{
    ItemSet::iterator it;
    // delete all items
    for(it = _itemSet.begin() ; it != _itemSet.end() ; ++it)
    {
	delete *it;
    }
}

void ItemManager::update(unsigned int tick)
{
    ItemSet::iterator it, tmp;
    Item* i;
    // update all items if not to remove
    for(it = _itemSet.begin() ; it != _itemSet.end() ; ++it)
    {
	i = *it;
	if(!i->_toRemove())
	    i->update(tick);
    }

    // remove some items
    for(it = _itemSet.begin() ; it != _itemSet.end() ; )
    {
	// keep trace of the current iterator *before* increment
	tmp = it++;
	
	i = *tmp;
	if(i->_toRemove())
	{
	    delete i;
	    _itemSet.erase(tmp);  // this unvalidates tmp, but it has been created before
	}
    }
}

Missile* ItemManager::createMissile(Item* launcher, Living* target)
{
    Missile *m = new Missile(launcher->xpos(), launcher->ypos(), target);
    _itemSet.insert(m);
    return m;
}

Base* ItemManager::createBase(double px, double py, Playable::Team team)
{
    TeamMap::const_iterator cit = _teamMap.find(team);
    if(cit != _teamMap.end())
    {
	Base *b = new Base(this, px, py, team, cit->second.play_base);
	_itemSet.insert(b);
	return b;
    }
    else
    {
	throw std::runtime_error("Team not registered");
    }
}

MiningShip* ItemManager::createMiningShip(double px, double py, Playable::Team team)
{
    TeamMap::const_iterator cit = _teamMap.find(team);
    if(cit != _teamMap.end())
    {
	MiningShip *t = new MiningShip(px, py, team, cit->second.play_miningShip);
	_itemSet.insert(t);
	return t;
    }
    else
    {
	throw std::runtime_error("Team not registered");
    }
}

MiningShip* ItemManager::createMiningShip(Base* base)
{
    return createMiningShip(base->xpos(), base->ypos(), base->team());
}

Mineral* ItemManager::createMineral(double px, double py)
{
    Mineral *m = new Mineral(px, py);
    _itemSet.insert(m);
    return m;
}

Fighter* ItemManager::createFighter(double px, double py, Playable::Team team)
{
    TeamMap::const_iterator cit = _teamMap.find(team);
    if(cit != _teamMap.end())
    {
	Fighter *f = new Fighter(this, px, py, team, cit->second.play_fighter);
	_itemSet.insert(f);
	return f;
    }
    else
    {
	throw std::runtime_error("Team is not registered");
    }
}

Fighter* ItemManager::createFighter(Base *base)
{
    return createFighter(base->xpos(), base->ypos(), base->team());
}

void ItemManager::registerTeam(Playable::Team team, Playable::PlayFunction pfBase, Playable::PlayFunction pfMiningShip, Playable::PlayFunction pfFighter)
{
    TeamInfo& ti = _teamMap[team];
    ti.play_base = pfBase;
    ti.play_miningShip = pfMiningShip;
    ti.play_fighter = pfFighter;
}

std::set<Item*>::const_iterator ItemManager::begin() const
{
    return _itemSet.begin();
}

std::set<Item*>::const_iterator ItemManager::end() const
{
    return _itemSet.end();
}
	    
