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

#include "memory.hpp"

#include <iostream>
#include <stdexcept>
#include <cassert>

using namespace aiwar::core;

Memory::Memory(unsigned int size) : _memory(size)
{
//    std::cout << "sizeof MemorySlot: " << sizeof(MemorySlot) << std::endl;
    assert(sizeof(MemorySlot) == 4); // check size of MemorySlot -> must be 32 bits
}

Memory::~Memory()
{
}

unsigned int Memory::memorySize() const
{
    return _memory.size();
}

namespace aiwar {
    namespace core {

	template<>
	void Memory::setMemory(unsigned int index, int value)
	{
	    try
	    {
		_memory.at(index).i = value;
	    }
	    catch(const std::out_of_range &)
	    {
	    }
	}

	template<>
	void Memory::setMemory(unsigned int index, unsigned int value)
	{
	    try
	    {
		_memory.at(index).u = value;
	    }
	    catch(const std::out_of_range &)
	    {
	    }
	}

	template<>
	void Memory::setMemory(unsigned int index, float value)
	{
	    try
	    {
		_memory.at(index).f = value;
	    }
	    catch(const std::out_of_range &)
	    {
	    }
	}

	template<>
	int Memory::getMemory(unsigned int index) const
	{
	    try
	    {
		return _memory.at(index).i;
	    }
	    catch(const std::out_of_range &)
	    {
		return 0;
	    }
	}

	template<>
	unsigned int Memory::getMemory(unsigned int index) const
	{
	    try
	    {
		return _memory.at(index).u;
	    }
	    catch(const std::out_of_range &)
	    {
		return 0u;
	    }
	}

	template<>
	float Memory::getMemory(unsigned int index) const
	{
	    try
	    {
		return _memory.at(index).f;
	    }
	    catch(const std::out_of_range &)
	    {
		return 0.0f;
	    }
	}

    } /* namespace aiwar::core */
} /* namespace aiwar */
