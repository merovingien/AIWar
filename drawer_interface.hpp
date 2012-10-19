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

#ifndef DRAWER_INTERFACE_HPP
#define DRAWER_INTERFACE_HPP

#include "item_manager.hpp"
#include "game_manager.hpp"

namespace aiwar {
    namespace renderer {

	/**
	 * \brief Interface for all drawer objects
	 */
	class DrawerInterface
	{
	public:
	    virtual ~DrawerInterface() {}

	    virtual std::string getName() const = 0;
	    virtual std::string getVersion() const = 0;

	    /**
	     * \brief Called by the core manager to initialize the drawer object
	     * \param params A string containg drawer parameters
	     * \return True if initialization succeeded
	     */
	    virtual bool initialize(const std::string& params) = 0;
	    
	    /**
	     * \brief Finalize the drawer object
	     * \return True if the drawer ended successfully
	     *
	     * This method must not block. If implementation has to do something special
	     * at the end of a battle, it can be done in the draw function when the
	     * gameover flag is set.
	     */
	    virtual bool finalize() = 0;

	    /**
	     * \brief Draw each item
	     * \param cit an iterator on all the item
	     * \param stat a statistic object giving global information about the battle
	     * \param gameover True if game is over
	     *
	     * The cit iterator is pointing on the first item. Drawing object must not use
	     * the iterator outside of this function, because it will be certainlly
	     * invalidated just after this function returns. The same applies for stat object.
	     * If gameover is true, this is the last call to the draw manager update. When 
	     * the function return, the core manager will clean and exit the game (or start
	     * a new battle, if it is implemented).
	     */
	    virtual void draw(const aiwar::core::ItemManager::ItemMap::const_iterator &cit,
			      const aiwar::core::GameManager::Stat &stats,
			      bool gameover) = 0;
	};

    } // aiwar::renderer
} // aiwar


/**
 * \brief Get the drawer implemented by the shared object
 * \return the drawer object
 */
extern "C" aiwar::renderer::DrawerInterface* getDrawer();

#endif /* DRAWER_INTERFACE_HPP */
