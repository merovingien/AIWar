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

#ifndef PLAYABLE_HPP
#define PLAYABLE_HPP

#include <sstream>

#include "config.hpp" // for Team
#include "item.hpp"

namespace aiwar {
    namespace core {

        class Movable;
        class Playable;

        enum State
        {
            DEFAULT,
            LIGHT,
            DARK
        };

        class PlayFunction
        {
        public:
            PlayFunction() {}
            virtual ~PlayFunction() {}
            virtual void operator()(Playable*) = 0;

        private:
            PlayFunction(const PlayFunction&);
            PlayFunction& operator=(const PlayFunction&);
        };

        class DefaultPlayFunction : public PlayFunction
        {
        public:
            DefaultPlayFunction(void (*pf)(Playable*)) : _fun_ptr(pf) {}
            void operator()(Playable* p) { if(_fun_ptr) _fun_ptr(p); }

        private:
            void (*_fun_ptr)(Playable*);
        };

        class Playable : virtual public Item
        {
        public:
            static DefaultPlayFunction playNoOp;

            virtual ~Playable();

            Team team() const;
            bool isFriend(const Playable* p) const;

            /**
             * \brief Query remaining fuel of friend
             * \param other A Movable friend
             * \return The remaining fuel of a friend
             *
             * To query fuel, the friend must be in the communication radius.
             */
            unsigned int fuel(const Movable* other) const;

            void log(const std::string &msg);
            std::string getLog() const;

            void state(State state);
            State getState() const;

        protected:
            Playable(GameManager& gm, Key k, Team team, PlayFunction& play);

            void _preUpdate(unsigned long ticks);

            Team _team;
            PlayFunction& _play;
            std::ostringstream _log;
            State _state;
        };


    } /* namespace aiwar::core */
} /* namespace aiwar */

#endif /* PLAYABLE_HPP */
