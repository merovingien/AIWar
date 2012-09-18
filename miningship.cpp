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

#include "miningship.hpp"

#include <iostream>

#include "config.hpp"
#include "mineral.hpp"
#include "base.hpp"

using namespace aiwar::core;

MiningShip::MiningShip(double xpos, double ypos, Team team, PlayFunction pf)
    : Item(xpos, ypos, MININGSHIP_SIZE_X, MININGSHIP_SIZE_Y, MININGSHIP_DETECTION_RADIUS),
      Movable(MININGSHIP_SPEED, MININGSHIP_START_FUEL, MININGSHIP_MAX_FUEL, MININGSHIP_MOVE_CONSO),
      Living(MININGSHIP_START_LIFE, MININGSHIP_MAX_LIFE),
      Playable(team, pf),
      Memory(MININGSHIP_MEMORY_SIZE),
      _mineralStorage(0),
      _hasExtracted(false)
{
}

MiningShip::~MiningShip()
{
}

void MiningShip::_preUpdate(unsigned int)
{
    _hasExtracted = false;
}

void MiningShip::update(unsigned int tick)
{
    Movable::preUpdate();
    this->_preUpdate(tick);

    if(_play)
	_play(this);
}

unsigned int MiningShip::extract(Mineral *m)
{
    unsigned int extracted = 0;
    if(!_hasExtracted)
    {
	if(distanceTo(m) <= MININGSHIP_MINING_RADIUS)
	{
	    unsigned int toExtract = ( (MININGSHIP_MAX_MINERAL_STORAGE-_mineralStorage) < MININGSHIP_MINERAL_EXTRACT ) ? (MININGSHIP_MAX_MINERAL_STORAGE-_mineralStorage) : MININGSHIP_MINERAL_EXTRACT;
	    extracted = m->_takeLife(toExtract);
	    _mineralStorage += extracted;
	}
	else
	{
	    std::cout << "Mining failed: Mineral is too far" << std::endl;
	}
    }
    else
    {
	std::cout << "Cannot extract twice in one play round" << std::endl;
    }

    if(extracted > 0)
	_hasExtracted = true;

    return extracted;
}

unsigned int MiningShip::mineralStorage() const
{
    return _mineralStorage;
}

unsigned int MiningShip::pushMineral(Base *base, unsigned int mp)
{
    return base->pullMineral(this, mp);
}

unsigned int MiningShip::_release(unsigned int mp)
{
    unsigned int p = 0;
    if(mp <= _mineralStorage)
    {
	p = mp;
	_mineralStorage -= mp;
    }
    else
    {
	p = _mineralStorage;
	_mineralStorage = 0;
    }
    return p;
}

std::ostream& operator<< (std::ostream& os, const MiningShip& t)
{
    os << "MiningShip[" << &t << "]";
    return os;
}
