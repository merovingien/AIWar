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

#ifndef ITEM_HPP
#define ITEM_HPP

#include <set>

#include "item_manager.hpp" // for ItemManager::ItemMap

namespace aiwar {
    namespace core {

        /**
	 * \brief Abstract base class for all items on the plate
	 */
	class Item
	{
	public:
	    typedef std::set<Item*> ItemSet;
	    typedef ItemManager::ItemKey Key;

	    virtual ~Item();

	    /**
	     * \brief Update the item at each step.
	     * \param tick The current step.
	     */
	    virtual void update(unsigned int tick) = 0;

	    double xpos() const;
	    double ypos() const;

	    /**
	     * \brief return item nearer than _vision from itself, itself excluded
	     */
	    ItemSet neighbours() const;

	    /**
	     * \brief Get the distance to the other item.
	     * \param other The other item
	     * \return The distance between this item and other.
	     */
	    double distanceTo(const Item *other) const;

	    /**
	     * \brief Get the distance to a point.
	     * \param px x position
	     * \param py y position
	     * \return The distance to the point(px,py)
	     */
	    double distanceTo(double px, double py) const;

	    /**
	     * \brief Intern method. Return true if the item must be removed
	     * \return True if the item must be removed
	     */
	    bool _toRemove() const;

	    Key _getKey() const;

	protected:
	    Item(ItemManager &im, Key k, double px = 0.0, double py = 0.0, double sx = 0.0, double sy = 0.0, double detection = 0.0);

	    ItemManager &_im;
	    const Key _key;

	    bool _toRemoveFlag; ///< set to true when the item must be deleted by the game manager

	    double _xpos; ///< horizontal Position
	    double _ypos; ///< vertical Position

	    double _xsize; ///< horizontal size
	    double _ysize; ///< vertical size

	    double _detection_radius; ///< radius of vision for the item

	private:
	    // no copy
	    Item(const Item&);
	    Item& operator= (const Item&);
	};

    } // namespace aiwar::core
} // namespace aiwar

#endif /* ITEM_HPP */
