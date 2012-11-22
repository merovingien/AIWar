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

#include "living.hpp"

#include <iostream>

using namespace aiwar::core;

Living::Living(GameManager& gm, Key k) : Item(gm, k), _maxLife(0), _life(0)
{
}

Living::Living(GameManager& gm, Key k, unsigned int life, unsigned int maxLife) : Item(gm, k), _maxLife(maxLife), _life(life)
{
}

Living::~Living()
{
//    std::cout << "~Living: " << this << std::endl;
}

unsigned int Living::_takeLife(unsigned int v, bool kill)
{
    unsigned int tmp = _life;
    if(v <= _life)
        _life -= v;
    else
        _life = 0;
    if(kill && _life == 0)
        _toRemoveFlag = true;
    return (tmp - _life);
}

unsigned int Living::_putLife(unsigned int v)
{
    unsigned int tmp = _life;
    _life += v;
    if(_life > _maxLife)
        _life = _maxLife;
    return (_life - tmp);
}

unsigned int Living::life() const
{
    return _life;
}

bool Living::_isDead() const
{
    return _life == 0;
}
