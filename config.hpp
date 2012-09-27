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

#ifndef CONFIG_HPP
#define CONFIG_HPP

const double       WORLD_SIZE_X = 800;
const double       WORLD_SIZE_Y = 800;
const bool         DRAW_DEBUG = false;

// TEAM number 0 is reserved
const unsigned int TEAM_BLUE = 1;
const unsigned int TEAM_RED  = 2;

const double       MINERAL_SIZE_X = 4.0;
const double       MINERAL_SIZE_Y = 4.0;
const unsigned int MINERAL_LIFE = 2000;

const double       MININGSHIP_SIZE_X = 16.0;
const double       MININGSHIP_SIZE_Y = 16.0;
const double       MININGSHIP_SPEED = 5.0;
const double       MININGSHIP_DETECTION_RADIUS = 160.0; //160.0;
const unsigned int MININGSHIP_MAX_LIFE = 1000;
const unsigned int MININGSHIP_START_LIFE = 600;
const unsigned int MININGSHIP_START_FUEL = 600;
const unsigned int MININGSHIP_MAX_FUEL = 600;
const unsigned int MININGSHIP_MOVE_CONSO = 5;
const double       MININGSHIP_MINING_RADIUS = 30;
const unsigned int MININGSHIP_MINERAL_EXTRACT = 50;
const unsigned int MININGSHIP_MAX_MINERAL_STORAGE = 2000;
const unsigned int MININGSHIP_MEMORY_SIZE = 4;

const double       FIGHTER_SIZE_X = 16.0;
const double       FIGHTER_SIZE_Y = 16.0;
const double       FIGHTER_SPEED = 5.0;
const double       FIGHTER_DETECTION_RADIUS = 160.0; //160.0;
const unsigned int FIGHTER_MAX_LIFE = 1000;
const unsigned int FIGHTER_START_LIFE = 600;
const unsigned int FIGHTER_MOVE_CONSO = 5;
const unsigned int FIGHTER_START_FUEL = 600;
const unsigned int FIGHTER_MAX_FUEL = 600;
const unsigned int FIGHTER_MEMORY_SIZE = 4;
const unsigned int FIGHTER_START_MISSILE = 8;
const unsigned int FIGHTER_MAX_MISSILE = 12;

const double       MISSILE_SIZE_X = 5.0;
const double       MISSILE_SIZE_Y = 1.0;
const unsigned int MISSILE_LIFE = 10;
const unsigned int MISSILE_MOVE_CONSO = 2;
const unsigned int MISSILE_START_FUEL = 50;
const unsigned int MISSILE_MAX_FUEL = 50;
const double       MISSILE_SPEED = 20.0;
const unsigned int MISSILE_DAMAGE = 200;

const double       BASE_SIZE_X = 25.0;
const double       BASE_SIZE_Y = 25.0;
const double       BASE_DETECTION_RADIUS = 200.0;
const unsigned int BASE_MAX_LIFE = 10000;
const unsigned int BASE_START_LIFE = 5000;
const unsigned int BASE_MISSILE_PRICE = 60;
const unsigned int BASE_MININGSHIP_PRICE = 300;
const unsigned int BASE_FIGHTER_PRICE = 100 + BASE_MISSILE_PRICE * FIGHTER_START_MISSILE; // ie 580
const unsigned int BASE_START_MINERAL_STORAGE = 1000;
const unsigned int BASE_MAX_MINERAL_STORAGE = 50000;
const unsigned int BASE_MEMORY_SIZE = 6;
const double       BASE_REPAIR_RADIUS = 30.0;
const double       BASE_REFUEL_RADIUS = 30.0;

const double       COMMUNICATION_RADIUS = 60;

#endif /* CONFIG_HPP */
