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

#ifndef LIVING_HPP
#define LIVING_HPP

#include "item.hpp"

namespace aiwar {
    namespace core {

        class Living : virtual public Item
        {
        public:

            virtual ~Living();

            /**
             * \brief Get the current number of life points
             * \return The current number of life points
             */
            unsigned int life() const;

            /**
             * \brief Take some life points
             * \param value Number of life point to remove
             * \param kill If true, the item is mark to be removed if life reached zero.
             * \return Number of life point finally removed
             * \warning Internal use only
             *
             * If the number of life points reaches zero, the object deads
             */
            unsigned int _takeLife(unsigned int value, bool kill = true);

            /**
             * \brief Put some life points
             * \param value Number of life points to add
             * \return Number of life points finally added.
             * \warning Internal use only
             *
             * The number of lifePoint cannot exceed _maxLife.
             */
            unsigned int _putLife(unsigned int value);

        protected:
            Living(ItemManager& im, Key k);
            Living(ItemManager& im, Key k, unsigned int life, unsigned int maxLife);

            bool _isDead() const;

            unsigned int _maxLife;
            unsigned int _life;
        };

    } // namespace aiwar::core
} // namespace aiwar

#endif /* LIVING_HPP */
