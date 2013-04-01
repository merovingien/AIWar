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

#include <list>

#include "item_manager.hpp" // for ItemManager::ItemMap

namespace aiwar {
    namespace core {

        class GameManager;
        class StatManager;

        /**
         * \brief Abstract base class for all items on the plate
         */
        class Item
        {
        public:
            typedef std::list<Item*> ItemList;
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
            ItemList neighbours() const;

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

            double _xSize() const;
            double _ySize() const;

            /**
             * \brief Dump the object state and memory
             * \return A string describing the object state
             */
            virtual std::string _dump() const = 0;

        protected:
            Item(GameManager &gm, Key k, double px = 0.0, double py = 0.0, double sx = 0.0, double sy = 0.0, double detection = 0.0);

            ItemManager &_im;
            StatManager &_sm;
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

std::ostream& operator<< (std::ostream& os, const aiwar::core::Item&);

#endif /* ITEM_HPP */
