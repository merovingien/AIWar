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

#include "base.hpp"

#include "miningship.hpp"
#include "fighter.hpp"

#include "config.hpp"

#include <iostream>

using namespace aiwar::core;

Base::Base(ItemManager &im, Key k, double xpos, double ypos, Team team, PlayFunction& pf)
    : Item(im, k, xpos, ypos, Config::instance().BASE_SIZE_X, Config::instance().BASE_SIZE_Y, Config::instance().BASE_DETECTION_RADIUS),
      Living(im, k, Config::instance().BASE_START_LIFE, Config::instance().BASE_MAX_LIFE),
      Playable(team, pf),
      Memory(im, k, Config::instance().BASE_MEMORY_SIZE),
      _mineralStorage(Config::instance().BASE_START_MINERAL_STORAGE),
      _hasLaunch(false)
{
//    std::cout << "Ctr Base(" << xpos << "," << ypos << ")" << std::endl;
}

Base::~Base()
{
}

void Base::_preUpdate(unsigned int)
{
    _hasLaunch = false;
}

void Base::update(unsigned int tick)
{
    this->_preUpdate(tick);

    _play(this);
}

void Base::launchMissile(Living* target)
{
    if(!_hasLaunch)
    {
	if(_mineralStorage >= Config::instance().BASE_MISSILE_PRICE)
	{
	    _im.createMissile(this, target);
	    _mineralStorage -= Config::instance().BASE_MISSILE_PRICE;
	    _hasLaunch = true;
	}
    }
}

void Base::createMiningShip()
{
    if(_mineralStorage >= Config::instance().BASE_MININGSHIP_PRICE)
    {
	_im.createMiningShip(this);
	_mineralStorage -= Config::instance().BASE_MININGSHIP_PRICE;
    }
}

unsigned int Base::mineralStorage() const
{
    return _mineralStorage;
}

unsigned int Base::pullMineral(MiningShip *ship, unsigned int mineralPoint)
{
    unsigned int p = 0;

    if(distanceTo(ship) > Config::instance().MININGSHIP_MINING_RADIUS)
    {
	std::cout << "Ship is too far to pull Mineral" << std::endl;
	return p;
    }

    if(isFriend(ship))
    {
	p = mineralPoint;
	if(p > (Config::instance().BASE_MAX_MINERAL_STORAGE - _mineralStorage))
	    p = Config::instance().BASE_MAX_MINERAL_STORAGE - _mineralStorage;

	p = ship->_release(p);
	_mineralStorage += p;
    }
    else
	std::cout << "WARNING: pullMineral from ennemy is forbidden" << std::endl;

    return p;
}

unsigned int Base::repair(unsigned int points)
{
    return repair(points, this);
}

unsigned int Base::repair(unsigned int points, Living *item)
{
    // repect the distance for repairing
    if(distanceTo(item) > Config::instance().BASE_REPAIR_RADIUS)
    {
	std::cout << "Item is to far to be repaired" << std::endl;
	return 0;
    }

    // repair only friends or neutral items
    Playable *pl = NULL;
    if((pl = dynamic_cast<Playable*>(item)))
    {
	if(!isFriend(pl))
	{
	    std::cout << "Repairing ennemy is forbidden" << std::endl;
	    return 0;
	}
    }
    
    unsigned int p = points;
    if(p > _mineralStorage) // cannot put more than the current mineral storage
	p = _mineralStorage;
    p = item->_putLife(p); // p now contain the number of points actually added
    _mineralStorage -= p;
    return p;
}

unsigned int Base::refuel(unsigned int points, Movable *item)
{
   // respect the distance for refueling
    if(distanceTo(item) > Config::instance().BASE_REFUEL_RADIUS)
    {
	std::cout << "Item is to far to be refueled" << std::endl;
	return 0;
    }

    // refuel only friends or neutral items
    Playable *pl = NULL;
    if((pl = dynamic_cast<Playable*>(item)))
    {
	if(!isFriend(pl))
	{
	    std::cout << "Refueled ennemy is forbidden. Moreover, it is stupid." << std::endl;
	    return 0;
	}
    }
    
    unsigned int p = points;
    if(p > _mineralStorage) // cannot put more than the current mineral storage
	p = _mineralStorage;
    p = item->_putFuel(p); // p now contain the number of points actually added
    _mineralStorage -= p;
    return p;
}

void Base::createFighter()
{
   if(_mineralStorage >= Config::instance().BASE_FIGHTER_PRICE)
    {
	_im.createFighter(this);
	_mineralStorage -= Config::instance().BASE_FIGHTER_PRICE;
    }
}

unsigned int Base::giveMissiles(unsigned int nb, Fighter* fighter)
{
    if(!isFriend(fighter))
    {
	std::cerr << "Give missile to an ennemy is forbiden" << std::endl;
	return 0;
    }

    if(distanceTo(fighter) > Config::instance().BASE_GIVE_MISSILE_RADIUS)
    {
	std::cerr << "Give missile failed: fighter is too far" << std::endl;
	return 0;
    }

    unsigned int p = nb;
    if(p * Config::instance().BASE_MISSILE_PRICE > _mineralStorage)
    {
	p = _mineralStorage / Config::instance().BASE_MISSILE_PRICE;
    }
    
    p = fighter->_addMissiles(p);
    _mineralStorage -= p * Config::instance().BASE_MISSILE_PRICE;

    return p;
}


std::ostream& operator<< (std::ostream& os, const Base& b)
{
    os << "Base[" << &b << "]";
    return os;
}
