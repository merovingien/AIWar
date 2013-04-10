/*
 * Copyright (C) 2012, 2013 Paul Grégoire
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

#ifndef MINERAL_HPP
#define MINERAL_HPP

#include "item.hpp"
#include "living.hpp"

namespace aiwar {
    namespace core {

        class Mineral : virtual public Item, public Living
        {
        public:
            Mineral(GameManager& gm, Key k, double px, double py);

            void update(unsigned int tick);

            std::string _dump() const;
        };

    } // namespace aiwar::core
} // namespace aiwar

#endif /* MINERAL_HPP */
