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

#ifndef BASE_HPP
#define BASE_HPP

#include <ostream>

#include "item.hpp"
#include "living.hpp"
#include "playable.hpp"
#include "memory.hpp"

namespace aiwar {
    namespace core {

	class ItemManager;
	class MiningShip;
	class Movable;
	class Fighter;

	class Base : virtual public Item, public Living, public Playable, public Memory
	{
	public:
	    Base(ItemManager* im, double xpos, double ypos, Team team, PlayFunction& pf);
	    ~Base();

	    void update(unsigned int tick);

	    /**
	     * \brief Launch a missile to the target
	     * \param target The targetted item. Take care that it can be a friend or a mineral.
	     *
	     * The missile is launch only if the base has enough mineral points to create it. Mineral points are consumed
	     */
	    void launchMissile(Living* target);
    
	    void createMiningShip();
    
	    /**
	     * \brief Get the current number of mineral points stored in the base.
	     * \return The current number of mineral points stored in the base.
	     */
	    unsigned int mineralStorage() const;
   
	    /**
	     * \brief Get mineral points from a MiningShip of the same team
	     * \return The number of mineral points taken from the MiningShip
	     */
	    unsigned int pullMineral(MiningShip* ship, unsigned int mineralPoints);
    
	    /**
	     * \brief Repair itself by converting mineralPoint in lifePoint
	     * \param points Number of point to convert
	     * \return Number of point actually converted
	     *
	     * The base cannot have more the BASE_MAX_LIFE and cannot convert more than its current mineral storage capacity.
	     */
	    unsigned int repair(unsigned int points);

	    /**
	     * \brief Repair a friend
	     * \param points Number of points to convert
	     * \param item Item to repair
	     * \return Number of point actually converted
	     *
	     * The base cannot push more than the max live point of item and cannot convert more than its current mineral storage capacity.
	     */
	    unsigned int repair(unsigned int points, Living *item);

	    /**
	     * \brief Fuel a friend
	     * \param points Number of points to convert
	     * \param item Item to refuel
	     * \return Number of points actually converted
	     *
	     * The base converts its mineral points to fuel. The base cannot push more than the max fuel capacity of the item and cannot convert more than its own mineral storage.
	     */
	    unsigned int refuel(unsigned int points, Movable *item);

	    void createFighter();

	    unsigned int giveMissiles(unsigned int nb, Fighter* fighter);

	private:
	    void _preUpdate(unsigned int tick);
	    
	    ItemManager* _im;

	    unsigned int _mineralStorage;
	    bool _hasLaunch;
	};

    } // namespace aiwar::core
} // namespace aiwar

std::ostream& operator<< (std::ostream& os, const aiwar::core::Base& b);

#endif /* BASE_HPP */
