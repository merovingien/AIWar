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

#include "mineral.hpp"

#include <iostream>

#include "config.hpp"

using namespace aiwar::core;

Mineral::Mineral(double px, double py)
    : Item(px, py, MINERAL_SIZE_X, MINERAL_SIZE_Y),
      Living(MINERAL_LIFE, MINERAL_LIFE)
{
}

void Mineral::update(unsigned int)
{
}

