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

#include "missile.hpp"

#include <iostream>
#include <sstream>

#include "stat_manager.hpp"
#include "config.hpp"

using namespace aiwar::core;

Missile::Missile(GameManager& gm, Key k, double px, double py, Living* target)
    : Item(gm, k, px, py, Config::instance().MISSILE_SIZE_X, Config::instance().MISSILE_SIZE_Y),
      Movable(gm, k, Config::instance().MISSILE_SPEED, Config::instance().MISSILE_START_FUEL, Config::instance().MISSILE_MAX_FUEL, Config::instance().MISSILE_MOVE_CONSO),
      Living(gm, k, Config::instance().MISSILE_LIFE, Config::instance().MISSILE_LIFE),
      _target(target->_getKey())
{
    // set angle
    rotateTo(target);
}

Missile::~Missile()
{
}

void Missile::update(unsigned int tick)
{
    Movable::_preUpdate(tick);

    // check if the target is still alive
    Living *target = dynamic_cast<Living*>(_im.get(_target));
    if(!target || target->_toRemove())
    {
        // no more target, auto destruction
        _toRemoveFlag = true;
        _sm.itemDestroyed(this);
    }
    else
    {
        // move to the target
        rotateTo(target);
        double d = distanceTo(target);
        bool reached = false;
        if(d <= _speed)
        {
            _speed = d;
            reached = true;
        }
        move();

        // target reached ?
        if(reached)
        {
            target->_takeLife(Config::instance().MISSILE_DAMAGE, true);
            _toRemoveFlag = true;
            _sm.itemDestroyed(this);
        }
        // enough fuel to continue ?
        else if(_fuel < Config::instance().MISSILE_MOVE_CONSO)
        {
            _toRemoveFlag = true;
            _sm.itemDestroyed(this);
        }
    }
}

std::string Missile::_dump() const
{
    std::ostringstream oss;
    oss << _key << " Missile pos=" << xpos() << "x" << ypos() << " angle=" << angle() << " fuel=" << Movable::fuel() << " target=" << _target << "\n";
    return oss.str();
}
