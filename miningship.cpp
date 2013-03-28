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

#include "miningship.hpp"

#include <iostream>

#include "config.hpp"
#include "mineral.hpp"
#include "base.hpp"

#include "stat_manager.hpp"

using namespace aiwar::core;

MiningShip::MiningShip(GameManager& gm, Key k, double xpos, double ypos, Team team, PlayFunction& pf)
    : Item(gm, k, xpos, ypos, Config::instance().MININGSHIP_SIZE_X, Config::instance().MININGSHIP_SIZE_Y, Config::instance().MININGSHIP_DETECTION_RADIUS),
      Movable(gm, k, Config::instance().MININGSHIP_SPEED, Config::instance().MININGSHIP_START_FUEL, Config::instance().MININGSHIP_MAX_FUEL, Config::instance().MININGSHIP_MOVE_CONSO),
      Living(gm, k, Config::instance().MININGSHIP_START_LIFE, Config::instance().MININGSHIP_MAX_LIFE),
      Playable(gm, k, team, pf),
      Memory(gm, k, Config::instance().MININGSHIP_MEMORY_SIZE),
      _mineralStorage(0),
      _hasExtracted(false)
{
}

MiningShip::~MiningShip()
{
}

void MiningShip::_preUpdate(unsigned int ticks)
{
    Movable::_preUpdate(ticks);
    Playable::_preUpdate(ticks);

    _hasExtracted = false;
}

void MiningShip::update(unsigned int tick)
{
    _preUpdate(tick);

    _play(this);

//    std::cout << getLog();
}

unsigned int MiningShip::extract(Mineral *m)
{
    unsigned int extracted = 0;
    if(!_hasExtracted)
    {
        if(distanceTo(m) <= Config::instance().MININGSHIP_MINING_RADIUS)
        {
            unsigned int toExtract = ( (Config::instance().MININGSHIP_MAX_MINERAL_STORAGE-_mineralStorage) < Config::instance().MININGSHIP_MINERAL_EXTRACT ) ? (Config::instance().MININGSHIP_MAX_MINERAL_STORAGE-_mineralStorage) : Config::instance().MININGSHIP_MINERAL_EXTRACT;
            extracted = m->_takeLife(toExtract);
            _setMineralStorage(extracted);
        }
        else
        {
            std::cout << "Mining failed: Mineral is too far" << std::endl;
        }
    }
    else
    {
        std::cout << "Cannot extract twice in one play round" << std::endl;
    }

    if(extracted > 0)
    {
        _hasExtracted = true;
        _sm.reportActivity();
    }

    return extracted;
}

unsigned int MiningShip::mineralStorage() const
{
    return _mineralStorage;
}

unsigned int MiningShip::pushMineral(Base *base, unsigned int mp)
{
    return base->pullMineral(this, mp);
}

unsigned int MiningShip::_release(unsigned int mp)
{
    unsigned int p = 0;
    if(mp <= _mineralStorage)
    {
        p = mp;
    }
    else
    {
        p = _mineralStorage;
    }
    _setMineralStorage(-p);
    return p;
}

void MiningShip::_setMineralStorage(int n)
{
    _mineralStorage += n;
    // a miningShip cannot spend mineral storage, so update stat only when minerals are saved
    if(n > 0)
        _sm.mineralSaved(_team, n);
}

std::ostream& operator<< (std::ostream& os, const MiningShip& t)
{
    os << "MiningShip[" << &t << "]";
    return os;
}

std::string MiningShip::_dump() const
{
    std::ostringstream oss;
    oss << _key << " MiningShip pos=" << xpos() << "x" << ypos() << " angle=" << angle() << " fuel=" << Movable::fuel() << " mineralStorage=" << mineralStorage() << "\n";
    return oss.str();
}
