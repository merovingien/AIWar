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

#include "test_handler.hpp"

#include "base.hpp"
#include "miningship.hpp"
#include "fighter.hpp"
#include "missile.hpp"
#include "mineral.hpp"

#include <iostream>

using namespace aiwar;

TestHandler::TestHandler()
    : _pf_Base(&play_base), _pf_MiningShip(&play_miningship), _pf_Fighter(&play_fighter)
{
}

bool TestHandler::initialize()
{
    return true;
}

bool TestHandler::finalize()
{
    return true;
}

bool TestHandler::load(P, const std::string&)
{
    return true;
}

bool TestHandler::unload(P)
{
    return true;
}

TestHandler::PF& TestHandler::get_BaseHandler(P)
{
    return _pf_Base;
}

TestHandler::PF& TestHandler::get_MiningShipHandler(P)
{
    return _pf_MiningShip;
}

TestHandler::PF& TestHandler::get_FighterHandler(P)
{
    return _pf_Fighter;
}

void TestHandler::play_miningship(aiwar::core::Playable* item)
{
    using namespace aiwar::core;
    using std::cout;
    using std::endl;

    MiningShip *self = dynamic_cast<aiwar::core::MiningShip*>(item);

    Item::ItemSet neighbours = self->neighbours();
//    cout << *self <<  ": Number of neighbours: " << neighbours.size() << endl;

    Item::ItemSet::iterator it;
    for(it = neighbours.begin() ; it != neighbours.end() ; it++)
    {
	Mineral *m = dynamic_cast<Mineral*>(*it);
	if(m) // m is a Mineral
	{
	    double d = self->distanceTo(m);
	    if(d <= Config::instance().MININGSHIP_MINING_RADIUS)
	    {
		/*unsigned int e =*/ self->extract(m);
//		cout << *self << ": Meet a Mineral, extracted: " << e << endl;
	    }
	    else
	    {
		self->rotateTo(m);
		self->move();
	    }
	}
    }

    self->rotateOf(15);
    self->move();

//    cout << *self << ": Life: " << self->life() << endl;
}


void TestHandler::play_base(aiwar::core::Playable* item)
{
    using namespace aiwar::core;
    using std::cout;
    using std::endl;

    Base *self = dynamic_cast<Base*>(item);

    Item::ItemSet neighbours = self->neighbours();
//    cout << *self << ": Number of neighbours: " << neighbours.size() << endl;

    Item::ItemSet::iterator it;
    for(it = neighbours.begin() ; it != neighbours.end() ; ++it)
    {
	aiwar::core::MiningShip *s = dynamic_cast<aiwar::core::MiningShip*>(*it);
	if(s)
	{
	    if(! self->isFriend(s))
	    {
		self->launchMissile(s);
//		cout << *self << ": launch a missile to " << *s << endl;
	    }
	    else
	    {
		self->setMemory(0, 5, s);
		/*int i =*/ self->getMemory<int>(0, s);
//		cout << *self << ": get Memory from " << *s << ": " << i << endl;
	    }
	}
    }

    if(self->mineralStorage() > Config::instance().BASE_MININGSHIP_PRICE*2)
    {
	self->createMiningShip();
//	cout << *self << ": create a new MiningShip" << endl;
    }

//    cout << *self << ": Life: " << self->life() << endl;

    self->setMemory(1, 1);
//    cout << *self << ": getMemory<float>(self, 1): " << self->getMemory<float>(1, self) << endl;
}


void TestHandler::play_fighter(aiwar::core::Playable* item)
{
    using namespace aiwar::core;
    using std::cout;
    using std::endl;

    aiwar::core::Fighter * self = dynamic_cast<aiwar::core::Fighter*>(item);

    Item::ItemSet neighbours = self->neighbours();
//    cout << *self << ": Number of neighbours: " << neighbours.size() << endl;

    Item::ItemSet::iterator it;
    for(it = neighbours.begin() ; it != neighbours.end() ; ++it)
    {
	aiwar::core::MiningShip *s = dynamic_cast<aiwar::core::MiningShip*>(*it);
	if(s)
	{
	    if(! self->isFriend(s))
	    {
		self->launchMissile(s);
//		cout << *self << ": launch a missile to " << *s << endl;
	    }
	}
    }  
}
