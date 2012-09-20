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

#include "game_manager.hpp"

using namespace aiwar::core;

ItemManager::ItemManager(GameManager& gm) : _gm(gm)
{
}

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
	    _gm.itemDestroyed(i);
	    delete i;
	    _itemSet.erase(tmp);  // this unvalidates tmp, but 'it' has been updated before
	}
    }
}

Missile* ItemManager::createMissile(Item* launcher, Living* target)
{
    Missile *m = new Missile(launcher->xpos(), launcher->ypos(), target);
    _itemSet.insert(m);
    _gm.missileCreated(m);
    return m;
}

Base* ItemManager::createBase(double px, double py, Playable::Team team)
{
    Base *b = new Base(this, px, py, team, _gm.getBasePF(team));
    _itemSet.insert(b);
    _gm.baseCreated(b);
    return b;
}

MiningShip* ItemManager::createMiningShip(double px, double py, Playable::Team team)
{
    MiningShip *t = new MiningShip(px, py, team, _gm.getMiningShipPF(team));
    _itemSet.insert(t);
    _gm.miningShipCreated(t);
    return t;
}

MiningShip* ItemManager::createMiningShip(Base* base)
{
    return createMiningShip(base->xpos(), base->ypos(), base->team());
}

Mineral* ItemManager::createMineral(double px, double py)
{
    Mineral *m = new Mineral(px, py);
    _itemSet.insert(m);
    _gm.mineralCreated(m);
    return m;
}

Fighter* ItemManager::createFighter(double px, double py, Playable::Team team)
{
    Fighter *f = new Fighter(this, px, py, team, _gm.getFighterPF(team));
    _itemSet.insert(f);
    _gm.fighterCreated(f);
    return f;
}

Fighter* ItemManager::createFighter(Base *base)
{
    return createFighter(base->xpos(), base->ypos(), base->team());
}

std::set<Item*>::const_iterator ItemManager::begin() const
{
    return _itemSet.begin();
}

std::set<Item*>::const_iterator ItemManager::end() const
{
    return _itemSet.end();
}
	    
