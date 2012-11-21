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

#include "game_manager.hpp"

#include <iostream>
#include <cmath>

using namespace aiwar::core;

Item::Item(GameManager &gm, Key k, double px, double py, double sx, double sy, double detection) : _im(gm.getItemManager()), _sm(gm.getStatManager()), _key(k), _toRemoveFlag(false), _xpos(px), _ypos(py), _xsize(sx), _ysize(sy), _detection_radius(detection)
{
//    std::cout << "Ctr Item(" << px << "," << py << ") -> " << this << std::endl;
}

Item::~Item()
{
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
    ItemManager::ItemMap::const_iterator cit;
    for(cit = _im.begin() ; cit != _im.end() ; cit++)
    {
        Item* i = cit->second;
        if(i->_key == this->_key)
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

Item::Key Item::_getKey() const
{
    return _key;
}
