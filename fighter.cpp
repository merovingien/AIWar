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

#include "fighter.hpp"

#include "item_manager.hpp"

using namespace aiwar::core;

Fighter::Fighter(ItemManager* im, double px, double py, Team team, PlayFunction& pf)
    : Item(px, py, FIGHTER_SIZE_X, FIGHTER_SIZE_Y, FIGHTER_DETECTION_RADIUS),
      Movable(FIGHTER_SPEED, FIGHTER_START_FUEL, FIGHTER_MAX_FUEL, FIGHTER_MOVE_CONSO),
      Living(FIGHTER_START_LIFE, FIGHTER_MAX_LIFE),
      Playable(team, pf),
      Memory(FIGHTER_MEMORY_SIZE),
      _im(im),
      _missiles(FIGHTER_START_MISSILE),
      _hasLaunch(false)
{
}
	 
Fighter::~Fighter()
{
}

void Fighter::_preUpdate(unsigned int)
{
    _hasLaunch = false;
}

void Fighter::update(unsigned int tick)
{
    Movable::preUpdate();
    this->_preUpdate(tick);

    _play(this);
}

unsigned int Fighter::missiles() const
{
    return _missiles;
}

void Fighter::launchMissile(Living* target)
{
    if(!_hasLaunch)
    {
	if(_missiles > 0)
	{
	    _im->createMissile(this, target);
	    _missiles--;
	    _hasLaunch = true;
	}
    }
}

unsigned int Fighter::_addMissiles(unsigned int nb)
{
    unsigned int p = nb;
    if(p > FIGHTER_MAX_MISSILE - _missiles)
	p = FIGHTER_MAX_MISSILE - _missiles;
    
    _missiles += p;

    return p;
}
