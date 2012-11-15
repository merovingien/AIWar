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

#ifndef PYTHON_WRAPPER_HPP
#define PYTHON_WRAPPER_HPP

#include <Python.h>

#include "miningship.hpp"
#include "missile.hpp"
#include "mineral.hpp"
#include "base.hpp"
#include "fighter.hpp"

// initialize the interpreter: add "." to sys.path
bool initPythonInterpreter(int argc, char* argv[]);

// initialize the aiwar module and MiningShip type
bool initAiwarModule();

// return a New Reference of MiningShip python object
PyObject* MiningShip_New(aiwar::core::MiningShip *m);

// return a New Reference of MiningShipConst python object
PyObject* MiningShipConst_New(aiwar::core::MiningShip *m);

// return a New Reference of Mineral python object
PyObject* Mineral_New(aiwar::core::Mineral *m);

// return a New Reference of Missile python object
PyObject* Missile_New(aiwar::core::Missile *m);

// return a New Reference of Base python object
PyObject* Base_New(aiwar::core::Base *m);

// return a New Reference of BaseConst python object
PyObject* BaseConst_New(aiwar::core::Base *m);

// return a New Reference of Fighter python object
PyObject* Fighter_New(aiwar::core::Fighter *m);

// return a New Reference of FighterConst python object
PyObject* FighterConst_New(aiwar::core::Fighter *m);

#endif /* PYTHON_WRAPPER_HPP */
