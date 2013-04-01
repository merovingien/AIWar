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

#include "playable.hpp"

#include "movable.hpp"

#include <iostream>

using namespace aiwar::core;

DefaultPlayFunction Playable::playNoOp(0);

Playable::Playable(GameManager& gm, Key k, Team team, PlayFunction& play)
    : Item(gm, k),
      _team(team),
      _play(play),
      _state(DEFAULT)
{
}

Playable::~Playable()
{
}

Team Playable::team() const
{
    return _team;
}

bool Playable::isFriend(const Playable* p) const
{
    return p->_team == _team;
}

void Playable::log(const std::string &msg)
{
    _log << msg << "\n";
}

std::string Playable::getLog() const
{
    return _log.str();
}

void Playable::state(State state)
{
    _state = state;
}

State Playable::getState() const
{
    return _state;
}

unsigned int Playable::fuel(const Movable* other) const
{
    unsigned int r = 0;
    if(this->distanceTo(other) <= Config::instance().COMMUNICATION_RADIUS)
    {
        // we return fuel only if other is a Playable and is a friend. Else we always return 0.
        const Playable* o = dynamic_cast<const Playable*>(other);
        if(o)
        {
            if(this->isFriend(o))
            {
                r = other->fuel();
            }
            else
            {
                std::cerr << "Quering fuel of ennemy is forbidden\n";
            }
        }
        else
        {
            std::cerr << "Quering fuel of non Playable item is forbidden\n";
        }
    }
    else
    {
        std::cerr << "Item is to far to query fuel\n";
    }
    return r;
}

void Playable::_preUpdate(unsigned long)
{
    _log.str("");
}
