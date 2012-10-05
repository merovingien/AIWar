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

#ifndef ITEM_MANAGER_HPP
#define ITEM_MANAGER_HPP

#include <set>
#include <map>

#include "config.hpp" // for Team

namespace aiwar {
    namespace core {

	class Item;
	class Living;
	class Missile;
	class Base;
	class MiningShip;
	class Mineral;
	class Fighter;

	class GameManager;


	class ItemManager
	{
	public:
	    typedef unsigned long ItemKey;
	    typedef std::map<ItemKey, Item*> ItemMap;

	    ItemManager(GameManager& gm);
	    ~ItemManager();

	    void update(unsigned int tick);

	    Missile* createMissile(Item* launcher, Living* target);
	    Base* createBase(double px, double py, Team team);
	    MiningShip* createMiningShip(double px, double py, Team team);  // for debug only
	    MiningShip* createMiningShip(Base* base);
	    Mineral* createMineral(double px, double py);
	    Fighter* createFighter(double px, double py, Team team);
	    Fighter* createFighter(Base* base);

	    bool exists(ItemKey key) const;
	    Item* get(ItemKey key) const;
	    ItemMap::const_iterator begin() const;
	    ItemMap::const_iterator end() const;
	        
	    bool loadMap(const std::string& mapFile);

	private:
	    // no copy
	    ItemManager(const ItemManager&);
	    ItemManager& operator=(const ItemManager&);

	    ItemKey _getNextItemKey();
    
	    GameManager& _gm;
	    ItemKey _currentItemId;
	    ItemMap _itemMap;
	};

    } // namespace aiwar::core
} // namespace aiwar

#endif /* ITEM_MANAGER_HPP */
