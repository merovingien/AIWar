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

#ifndef MOVABLE_HPP
#define MOVABLE_HPP

#include "item.hpp"

namespace aiwar {
    namespace core {

        class Movable : virtual public Item
        {
        public:
            virtual ~Movable();

            void rotateOf(double angle);
            void rotateTo(const Item *target);
            void rotateTo(double px, double py);

            void move();

            double angle() const;
//            double xdest() const;
//            double ydest() const;

            unsigned int fuel() const;

            unsigned int _putFuel(unsigned int points);

        protected:
            Movable(GameManager& gm, Key k, double speed = 0.0, unsigned int startFuel = 0, unsigned int maxFuel = 0, unsigned int moveConso = 0, double angle = 0.0);

            /**
             * \brief Initialize the movement
             *
             * Reset _hasMove and destination
             */
            void _preUpdate(unsigned int tick);

            /**
             * \brief Do some checks and actions before moving.
             *
             * If the function return true, the move is done, else nothing happened.
             * Default implementation tries to consume _moveConso fuel and returns true if it is possible, false otherwise.
             *
             * \return true to indicate that the move is authorized, false to forbid the move
             */
            virtual bool doMove();

            double _speed; ///< speed of the item
            double _angle; ///< direction, in degree, use trigonometric system
            unsigned int _fuel; ///< fuel quantity
            unsigned int _maxFuel; ///< capacity of the fuel tank
            unsigned int _moveConso; ///< fuel consumption per move

        private:
            double _hasMoved; ///< true if a move has been done for the current step
        };

    } // namespace aiwar::core
} // namespace aiwar

#endif /* MOVABLE_HPP */
