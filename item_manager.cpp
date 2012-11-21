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

#include "item_manager.hpp"

#include "item.hpp"
#include "living.hpp"
#include "missile.hpp"
#include "base.hpp"
#include "miningship.hpp"
#include "mineral.hpp"
#include "fighter.hpp"

#include "game_manager.hpp"
#include "stat_manager.hpp"

#include <stdexcept>
#include <cstdlib>
#include <tinyxml.h>


using namespace aiwar::core;

ItemManager::ItemManager(GameManager& gm) : _gm(gm), _currentItemId(0)
{
    // offset is between 1 and 50000 included
    _xOffset = static_cast<double>(std::rand() % 50000) + 1.0;
    _yOffset = static_cast<double>(std::rand() % 50000) + 1.0;

    std::cout << "ItemManager: position offset: " << _xOffset << "x" << _yOffset << "\n";
}

ItemManager::~ItemManager()
{
    ItemMap::iterator it;
    // delete all items
    for(it = _itemMap.begin() ; it != _itemMap.end() ; ++it)
    {
        delete it->second;
    }
}

bool ItemManager::init()
{
    std::cout << "ItemManager: Loading the map... ";
    if(!this->loadMap(Config::instance().mapFile))
    {
        std::cerr << "Error while loading map file\n";
        return false;
    }
    std::cout << "Done\n";
    return true;
}

void ItemManager::update(unsigned int tick)
{
    ItemMap::iterator it, tmp;
    Item* i;
    // update all items if not to remove
    for(it = _itemMap.begin() ; it != _itemMap.end() ; ++it)
    {
        i = it->second;
        if(!i->_toRemove())
            i->update(tick);
    }

    // remove some items
    for(it = _itemMap.begin() ; it != _itemMap.end() ; )
    {
        // keep trace of the current iterator *before* increment
        tmp = it++;

        i = tmp->second;
        if(i->_toRemove())
        {
            _gm.getStatManager().itemDestroyed(i);
            delete i;
            _itemMap.erase(tmp);  // this unvalidates tmp, but 'it' has been updated before
        }
    }
}

Missile* ItemManager::createMissile(Item* launcher, Living* target)
{
    ItemKey k = _getNextItemKey();
    Missile *m = new Missile(_gm, k, launcher->xpos(), launcher->ypos(), target);
    _itemMap.insert(ItemMap::value_type(k, m));
    _gm.getStatManager().missileCreated(m);
    /* How can I do this ? But warning, because this function is called when launching missile already bought !
    _gm.mineralSpent(launcher->team(), Config::instance().BASE_MISSILE_PRICE);*/
    return m;
}

Base* ItemManager::createBase(double px, double py, Team team)
{
    ItemKey k = _getNextItemKey();
    Base *b = new Base(_gm, k, px, py, team, _gm.getBasePF(team));
    _itemMap.insert(ItemMap::value_type(k, b));
    _gm.getStatManager().baseCreated(b);
    /* Need the price of base !
    _gm.mineralSpent(team, Config::instance().BASE_CreateBase_PRICE);*/
    return b;
}

MiningShip* ItemManager::createMiningShip(double px, double py, Team team)
{
    ItemKey k = _getNextItemKey();
    MiningShip *t = new MiningShip(_gm, k, px, py, team, _gm.getMiningShipPF(team));
    _itemMap.insert(ItemMap::value_type(k, t));
    _gm.getStatManager().miningShipCreated(t);
    _gm.getStatManager().mineralSpent(team, Config::instance().BASE_MININGSHIP_PRICE);
    return t;
}

MiningShip* ItemManager::createMiningShip(Base* base)
{
    return createMiningShip(base->xpos(), base->ypos(), base->team());
}

Mineral* ItemManager::createMineral(double px, double py)
{
    ItemKey k = _getNextItemKey();
    Mineral *m = new Mineral(_gm, k, px, py);
    _itemMap.insert(ItemMap::value_type(k, m));
    _gm.getStatManager().mineralCreated(m);
    return m;
}

Fighter* ItemManager::createFighter(double px, double py, Team team)
{
    ItemKey k = _getNextItemKey();
    Fighter *f = new Fighter(_gm, k, px, py, team, _gm.getFighterPF(team));
    _itemMap.insert(ItemMap::value_type(k, f));
    _gm.getStatManager().fighterCreated(f);
    _gm.getStatManager().mineralSpent(team, Config::instance().BASE_FIGHTER_PRICE);
    return f;
}

Fighter* ItemManager::createFighter(Base *base)
{
    return createFighter(base->xpos(), base->ypos(), base->team());
}

bool ItemManager::exists(ItemKey key) const
{
    return (get(key) != NULL);
}

Item* ItemManager::get(ItemKey key) const
{
    ItemMap::const_iterator cit = _itemMap.find(key);
    if(cit != _itemMap.end())
        return cit->second;
    else
        return NULL;
}

void ItemManager::applyOffset(double &px, double &py) const
{
    px += _xOffset;
    py += _yOffset;
}

void ItemManager::undoOffset(double &px, double &py) const
{
    px -= _xOffset;
    py -= _yOffset;
}

ItemManager::ItemMap::const_iterator ItemManager::begin() const
{
    return _itemMap.begin();
}

ItemManager::ItemMap::const_iterator ItemManager::end() const
{
    return _itemMap.end();
}

ItemManager::ItemKey ItemManager::_getNextItemKey()
{
    ItemKey k = _currentItemId++;
    return k;
}

bool ItemManager::loadMap(const std::string& mapFile)
{
    TiXmlDocument doc(mapFile.c_str());
    if(!doc.LoadFile())
    {
        std::cerr << "Cannot load map file: \"" << mapFile << "\"\n";
        return false;
    }

    TiXmlElement *pRoot, *pElem;

    // root: items
    pRoot = doc.RootElement();
    if(!pRoot || pRoot->ValueStr() != "items")
    {
        std::cerr << "Parse error - Bad root element tag, must be \"items\"\n";
        return false;
    }

    // read all items
    std::string stype, steam;
    double x, y;
    Team team;
    pElem = 0;
    for(pElem=pRoot->FirstChildElement("item") ; pElem ; pElem=pElem->NextSiblingElement("item"))
    {
        if(pElem->QueryDoubleAttribute("x", &x) != TIXML_SUCCESS)
        {
            std::cerr << "Parse error - No or bad \"x\" attribute\n";
            return false;
        }

        if(pElem->QueryDoubleAttribute("y", &y) != TIXML_SUCCESS)
        {
            std::cerr << "Parse error - No or bad \"y\" attribute\n";
            return false;
        }

        if(pElem->QueryStringAttribute("type", &stype) != TIXML_SUCCESS)
        {
            std::cerr << "Parse error - No \"type\" attribute\n";
            return false;
        }

        applyOffset(x, y);

        if(stype == "MINERAL")
        {
            // load a mineral
            createMineral(x, y);
        }
        else if(stype == "BASE" || stype == "MININGSHIP" || stype == "FIGHTER")
        {
            // get team
            if(pElem->QueryStringAttribute("team", &steam) != TIXML_SUCCESS)
            {
                std::cerr << "Parse error - No \"team\" attribute\n";
                return false;
            }
            if(steam == "BLUE")
                team = BLUE_TEAM;
            else if(steam == "RED")
                team = RED_TEAM;
            else
            {
                std::cerr << "Parse error - Bad \"team\" attribute\n";
                return false;
            }

            if(stype == "BASE")
                createBase(x, y, team);
            else if(stype == "MININGSHIP")
                createMiningShip(x, y, team);
            else
                createFighter(x, y, team);
        }
    }

    return true;
}
