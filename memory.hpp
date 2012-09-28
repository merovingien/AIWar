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

#ifndef MEMORY_HPP
#define MEMORY_HPP

#include <vector>
#include <iostream>

#include "item.hpp"
#include "playable.hpp"
#include "config.hpp"

namespace aiwar {
    namespace core {

	class Memory : virtual public Item
	{
	public:
	    virtual ~Memory();

	    unsigned int memorySize() const;

	    template<typename T>
	    T getMemory(unsigned int index) const;

	    template<typename T>
	    T getMemory(unsigned int index, const Memory *item) const;

	    template<typename T>
	    void setMemory(unsigned int index, T value);

	    template<typename T>
	    void setMemory(unsigned int index, T value, Memory *item);

	protected:
	    typedef union {
		int i;
		unsigned int u;
		float f;
	    } MemorySlot;

	    Memory(ItemManager& im, Key k, unsigned int size);

	    std::vector<MemorySlot> _memory;
	};


// template implementation


	template<typename T>
	T Memory::getMemory(unsigned int index, const Memory *other) const
	{
	    // check distance to the other item
	    if(distanceTo(other) > COMMUNICATION_RADIUS)
	    {
		std::cout << "Memory: other item is too far to communicate" << std::endl;
		return T();
	    }

	    // manage playability : if we are a Playable item, we check if the other item is also a playable item. If it is the case, we check if the other item is a friend. Else we do not exchange information. If we are not a Playable item, we do no other check and we accept the exchange.

	    const Playable *self = dynamic_cast<const Playable*>(this);
	    if(self)
	    {
		const Playable *o = dynamic_cast<const Playable*>(other);
		if(o)
		{
		    if(!self->isFriend(o))
		    {
			std::cerr << "Memory::getMemory: item is not a friend" << std::endl;
			return T();
		    }
		}
		else
		{
		    std::cerr << "Memory::getMemory: item is not Playable" << std::endl;
		}
	    }
    
	    return other->getMemory<T>(index);
	}

	template<typename T>
	void Memory::setMemory(unsigned int index, T value, Memory *other)
	{
	    // check distance to the other item
	    if(distanceTo(other) > COMMUNICATION_RADIUS)
	    {
		std::cout << "Memory: other item is too far to communicate" << std::endl;
		return;
	    }

	    // manage playability : if we are a Playable item, we check if the other item is also a playable item. If it is the case, we check if the other item is a friend. Else we do not exchange information. If we are not a Playable item, we do no other check and we accept the exchange.

	    Playable *self = dynamic_cast<Playable*>(this);
	    if(self)
	    {
		Playable *o = dynamic_cast<Playable*>(other);
		if(o)
		{
		    if(!self->isFriend(o))
		    {
			std::cerr << "Memory::setMemory: item is not a friend" << std::endl;
			return;
		    }
		}
	    }
    
	    other->setMemory<T>(index, value);
	}

    } /* namespace aiwar::core */
} /* namespace aiwar */

#endif /* MEMORY_HPP */
