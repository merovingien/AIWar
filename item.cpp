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

#include "item.hpp"

#include <iostream>
#include <cmath>

using namespace aiwar::core;

std::set<Item*> Item::_itemSet;

Item::Item(double px, double py, double sx, double sy, double detection) : _toRemoveFlag(false), _xpos(px), _ypos(py), _xsize(sx), _ysize(sy), _detection_radius(detection)
{
//    std::cout << "Ctr Item(" << px << "," << py << ") -> " << this << std::endl;
    _itemSet.insert(this);
}

Item::~Item()
{
    _itemSet.erase(this);
}

double Item::xpos() const
{
    return _xpos;
}

double Item::ypos() const
{
    return _ypos;
}

Item::ItemSet Item::neighbours() const
{
//    std::cout << "getNeighbours, size=" << _itemSet.size() << " this=" << this << std::endl;

    ItemSet res;
    ItemSet::const_iterator cit;
    for(cit = _itemSet.begin() ; cit != _itemSet.end() ; cit++)
    {
	Item* i = *cit;
//	std::cout << "Item " << i << std::endl;
	if(i == this)
	    continue;

	if(i->_toRemove())
	    continue;

	double distance = (i->_xpos - _xpos) * (i->_xpos - _xpos) + (i->_ypos - _ypos) * (i->_ypos - _ypos);
	if(distance > _detection_radius * _detection_radius)
	    continue;

	res.insert(i);
    }

    return res;
}

double Item::distanceTo(const Item *i) const
{
    return distanceTo(i->_xpos, i->_ypos);
}

double Item::distanceTo(double px, double py) const
{
    return sqrt( (px - _xpos) * (px - _xpos) + (py - _ypos) * (py - _ypos) );
}


bool Item::_toRemove() const
{
    return _toRemoveFlag;
}

bool Item::_exists(Item* item)
{
//    std::cout << "_exists(" << item << ")" << std::endl;
    ItemSet::const_iterator cit = _itemSet.find(item);
    if(cit != _itemSet.end())
	return !(*cit)->_toRemove();
    else
	return false;
}
