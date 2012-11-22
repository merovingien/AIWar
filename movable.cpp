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

#include "movable.hpp"

#include <iostream>
#include <cmath>

#ifndef M_PI
#       define M_PI 3.1415926535897932384626433832795
#endif

using namespace aiwar::core;

Movable::~Movable()
{
}

Movable::Movable(GameManager& gm, Key k, double speed, unsigned int startFuel, unsigned int maxFuel, unsigned int moveConso, double angle)
    : Item(gm, k), _xdest(0.0), _ydest(0.0), _speed(speed), _angle(angle), _fuel(startFuel), _maxFuel(maxFuel), _moveConso(moveConso), _hasMoved(false)
{
    // update _xdest and _ydest with the real position of the item.
    // _xpos and _ypos has been set with the value given in the constructor of the final item.
    _xdest = _xpos;
    _ydest = _ypos;

//    std::cout << "Ctr Movable()" << std::endl;
}

void Movable::rotateOf(double angle)
{
    _angle += angle;
}

void Movable::rotateTo(const Item* target)
{
    rotateTo(target->xpos(), target->ypos());
}

void Movable::rotateTo(double px, double py)
{
    _angle = atan2(_ypos-py, px-_xpos) * 180.0 / M_PI;
}

void Movable::move()
{
    if(!_hasMoved && doMove())
    {
        _xdest += cos(_angle * M_PI / 180.0) * _speed;
        _ydest -= sin(_angle * M_PI / 180.0) * _speed;

        _hasMoved = true;
    }
}

double Movable::angle() const
{
    return _angle;
}

double Movable::xdest() const
{
    return _xdest;
}

double Movable::ydest() const
{
    return _ydest;
}

unsigned int Movable::fuel() const
{
    return _fuel;
}

void Movable::preUpdate()
{
    _xpos = _xdest;
    _ypos = _ydest;
    _hasMoved = false;
}

bool Movable::doMove()
{
    if(_fuel < _moveConso)
        return false;

    _fuel -= _moveConso;
    return true;
}

unsigned int Movable::_putFuel(unsigned int points)
{
    unsigned int p = points;
    if(p > _maxFuel - _fuel)
        p = _maxFuel - _fuel;

    _fuel += p;

    return p;
}
