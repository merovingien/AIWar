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

#include "stat_manager.hpp"

using namespace aiwar::core;

Fighter::Fighter(GameManager &gm, Key k, double px, double py, Team team, PlayFunction& pf)
    : Item(gm, k, px, py, Config::instance().FIGHTER_SIZE_X, Config::instance().FIGHTER_SIZE_Y, Config::instance().FIGHTER_DETECTION_RADIUS),
      Movable(gm, k, Config::instance().FIGHTER_SPEED, Config::instance().FIGHTER_START_FUEL, Config::instance().FIGHTER_MAX_FUEL, Config::instance().FIGHTER_MOVE_CONSO),
      Living(gm, k, Config::instance().FIGHTER_START_LIFE, Config::instance().FIGHTER_MAX_LIFE),
      Playable(team, pf),
      Memory(gm, k, Config::instance().FIGHTER_MEMORY_SIZE),
      _missiles(Config::instance().FIGHTER_START_MISSILE),
      _hasLaunch(false)
{
    _sm.missileCreated(team, _missiles);
}

Fighter::~Fighter()
{
}

void Fighter::_preUpdate(unsigned int ticks)
{
    Movable::preUpdate();
    Playable::_preUpdate(ticks);

    _hasLaunch = false;
}

void Fighter::update(unsigned int tick)
{
    _preUpdate(tick);

    _play(this);

//    std::cout << getLog();
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
            _im.createMissile(this, target);
            _missiles--;
            _sm.missileLaunched(_team, 1);
            _hasLaunch = true;
        }
    }
}

unsigned int Fighter::_addMissiles(unsigned int nb)
{
    unsigned int p = nb;
    if(p > Config::instance().FIGHTER_MAX_MISSILE - _missiles)
        p = Config::instance().FIGHTER_MAX_MISSILE - _missiles;

    _missiles += p;

    return p;
}
