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

#include <Python.h>
#include <structmember.h>

#include "python_wrapper.hpp"

#include "config.hpp"

/*** Generic Item Object ***/

typedef struct {
    PyObject_HEAD
    aiwar::core::Item* item;
} Item;

// global tuple with all PyTypeObject based on Item
static PyObject* pItemBasedTuple = NULL;

static void
Item_dealloc(Item* self)
{
//    self->ob_type->tp_free((PyObject*)self);  -> replace by:
    PyObject_Del(self);
}

static int
Item_init(Item *self, PyObject * /*args*/, PyObject * /*kwds*/)
{
    std::string msg = "Creating new ";
    msg.append(self->ob_type->tp_name).append(" object is forbidden");
    PyErr_SetString(PyExc_RuntimeError, msg.c_str());
    return -1;
}

static PyObject * Item_pos(Item* self); // Item
static PyObject * Item_neighbours(Item* self); // Item
static PyObject * Item_distanceTo(Item* self, PyObject *args); // Item
static PyObject * Item_rotateOf(Item* self, PyObject *args); // Movable
static PyObject * Item_rotateTo(Item* self, PyObject *args); // Movable
static PyObject * Item_angle(Item* self); // Movable
static PyObject * Item_fuel(Item* self); // Movable
static PyObject * Item_move(Item* self); // Movable
static PyObject * Item_life(Item* self); // Living
static PyObject * Item_team(Item* self); // Playable
static PyObject * Item_isFriend(Item* self, PyObject *args); // Playable
static PyObject * Item_log(Item* self, PyObject *args); // Playable
static PyObject * Item_memorySize(Item* self); // Memory
static PyObject * Item_getMemoryInt(Item* self, PyObject *args); // Memory
static PyObject * Item_getMemoryUInt(Item* self, PyObject *args); // Memory
static PyObject * Item_getMemoryFloat(Item* self, PyObject *args); // Memory
static PyObject * Item_setMemoryInt(Item* self, PyObject *args); // Memory
static PyObject * Item_setMemoryUInt(Item* self, PyObject *args); // Memory
static PyObject * Item_setMemoryFloat(Item* self, PyObject *args); // Memory
static PyObject * MiningShip_extract(Item* self, PyObject *args); // MiningShip
static PyObject * MiningShip_mineralStorage(Item* self); // MiningShip
static PyObject * MiningShip_pushMineral(Item* self, PyObject *args); // MiningShip
static PyObject * Base_mineralStorage(Item* self); // Base
static PyObject * Base_pullMineral(Item* self, PyObject *args); // Base
static PyObject * Base_launchMissile(Item* self, PyObject *args); // Base
static PyObject * Base_createMiningShip(Item* self); // Base
static PyObject * Base_repair(Item* self, PyObject *args); // Base
static PyObject * Base_refuel(Item* self, PyObject *args); // Base
static PyObject * Base_createFighter(Item* self); // Base
static PyObject * Base_giveMissiles(Item* self, PyObject *args); // Base
static PyObject * Fighter_missiles(Item* self); // Fighter
static PyObject * Fighter_launchMissile(Item* self, PyObject *args); // Fighter

/*************** MiningShip object **************/

static PyMemberDef MiningShip_members[] = {
    {NULL, 0, 0, 0, NULL} /* Sentinel */
};

static PyMethodDef MiningShip_methods[] = {
    {"pos", (PyCFunction)Item_pos, METH_NOARGS, "Return the position of the item"},
    {"neighbours", (PyCFunction)Item_neighbours, METH_NOARGS, "Return the neighbours of the item"},
    {"distanceTo", (PyCFunction)Item_distanceTo, METH_VARARGS, "Return the distance to the other item or a point"},
    {"rotateOf", (PyCFunction)Item_rotateOf, METH_VARARGS, "Rotate the movable item of the given angle"},
    {"rotateTo", (PyCFunction)Item_rotateTo, METH_VARARGS, "Rotate the movable item in the direction of the other item"},
    {"angle", (PyCFunction)Item_angle, METH_NOARGS, "Return the current angle of the ship"},
    {"fuel", (PyCFunction)Item_fuel, METH_NOARGS, "Return the current fuel of the ship"},
    {"move", (PyCFunction)Item_move, METH_NOARGS, "Move the movable item in the direction given by its angle"},
    {"life", (PyCFunction)Item_life, METH_NOARGS, "Return the remaining life of the item"},
    {"team", (PyCFunction)Item_team, METH_NOARGS, "Return the team of the item"},
    {"isFriend", (PyCFunction)Item_isFriend, METH_VARARGS, "Return true if the given item belong to the same team"},
    {"log", (PyCFunction)Item_log, METH_VARARGS, "Log the message"},
    {"memorySize", (PyCFunction)Item_memorySize, METH_NOARGS, "Return the number of memory slots allocated to the item"},
    {"getMemoryInt", (PyCFunction)Item_getMemoryInt, METH_VARARGS, "Return the memory contained at position 'index' as an int value"},
    {"getMemoryUInt", (PyCFunction)Item_getMemoryUInt, METH_VARARGS, "Return the memory contained at position 'index' as an unsigned int value"},
    {"getMemoryFloat", (PyCFunction)Item_getMemoryFloat, METH_VARARGS, "Return the memory contained at position 'index' as a float value"},
    {"setMemoryInt", (PyCFunction)Item_setMemoryInt, METH_VARARGS, "Set the memory at position 'index' with 'value' as an int"},
    {"setMemoryUInt", (PyCFunction)Item_setMemoryUInt, METH_VARARGS, "Set the memory at position 'index' with 'value' as an unsigned int"},
    {"setMemoryFloat", (PyCFunction)Item_setMemoryFloat, METH_VARARGS, "Set the memory at position 'index' with 'value' as a float"},
    {"extract", (PyCFunction)MiningShip_extract, METH_VARARGS, "Extract mineral points from a Mineral item"},
    {"mineralStorage", (PyCFunction)MiningShip_mineralStorage, METH_NOARGS, "Return the number of mineral points contained in the ship"},
    {"pushMineral", (PyCFunction)MiningShip_pushMineral, METH_VARARGS, "Push Mineral points to a friend Base"},
    {NULL, NULL, 0, NULL} /* Sentinel */
};

static PyTypeObject MiningShipType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "aiwar.PlayableMiningShip",/*tp_name*/
    sizeof(Item),              /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)Item_dealloc,  /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT,        /*tp_flags*/
    "Playable MiningShip objects",/* tp_doc */
    0,                         /* tp_traverse */
    0,                         /* tp_clear */
    0,                         /* tp_richcompare */
    0,                         /* tp_weaklistoffset */
    0,                         /* tp_iter */
    0,                         /* tp_iternext */
    MiningShip_methods,        /* tp_methods */
    MiningShip_members,        /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)Item_init,       /* tp_init */
    0,                         /* tp_alloc */
    0,                         /* tp_new */
    0,                         /* tp_free */
    0,                         /* tp_is_gc */
    0,                         /* tp_bases */
    0,                         /* tp_mro */
    0,                         /* tp_cache */
    0,                         /* tp_subclasses */
    0,                         /* tp_weaklist */
    0,                         /* tp_del */
    0,                         /* tp_version_tag */
};

PyObject* MiningShip_New(aiwar::core::MiningShip *m)
{
    Item *pM = PyObject_New(Item, &MiningShipType);
    if(!pM)
    {
        std::cerr << "Error while creating new MiningShip python object" << std::endl;
        return NULL;
    }

    pM->item = m;
    return (PyObject*)pM;
}

/*************** MiningShipConst object **************/

static PyMemberDef MiningShipConst_members[] = {
    {NULL, 0, 0, 0, NULL} /* Sentinel */
};

static PyMethodDef MiningShipConst_methods[] = {
    {"pos", (PyCFunction)Item_pos, METH_NOARGS, "Return the position of the item"},
    {"angle", (PyCFunction)Item_angle, METH_NOARGS, "Return the current angle of the ship"},
    {"life", (PyCFunction)Item_life, METH_NOARGS, "Return the remaining life of the item"},
    {NULL, NULL, 0, NULL} /* Sentinel */
};

static PyTypeObject MiningShipConstType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "aiwar.MiningShip",        /*tp_name*/
    sizeof(Item),              /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)Item_dealloc,  /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT,        /*tp_flags*/
    "Const MiningShip objects",/* tp_doc */
    0,                         /* tp_traverse */
    0,                         /* tp_clear */
    0,                         /* tp_richcompare */
    0,                         /* tp_weaklistoffset */
    0,                         /* tp_iter */
    0,                         /* tp_iternext */
    MiningShipConst_methods,   /* tp_methods */
    MiningShipConst_members,   /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)Item_init,       /* tp_init */
    0,                         /* tp_alloc */
    0,                         /* tp_new */
    0,                         /* tp_free */
    0,                         /* tp_is_gc */
    0,                         /* tp_bases */
    0,                         /* tp_mro */
    0,                         /* tp_cache */
    0,                         /* tp_subclasses */
    0,                         /* tp_weaklist */
    0,                         /* tp_del */
    0,                         /* tp_version_tag */
};

PyObject* MiningShipConst_New(aiwar::core::MiningShip *m)
{
    Item *pM = PyObject_New(Item, &MiningShipConstType);
    if(!pM)
    {
        std::cerr << "Error while creating new MiningShipConst python object" << std::endl;
        return NULL;
    }

    pM->item = m;
    return (PyObject*)pM;
}


/*************** Mineral object **************/

static PyMemberDef Mineral_members[] = {
    {NULL, 0, 0, 0, NULL} /* Sentinel */
};

static PyMethodDef Mineral_methods[] = {
    {"pos", (PyCFunction)Item_pos, METH_NOARGS, "Return the position of the item"},
    {"life", (PyCFunction)Item_life, METH_NOARGS, "Return the remaining mineral points of the Mineral"},
    {NULL, NULL, 0, NULL} /* Sentinel */
};

static PyTypeObject MineralType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "aiwar.Mineral",           /*tp_name*/
    sizeof(Item),              /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)Item_dealloc,  /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT,        /*tp_flags*/
    "Mineral objects",         /* tp_doc */
    0,                         /* tp_traverse */
    0,                         /* tp_clear */
    0,                         /* tp_richcompare */
    0,                         /* tp_weaklistoffset */
    0,                         /* tp_iter */
    0,                         /* tp_iternext */
    Mineral_methods,           /* tp_methods */
    Mineral_members,           /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)Item_init,       /* tp_init */
    0,                         /* tp_alloc */
    0,                         /* tp_new */
    0,                         /* tp_free */
    0,                         /* tp_is_gc */
    0,                         /* tp_bases */
    0,                         /* tp_mro */
    0,                         /* tp_cache */
    0,                         /* tp_subclasses */
    0,                         /* tp_weaklist */
    0,                         /* tp_del */
    0,                         /* tp_version_tag */
};

PyObject* Mineral_New(aiwar::core::Mineral *m)
{
    Item *pM = PyObject_New(Item, &MineralType);
    if(!pM)
    {
        std::cerr << "Error while creating new Mineral python object" << std::endl;
        return NULL;
    }

    pM->item = m;
    return (PyObject*)pM;
}

/*************** Missile object **************/

static PyMemberDef Missile_members[] = {
    {NULL, 0, 0, 0, NULL} /* Sentinel */
};

static PyMethodDef Missile_methods[] = {
    {"pos", (PyCFunction)Item_pos, METH_NOARGS, "Return the position of the item"},
    {"angle", (PyCFunction)Item_angle, METH_NOARGS, "Return the current angle of the missile"},
    {"life", (PyCFunction)Item_life, METH_NOARGS, "Return the remaining life of the item"},
    {NULL, NULL, 0, NULL} /* Sentinel */
};

static PyTypeObject MissileType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "aiwar.Missile",           /*tp_name*/
    sizeof(Item),              /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)Item_dealloc,  /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT,        /*tp_flags*/
    "Missile objects",         /* tp_doc */
    0,                         /* tp_traverse */
    0,                         /* tp_clear */
    0,                         /* tp_richcompare */
    0,                         /* tp_weaklistoffset */
    0,                         /* tp_iter */
    0,                         /* tp_iternext */
    Missile_methods,           /* tp_methods */
    Missile_members,           /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)Item_init,       /* tp_init */
    0,                         /* tp_alloc */
    0,                         /* tp_new */
    0,                         /* tp_free */
    0,                         /* tp_is_gc */
    0,                         /* tp_bases */
    0,                         /* tp_mro */
    0,                         /* tp_cache */
    0,                         /* tp_subclasses */
    0,                         /* tp_weaklist */
    0,                         /* tp_del */
    0,                         /* tp_version_tag */
};

PyObject* Missile_New(aiwar::core::Missile *m)
{
    Item *pM = PyObject_New(Item, &MissileType);
    if(!pM)
    {
        std::cerr << "Error while creating new Missile python object" << std::endl;
        return NULL;
    }

    pM->item = m;
    return (PyObject*)pM;
}

/*************** Base object **************/

static PyMemberDef Base_members[] = {
    {NULL, 0, 0, 0, NULL} /* Sentinel */
};

static PyMethodDef Base_methods[] = {
    {"pos", (PyCFunction)Item_pos, METH_NOARGS, "Return the position of the item"},
    {"neighbours", (PyCFunction)Item_neighbours, METH_NOARGS, "Return the neighbours of the item"},
    {"distanceTo", (PyCFunction)Item_distanceTo, METH_VARARGS, "Return the distance to the other item or a point"},
    {"life", (PyCFunction)Item_life, METH_NOARGS, "Return the remaining life of the item"},
    {"team", (PyCFunction)Item_team, METH_NOARGS, "Return the team of the item"},
    {"isFriend", (PyCFunction)Item_isFriend, METH_VARARGS, "Return true if the given item belong to the same team"},
    {"log", (PyCFunction)Item_log, METH_VARARGS, "Log the message"},
    {"memorySize", (PyCFunction)Item_memorySize, METH_NOARGS, "Return the number of memory slots allocated to the item"},
    {"getMemoryInt", (PyCFunction)Item_getMemoryInt, METH_VARARGS, "Return the memory contained at position 'index' as an int value"},
    {"getMemoryUInt", (PyCFunction)Item_getMemoryUInt, METH_VARARGS, "Return the memory contained at position 'index' as an unsigned int value"},
    {"getMemoryFloat", (PyCFunction)Item_getMemoryFloat, METH_VARARGS, "Return the memory contained at position 'index' as a float value"},
    {"setMemoryInt", (PyCFunction)Item_setMemoryInt, METH_VARARGS, "Set the memory at position 'index' with 'value' as an int"},
    {"setMemoryUInt", (PyCFunction)Item_setMemoryUInt, METH_VARARGS, "Set the memory at position 'index' with 'value' as an unsigned int"},
    {"setMemoryFloat", (PyCFunction)Item_setMemoryFloat, METH_VARARGS, "Set the memory at position 'index' with 'value' as a float"},
    {"mineralStorage", (PyCFunction)Base_mineralStorage, METH_NOARGS, "Return the number of mineral points contained in the base"},
    {"pullMineral", (PyCFunction)Base_pullMineral, METH_VARARGS, "Pull mineral from a friend MiningShip"},
    {"launchMissile", (PyCFunction)Base_launchMissile, METH_VARARGS, "Launch a Missile to a target"},
    {"createMiningShip", (PyCFunction)Base_createMiningShip, METH_NOARGS, "Create a new MiningShip"},
    {"repair", (PyCFunction)Base_repair, METH_VARARGS, "Repair itself or a friend"},
    {"refuel", (PyCFunction)Base_refuel, METH_VARARGS, "Refuel a friend ship"},
    {"createFighter", (PyCFunction)Base_createFighter, METH_NOARGS, "Create a new Fighter"},
    {"giveMissiles", (PyCFunction)Base_giveMissiles, METH_VARARGS, "Give missiles to a friend Fighter"},
    {NULL, NULL, 0, NULL} /* Sentinel */
};

static PyTypeObject BaseType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "aiwar.PlayableBase",      /*tp_name*/
    sizeof(Item),              /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)Item_dealloc,  /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT,        /*tp_flags*/
    "Playable Base objects",   /* tp_doc */
    0,                         /* tp_traverse */
    0,                         /* tp_clear */
    0,                         /* tp_richcompare */
    0,                         /* tp_weaklistoffset */
    0,                         /* tp_iter */
    0,                         /* tp_iternext */
    Base_methods,              /* tp_methods */
    Base_members,              /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)Item_init,       /* tp_init */
    0,                         /* tp_alloc */
    0,                         /* tp_new */
    0,                         /* tp_free */
    0,                         /* tp_is_gc */
    0,                         /* tp_bases */
    0,                         /* tp_mro */
    0,                         /* tp_cache */
    0,                         /* tp_subclasses */
    0,                         /* tp_weaklist */
    0,                         /* tp_del */
    0,                         /* tp_version_tag */
};

PyObject* Base_New(aiwar::core::Base *m)
{
    Item *pM = PyObject_New(Item, &BaseType);
    if(!pM)
    {
        std::cerr << "Error while creating new Base python object" << std::endl;
        return NULL;
    }

    pM->item = m;
    return (PyObject*)pM;
}

/*************** BaseConst object **************/

static PyMemberDef BaseConst_members[] = {
    {NULL, 0, 0, 0, NULL} /* Sentinel */
};

static PyMethodDef BaseConst_methods[] = {
    {"pos", (PyCFunction)Item_pos, METH_NOARGS, "Return the position of the item"},
    {"life", (PyCFunction)Item_life, METH_NOARGS, "Return the remaining life of the item"},
    {NULL, NULL, 0, NULL} /* Sentinel */
};

static PyTypeObject BaseConstType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "aiwar.Base",              /*tp_name*/
    sizeof(Item),              /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)Item_dealloc,  /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT,        /*tp_flags*/
    "Const Base objects",      /* tp_doc */
    0,                         /* tp_traverse */
    0,                         /* tp_clear */
    0,                         /* tp_richcompare */
    0,                         /* tp_weaklistoffset */
    0,                         /* tp_iter */
    0,                         /* tp_iternext */
    BaseConst_methods,         /* tp_methods */
    BaseConst_members,         /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)Item_init,       /* tp_init */
    0,                         /* tp_alloc */
    0,                         /* tp_new */
    0,                         /* tp_free */
    0,                         /* tp_is_gc */
    0,                         /* tp_bases */
    0,                         /* tp_mro */
    0,                         /* tp_cache */
    0,                         /* tp_subclasses */
    0,                         /* tp_weaklist */
    0,                         /* tp_del */
    0,                         /* tp_version_tag */
};

PyObject* BaseConst_New(aiwar::core::Base *m)
{
    Item *pM = PyObject_New(Item, &BaseConstType);
    if(!pM)
    {
        std::cerr << "Error while creating new BaseConst python object" << std::endl;
        return NULL;
    }

    pM->item = m;
    return (PyObject*)pM;
}

/*************** Fighter object **************/

static PyMemberDef Fighter_members[] = {
    {NULL, 0, 0, 0, NULL} /* Sentinel */
};

static PyMethodDef Fighter_methods[] = {
    {"pos", (PyCFunction)Item_pos, METH_NOARGS, "Return the position of the item"},
    {"neighbours", (PyCFunction)Item_neighbours, METH_NOARGS, "Return the neighbours of the item"},
    {"distanceTo", (PyCFunction)Item_distanceTo, METH_VARARGS, "Return the distance to the other item or a point"},
    {"rotateOf", (PyCFunction)Item_rotateOf, METH_VARARGS, "Rotate the movable item of the given angle"},
    {"rotateTo", (PyCFunction)Item_rotateTo, METH_VARARGS, "Rotate the movable item in the direction of the other item"},
    {"angle", (PyCFunction)Item_angle, METH_NOARGS, "Return the current angle of the ship"},
    {"fuel", (PyCFunction)Item_fuel, METH_NOARGS, "Return the current fuel of the ship"},
    {"move", (PyCFunction)Item_move, METH_NOARGS, "Move the movable item in the direction given by its angle"},
    {"life", (PyCFunction)Item_life, METH_NOARGS, "Return the remaining life of the item"},
    {"team", (PyCFunction)Item_team, METH_NOARGS, "Return the team of the item"},
    {"isFriend", (PyCFunction)Item_isFriend, METH_VARARGS, "Return true if the given item belong to the same team"},
    {"log", (PyCFunction)Item_log, METH_VARARGS, "Log the message"},
    {"memorySize", (PyCFunction)Item_memorySize, METH_NOARGS, "Return the number of memory slots allocated to the item"},
    {"getMemoryInt", (PyCFunction)Item_getMemoryInt, METH_VARARGS, "Return the memory contained at position 'index' as an int value"},
    {"getMemoryUInt", (PyCFunction)Item_getMemoryUInt, METH_VARARGS, "Return the memory contained at position 'index' as an unsigned int value"},
    {"getMemoryFloat", (PyCFunction)Item_getMemoryFloat, METH_VARARGS, "Return the memory contained at position 'index' as a float value"},
    {"setMemoryInt", (PyCFunction)Item_setMemoryInt, METH_VARARGS, "Set the memory at position 'index' with 'value' as an int"},
    {"setMemoryUInt", (PyCFunction)Item_setMemoryUInt, METH_VARARGS, "Set the memory at position 'index' with 'value' as an unsigned int"},
    {"setMemoryFloat", (PyCFunction)Item_setMemoryFloat, METH_VARARGS, "Set the memory at position 'index' with 'value' as a float"},
    {"missiles", (PyCFunction)Fighter_missiles, METH_NOARGS, "Return the number of missiles in the ship"},
    {"launchMissile", (PyCFunction)Fighter_launchMissile, METH_VARARGS, "Launch a missile to a target"},

    {NULL, NULL, 0, NULL} /* Sentinel */
};

static PyTypeObject FighterType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "aiwar.PlayableFighter",   /*tp_name*/
    sizeof(Item),              /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)Item_dealloc,  /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT,        /*tp_flags*/
    "Playable Fighter objects",/* tp_doc */
    0,                         /* tp_traverse */
    0,                         /* tp_clear */
    0,                         /* tp_richcompare */
    0,                         /* tp_weaklistoffset */
    0,                         /* tp_iter */
    0,                         /* tp_iternext */
    Fighter_methods,           /* tp_methods */
    Fighter_members,           /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)Item_init,       /* tp_init */
    0,                         /* tp_alloc */
    0,                         /* tp_new */
    0,                         /* tp_free */
    0,                         /* tp_is_gc */
    0,                         /* tp_bases */
    0,                         /* tp_mro */
    0,                         /* tp_cache */
    0,                         /* tp_subclasses */
    0,                         /* tp_weaklist */
    0,                         /* tp_del */
    0,                         /* tp_version_tag */
};

PyObject* Fighter_New(aiwar::core::Fighter *m)
{
    Item *pM = PyObject_New(Item, &FighterType);
    if(!pM)
    {
        std::cerr << "Error while creating new Fighter python object" << std::endl;
        return NULL;
    }

    pM->item = m;
    return (PyObject*)pM;
}

/*************** FighterConst object **************/

static PyMemberDef FighterConst_members[] = {
    {NULL, 0, 0, 0, NULL} /* Sentinel */
};

static PyMethodDef FighterConst_methods[] = {
    {"pos", (PyCFunction)Item_pos, METH_NOARGS, "Return the position of the item"},
    {"angle", (PyCFunction)Item_angle, METH_NOARGS, "Return the current angle of the ship"},
    {"life", (PyCFunction)Item_life, METH_NOARGS, "Return the remaining life of the item"},
    {NULL, NULL, 0, NULL} /* Sentinel */
};

static PyTypeObject FighterConstType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "aiwar.Fighter",           /*tp_name*/
    sizeof(Item),              /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)Item_dealloc,  /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT,        /*tp_flags*/
    "Const Fighter objects",   /* tp_doc */
    0,                         /* tp_traverse */
    0,                         /* tp_clear */
    0,                         /* tp_richcompare */
    0,                         /* tp_weaklistoffset */
    0,                         /* tp_iter */
    0,                         /* tp_iternext */
    FighterConst_methods,      /* tp_methods */
    FighterConst_members,      /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)Item_init,       /* tp_init */
    0,                         /* tp_alloc */
    0,                         /* tp_new */
    0,                         /* tp_free */
    0,                         /* tp_is_gc */
    0,                         /* tp_bases */
    0,                         /* tp_mro */
    0,                         /* tp_cache */
    0,                         /* tp_subclasses */
    0,                         /* tp_weaklist */
    0,                         /* tp_del */
    0,                         /* tp_version_tag */
};

PyObject* FighterConst_New(aiwar::core::Fighter *m)
{
    Item *pM = PyObject_New(Item, &FighterConstType);
    if(!pM)
    {
        std::cerr << "Error while creating new FighterConst python object" << std::endl;
        return NULL;
    }

    pM->item = m;
    return (PyObject*)pM;
}



/**** methods implementation ****/
static PyObject *
Item_pos(Item* self)
{
    return Py_BuildValue("(dd)", ((Item*)self)->item->xpos(), ((Item*)self)->item->ypos());
}

static PyObject * Item_neighbours(Item* self)
{
    PyObject* pSet = PyFrozenSet_New(NULL);
    if(!pSet)
        return NULL;

    aiwar::core::Item::ItemSet n = self->item->neighbours();
    aiwar::core::Item::ItemSet::iterator it;
    aiwar::core::Item *item;
    aiwar::core::Mineral *mineral;
    aiwar::core::Missile *missile;
    aiwar::core::MiningShip *miningShip;
    aiwar::core::Base *base;
    aiwar::core::Fighter *fighter;
    PyObject* pItem = NULL;

    for(it = n.begin() ; it != n.end() ; ++it)
    {
        item = *it;
        pItem = NULL;

        if((mineral = dynamic_cast<aiwar::core::Mineral*>(item)))
            pItem = Mineral_New(mineral);
        else if((missile = dynamic_cast<aiwar::core::Missile*>(item)))
            pItem = Missile_New(missile);
        else if((miningShip = dynamic_cast<aiwar::core::MiningShip*>(item)))
            pItem = MiningShipConst_New(miningShip);
        else if((base = dynamic_cast<aiwar::core::Base*>(item)))
            pItem = BaseConst_New(base);
        else if((fighter = dynamic_cast<aiwar::core::Fighter*>(item)))
            pItem = FighterConst_New(fighter);

        if(pItem)
        {
            int r = PySet_Add(pSet, pItem);
            Py_DECREF(pItem);
            if(r != 0) // failure
            {
                std::cerr << "Error while filling neighbours Set" << std::endl;
                PyErr_Print();
                Py_DECREF(pSet);
                return NULL;
            }
        }
        else
            std::cerr << "Item type not yet implemented" << std::endl;
    }

    return pSet;
}

static PyObject *
Item_distanceTo(Item* self, PyObject *args)
{
    PyObject *o = NULL;
    double px = 0.0;
    double py = 0.0;
    if(!PyArg_ParseTuple(args, "O", &o))
    {
        return NULL;
    }
    if(PyObject_IsInstance(o, pItemBasedTuple))
    {
        return PyFloat_FromDouble(self->item->distanceTo(((Item*)o)->item));
    }
    else if(PyArg_ParseTuple(o, "dd", &px, &py))
    {
        return PyFloat_FromDouble(self->item->distanceTo(px, py));
    }
    else
    {
        PyErr_SetString(PyExc_TypeError, "must be an Item or a tuple of two floats");
        return NULL;
    }
}

static PyObject *
Item_rotateOf(Item* self, PyObject *args)
{
    double a;
    if(!PyArg_ParseTuple(args, "d", &a))
        return NULL;
    dynamic_cast<aiwar::core::Movable*>(self->item)->rotateOf(a);
    Py_RETURN_NONE;
}

static PyObject *
Item_rotateTo(Item* self, PyObject *args)
{
    PyObject *o = NULL;
    double px = -1.0;
    double py = -1.0;
    if(!PyArg_ParseTuple(args, "O", &o))
    {
        return NULL;
    }
    if(PyObject_IsInstance(o, pItemBasedTuple))
    {
        dynamic_cast<aiwar::core::Movable*>(self->item)->rotateTo(((Item*)o)->item);
        Py_RETURN_NONE;
    }
    else if(PyArg_ParseTuple(o, "dd", &px, &py))
    {
        dynamic_cast<aiwar::core::Movable*>(self->item)->rotateTo(px, py);
        Py_RETURN_NONE;
    }
    else
    {
        PyErr_SetString(PyExc_TypeError, "must be an Item or a tuple of two floats");
        return NULL;
    }
}

static PyObject *
Item_angle(Item* self)
{
    return Py_BuildValue("d", dynamic_cast<aiwar::core::Movable*>(self->item)->angle());
}

static PyObject *
Item_fuel(Item* self)
{
    return Py_BuildValue("I", dynamic_cast<aiwar::core::Movable*>(self->item)->fuel());
}

static PyObject *
Item_move(Item* self)
{
    dynamic_cast<aiwar::core::Movable*>(self->item)->move();
    Py_RETURN_NONE;
}

static PyObject *
Item_life(Item* self)
{
    return Py_BuildValue("I", dynamic_cast<aiwar::core::Living*>(self->item)->life());
}

static PyObject *
Item_team(Item* self)
{
    return Py_BuildValue("I", dynamic_cast<aiwar::core::Playable*>(self->item)->team());
}

static PyObject *
Item_isFriend(Item* self, PyObject *args)
{
    PyObject *o = NULL;
    if(!PyArg_ParseTuple(args, "O", &o))
    {
        return NULL;
    }

    if(!PyObject_IsInstance(o, pItemBasedTuple))
    {
        PyErr_SetString(PyExc_TypeError, "argmument is not an item");
        return NULL;
    }

    aiwar::core::Playable *pl = dynamic_cast<aiwar::core::Playable*>(((Item*)o)->item);
    if(!pl)
    {
        PyErr_SetString(PyExc_TypeError, "argmument is not a Playable item");
        return NULL;
    }

    if(dynamic_cast<aiwar::core::Playable*>(self->item)->isFriend(pl))
        Py_RETURN_TRUE;
    else
        Py_RETURN_FALSE;
}

static PyObject *
Item_log(Item* self, PyObject *args)
{
    const char *msg;
    if(!PyArg_ParseTuple(args, "s", &msg))
        return NULL;
    dynamic_cast<aiwar::core::Playable*>(self->item)->log(msg);
    Py_RETURN_NONE;
}

static PyObject *
Item_memorySize(Item* self)
{
    return Py_BuildValue("I", dynamic_cast<aiwar::core::Memory*>(self->item)->memorySize());
}

static PyObject *
Item_getMemoryInt(Item *self, PyObject *args)
{
    unsigned int index = 0;
    PyObject *o = NULL;
    if(!PyArg_ParseTuple(args, "I|O", &index, &o))
        return NULL;

    // check if a target item has been given
    if(o)
    {
        if(!PyObject_IsInstance(o, pItemBasedTuple))
        {
            PyErr_SetString(PyExc_TypeError, "second argmument is not an item");
            return NULL;
        }
        aiwar::core::Memory *mem = dynamic_cast<aiwar::core::Memory*>(((Item*)o)->item);
        if(!mem)
        {
            PyErr_SetString(PyExc_TypeError, "second argmument is not a Memory item");
            return NULL;
        }
        return Py_BuildValue("i", dynamic_cast<aiwar::core::Memory*>(self->item)->getMemory<int>(index, mem));
    }
    else
    {
        return Py_BuildValue("i", dynamic_cast<aiwar::core::Memory*>(self->item)->getMemory<int>(index));
    }
}

static PyObject *
Item_getMemoryUInt(Item *self, PyObject *args)
{
    unsigned int index = 0;
    PyObject *o = NULL;
    if(!PyArg_ParseTuple(args, "I|O", &index, &o))
        return NULL;

    // check if a target item has been given
    if(o)
    {
        if(!PyObject_IsInstance(o, pItemBasedTuple))
        {
            PyErr_SetString(PyExc_TypeError, "second argmument is not an item");
            return NULL;
        }
        aiwar::core::Memory *mem = dynamic_cast<aiwar::core::Memory*>(((Item*)o)->item);
        if(!mem)
        {
            PyErr_SetString(PyExc_TypeError, "second argmument is not a Memory item");
            return NULL;
        }
        return Py_BuildValue("I", dynamic_cast<aiwar::core::Memory*>(self->item)->getMemory<unsigned int>(index, mem));
    }
    else
    {
        return Py_BuildValue("I", dynamic_cast<aiwar::core::Memory*>(self->item)->getMemory<unsigned int>(index));
    }
}

static PyObject *
Item_getMemoryFloat(Item *self, PyObject *args)
{
    unsigned int index = 0;
    PyObject *o = NULL;
    if(!PyArg_ParseTuple(args, "I|O", &index, &o))
        return NULL;

    // check if a target item has been given
    if(o)
    {
        if(!PyObject_IsInstance(o, pItemBasedTuple))
        {
            PyErr_SetString(PyExc_TypeError, "second argmument is not an item");
            return NULL;
        }
        aiwar::core::Memory *mem = dynamic_cast<aiwar::core::Memory*>(((Item*)o)->item);
        if(!mem)
        {
            PyErr_SetString(PyExc_TypeError, "second argmument is not a Memory item");
            return NULL;
        }
        return Py_BuildValue("f", dynamic_cast<aiwar::core::Memory*>(self->item)->getMemory<float>(index, mem));
    }
    else
    {
        return Py_BuildValue("f", dynamic_cast<aiwar::core::Memory*>(self->item)->getMemory<float>(index));
    }
}

static PyObject *
Item_setMemoryInt(Item *self, PyObject *args)
{
    unsigned int index = 0;
    int value = 0;
    PyObject *o = NULL;
    if(!PyArg_ParseTuple(args, "Ii|O", &index, &value, &o))
        return NULL;

    // check if a target item has been given
    if(o)
    {
        if(!PyObject_IsInstance(o, pItemBasedTuple))
        {
            PyErr_SetString(PyExc_TypeError, "second argmument is not an item");
            return NULL;
        }
        aiwar::core::Memory *mem = dynamic_cast<aiwar::core::Memory*>(((Item*)o)->item);
        if(!mem)
        {
            PyErr_SetString(PyExc_TypeError, "second argmument is not a Memory item");
            return NULL;
        }
        dynamic_cast<aiwar::core::Memory*>(self->item)->setMemory<int>(index, value, mem);
    }
    else
    {
        dynamic_cast<aiwar::core::Memory*>(self->item)->setMemory<int>(index, value);
    }
    Py_RETURN_NONE;
}

static PyObject *
Item_setMemoryUInt(Item *self, PyObject *args)
{
    unsigned int index = 0;
    unsigned int value = 0u;
    PyObject *o = NULL;
    if(!PyArg_ParseTuple(args, "II|O", &index, &value, &o))
        return NULL;

    // check if a target item has been given
    if(o)
    {
        if(!PyObject_IsInstance(o, pItemBasedTuple))
        {
            PyErr_SetString(PyExc_TypeError, "second argmument is not an item");
            return NULL;
        }
        aiwar::core::Memory *mem = dynamic_cast<aiwar::core::Memory*>(((Item*)o)->item);
        if(!mem)
        {
            PyErr_SetString(PyExc_TypeError, "second argmument is not a Memory item");
            return NULL;
        }
        dynamic_cast<aiwar::core::Memory*>(self->item)->setMemory<unsigned int>(index, value, mem);
    }
    else
    {
        dynamic_cast<aiwar::core::Memory*>(self->item)->setMemory<unsigned int>(index, value);
    }
    Py_RETURN_NONE;
}

static PyObject *
Item_setMemoryFloat(Item *self, PyObject *args)
{
    unsigned int index = 0;
    float value = 0.0f;
    PyObject *o = NULL;
    if(!PyArg_ParseTuple(args, "If|O", &index, &value, &o))
        return NULL;

    // check if a target item has been given
    if(o)
    {
        if(!PyObject_IsInstance(o, pItemBasedTuple))
        {
            PyErr_SetString(PyExc_TypeError, "second argmument is not an item");
            return NULL;
        }
        aiwar::core::Memory *mem = dynamic_cast<aiwar::core::Memory*>(((Item*)o)->item);
        if(!mem)
        {
            PyErr_SetString(PyExc_TypeError, "second argmument is not a Memory item");
            return NULL;
        }
        dynamic_cast<aiwar::core::Memory*>(self->item)->setMemory<float>(index, value, mem);
    }
    else
    {
        dynamic_cast<aiwar::core::Memory*>(self->item)->setMemory<float>(index, value);
    }
    Py_RETURN_NONE;
}

static PyObject *
MiningShip_extract(Item* self, PyObject *args)
{
    Item *m = NULL;
    if(!PyArg_ParseTuple(args, "O!", &MineralType, &m))
        return NULL;
    return Py_BuildValue("I", dynamic_cast<aiwar::core::MiningShip*>(self->item)->extract(dynamic_cast<aiwar::core::Mineral*>(m->item)));
}

static PyObject *
MiningShip_mineralStorage(Item* self)
{
    return Py_BuildValue("I", dynamic_cast<aiwar::core::MiningShip*>(self->item)->mineralStorage());
}

static PyObject *
MiningShip_pushMineral(Item* self, PyObject *args)
{
    PyObject *o = NULL;
    unsigned int value = 0;
    if(!PyArg_ParseTuple(args, "OI", &o, &value))
        return NULL;

    if(!PyObject_IsInstance(o, pItemBasedTuple))
    {
        PyErr_SetString(PyExc_TypeError, "must be an item");
        return NULL;
    }
    aiwar::core::Base *b = dynamic_cast<aiwar::core::Base*>(((Item*)o)->item);
    if(!b)
    {
        PyErr_SetString(PyExc_TypeError, "must be a Base");
        return NULL;
    }

    return Py_BuildValue("I", dynamic_cast<aiwar::core::MiningShip*>(self->item)->pushMineral(b, value));
}

static PyObject *
Base_mineralStorage(Item* self)
{
    return Py_BuildValue("I", dynamic_cast<aiwar::core::Base*>(self->item)->mineralStorage());
}

static PyObject *
Base_pullMineral(Item* self, PyObject *args)
{
    PyObject *o = NULL;
    unsigned int value = 0;
    if(!PyArg_ParseTuple(args, "OI", &o, &value))
    {
        return NULL;
    }
    if(!PyObject_IsInstance(o, pItemBasedTuple))
    {
        PyErr_SetString(PyExc_TypeError, "must be an item");
        return NULL;
    }
    aiwar::core::MiningShip *m = dynamic_cast<aiwar::core::MiningShip*>(((Item*)o)->item);
    if(!m)
    {
        PyErr_SetString(PyExc_TypeError, "must be a MiningShip");
        return NULL;
    }
    return Py_BuildValue("I", dynamic_cast<aiwar::core::Base*>(self->item)->pullMineral(m, value));
}

static PyObject *
Base_launchMissile(Item* self, PyObject *args)
{
    PyObject *o = NULL;
    if(!PyArg_ParseTuple(args, "O", &o))
    {
        return NULL;
    }
    if(!PyObject_IsInstance(o, pItemBasedTuple))
    {
        PyErr_SetString(PyExc_TypeError, "must be an item");
        return NULL;
    }
    aiwar::core::Living *t = dynamic_cast<aiwar::core::Living*>(((Item*)o)->item);
    if(!t)
    {
        PyErr_SetString(PyExc_TypeError, "must be a Living Object");
        return NULL;
    }
    dynamic_cast<aiwar::core::Base*>(self->item)->launchMissile(t);
    Py_RETURN_NONE;
}

static PyObject *
Base_createMiningShip(Item* self)
{
    dynamic_cast<aiwar::core::Base*>(self->item)->createMiningShip();
    Py_RETURN_NONE;
}

static PyObject *
Base_repair(Item* self, PyObject *args)
{
    PyObject *o = NULL;
    unsigned int value = 0;
    if(!PyArg_ParseTuple(args, "I|O", &value, &o))
    {
        return NULL;
    }
    if(!o)
    {
        return Py_BuildValue("I", dynamic_cast<aiwar::core::Base*>(self->item)->repair(value));
    }
    else
    {
        if(!PyObject_IsInstance(o, pItemBasedTuple))
        {
            PyErr_SetString(PyExc_TypeError, "must be an item");
            return NULL;
        }
        aiwar::core::Living *t = dynamic_cast<aiwar::core::Living*>(((Item*)o)->item);
        if(!t)
        {
            PyErr_SetString(PyExc_TypeError, "must be a Living Object");
            return NULL;
        }
        return Py_BuildValue("I", dynamic_cast<aiwar::core::Base*>(self->item)->repair(value, t));
    }
}

static PyObject *
Base_refuel(Item* self, PyObject *args)
{
    PyObject *o = NULL;
    unsigned int value = 0;
    if(!PyArg_ParseTuple(args, "IO", &value, &o))
    {
        return NULL;
    }
    if(!PyObject_IsInstance(o, pItemBasedTuple))
    {
        PyErr_SetString(PyExc_TypeError, "must be an item");
        return NULL;
    }
    aiwar::core::Movable *t = dynamic_cast<aiwar::core::Movable*>(((Item*)o)->item);
    if(!t)
    {
        PyErr_SetString(PyExc_TypeError, "must be a Movable Object");
        return NULL;
    }
    return Py_BuildValue("I", dynamic_cast<aiwar::core::Base*>(self->item)->refuel(value, t));
}

static PyObject *
Fighter_missiles(Item* self)
{
    return Py_BuildValue("I", dynamic_cast<aiwar::core::Fighter*>(self->item)->missiles());
}

static PyObject *
Fighter_launchMissile(Item* self, PyObject *args)
{
    PyObject *o = NULL;
    if(!PyArg_ParseTuple(args, "O", &o))
    {
        return NULL;
    }
    if(!PyObject_IsInstance(o, pItemBasedTuple))
    {
        PyErr_SetString(PyExc_TypeError, "must be an item");
        return NULL;
    }
    aiwar::core::Living *t = dynamic_cast<aiwar::core::Living*>(((Item*)o)->item);
    if(!t)
    {
        PyErr_SetString(PyExc_TypeError, "must be a Living Object");
        return NULL;
    }
    dynamic_cast<aiwar::core::Fighter*>(self->item)->launchMissile(t);
    Py_RETURN_NONE;
}

static PyObject *
Base_createFighter(Item* self)
{
    dynamic_cast<aiwar::core::Base*>(self->item)->createFighter();
    Py_RETURN_NONE;
}

static PyObject *
Base_giveMissiles(Item* self, PyObject *args)
{
    PyObject *o = NULL;
    unsigned int value = 0;
    if(!PyArg_ParseTuple(args, "IO", &value, &o))
    {
        return NULL;
    }
    if(!PyObject_IsInstance(o, pItemBasedTuple))
    {
        PyErr_SetString(PyExc_TypeError, "must be an item");
        return NULL;
    }
    aiwar::core::Fighter *t = dynamic_cast<aiwar::core::Fighter*>(((Item*)o)->item);
    if(!t)
    {
        PyErr_SetString(PyExc_TypeError, "must be a Fighter");
        return NULL;
    }
    return Py_BuildValue("I", dynamic_cast<aiwar::core::Base*>(self->item)->giveMissiles(value, t));
}




/* getter for all config constants */
static PyObject* Config_WORLD_SIZE_X(PyObject*) { return Py_BuildValue("d", aiwar::core::Config::instance().WORLD_SIZE_X); }
static PyObject* Config_WORLD_SIZE_Y(PyObject*) { return Py_BuildValue("d", aiwar::core::Config::instance().WORLD_SIZE_Y); }

static PyObject* Config_MINERAL_SIZE_X(PyObject*) { return Py_BuildValue("d", aiwar::core::Config::instance().MINERAL_SIZE_X); }
static PyObject* Config_MINERAL_SIZE_Y(PyObject*) { return Py_BuildValue("d", aiwar::core::Config::instance().MINERAL_SIZE_Y); }
static PyObject* Config_MINERAL_LIFE(PyObject*) { return Py_BuildValue("I", aiwar::core::Config::instance().MINERAL_LIFE); }

static PyObject* Config_MININGSHIP_SIZE_X(PyObject*) { return Py_BuildValue("d", aiwar::core::Config::instance().MININGSHIP_SIZE_X); }
static PyObject* Config_MININGSHIP_SIZE_Y(PyObject*) { return Py_BuildValue("d", aiwar::core::Config::instance().MININGSHIP_SIZE_Y); }
static PyObject* Config_MININGSHIP_SPEED(PyObject*) { return Py_BuildValue("d", aiwar::core::Config::instance().MININGSHIP_SPEED); }
static PyObject* Config_MININGSHIP_DETECTION_RADIUS(PyObject*) { return Py_BuildValue("d", aiwar::core::Config::instance().MININGSHIP_DETECTION_RADIUS); }
static PyObject* Config_MININGSHIP_MAX_LIFE(PyObject*) { return Py_BuildValue("I", aiwar::core::Config::instance().MININGSHIP_MAX_LIFE); }
static PyObject* Config_MININGSHIP_START_LIFE(PyObject*) { return Py_BuildValue("I", aiwar::core::Config::instance().MININGSHIP_START_LIFE); }
static PyObject* Config_MININGSHIP_START_FUEL(PyObject*) { return Py_BuildValue("I", aiwar::core::Config::instance().MININGSHIP_START_FUEL); }
static PyObject* Config_MININGSHIP_MAX_FUEL(PyObject*) { return Py_BuildValue("I", aiwar::core::Config::instance().MININGSHIP_MAX_FUEL); }
static PyObject* Config_MININGSHIP_MOVE_CONSO(PyObject*) { return Py_BuildValue("I", aiwar::core::Config::instance().MININGSHIP_MOVE_CONSO); }
static PyObject* Config_MININGSHIP_MINING_RADIUS(PyObject*) { return Py_BuildValue("d", aiwar::core::Config::instance().MININGSHIP_MINING_RADIUS); }
static PyObject* Config_MININGSHIP_MINERAL_EXTRACT(PyObject*) { return Py_BuildValue("I", aiwar::core::Config::instance().MININGSHIP_MINERAL_EXTRACT); }
static PyObject* Config_MININGSHIP_MAX_MINERAL_STORAGE(PyObject*) { return Py_BuildValue("I", aiwar::core::Config::instance().MININGSHIP_MAX_MINERAL_STORAGE); }
static PyObject* Config_MININGSHIP_MEMORY_SIZE(PyObject*) { return Py_BuildValue("I", aiwar::core::Config::instance().MININGSHIP_MEMORY_SIZE); }

static PyObject* Config_FIGHTER_SIZE_X(PyObject*) { return Py_BuildValue("d", aiwar::core::Config::instance().FIGHTER_SIZE_X); }
static PyObject* Config_FIGHTER_SIZE_Y(PyObject*) { return Py_BuildValue("d", aiwar::core::Config::instance().FIGHTER_SIZE_Y); }
static PyObject* Config_FIGHTER_SPEED(PyObject*) { return Py_BuildValue("d", aiwar::core::Config::instance().FIGHTER_SPEED); }
static PyObject* Config_FIGHTER_DETECTION_RADIUS(PyObject*) { return Py_BuildValue("d", aiwar::core::Config::instance().FIGHTER_DETECTION_RADIUS); }
static PyObject* Config_FIGHTER_MAX_LIFE(PyObject*) { return Py_BuildValue("I", aiwar::core::Config::instance().FIGHTER_MAX_LIFE); }
static PyObject* Config_FIGHTER_START_LIFE(PyObject*) { return Py_BuildValue("I", aiwar::core::Config::instance().FIGHTER_START_LIFE); }
static PyObject* Config_FIGHTER_MOVE_CONSO(PyObject*) { return Py_BuildValue("I", aiwar::core::Config::instance().FIGHTER_MOVE_CONSO); }
static PyObject* Config_FIGHTER_START_FUEL(PyObject*) { return Py_BuildValue("I", aiwar::core::Config::instance().FIGHTER_START_FUEL); }
static PyObject* Config_FIGHTER_MAX_FUEL(PyObject*) { return Py_BuildValue("I", aiwar::core::Config::instance().FIGHTER_MAX_FUEL); }
static PyObject* Config_FIGHTER_MEMORY_SIZE(PyObject*) { return Py_BuildValue("I", aiwar::core::Config::instance().FIGHTER_MEMORY_SIZE); }
static PyObject* Config_FIGHTER_START_MISSILE(PyObject*) { return Py_BuildValue("I", aiwar::core::Config::instance().FIGHTER_START_MISSILE); }
static PyObject* Config_FIGHTER_MAX_MISSILE(PyObject*) { return Py_BuildValue("I", aiwar::core::Config::instance().FIGHTER_MAX_MISSILE); }

static PyObject* Config_MISSILE_SIZE_X(PyObject*) { return Py_BuildValue("d", aiwar::core::Config::instance().MISSILE_SIZE_X); }
static PyObject* Config_MISSILE_SIZE_Y(PyObject*) { return Py_BuildValue("d", aiwar::core::Config::instance().MISSILE_SIZE_Y); }
static PyObject* Config_MISSILE_LIFE(PyObject*) { return Py_BuildValue("I", aiwar::core::Config::instance().MISSILE_LIFE); }
static PyObject* Config_MISSILE_MOVE_CONSO(PyObject*) { return Py_BuildValue("I", aiwar::core::Config::instance().MISSILE_MOVE_CONSO); }
static PyObject* Config_MISSILE_START_FUEL(PyObject*) { return Py_BuildValue("I", aiwar::core::Config::instance().MISSILE_START_FUEL); }
static PyObject* Config_MISSILE_MAX_FUEL(PyObject*) { return Py_BuildValue("I", aiwar::core::Config::instance().MISSILE_MAX_FUEL); }
static PyObject* Config_MISSILE_SPEED(PyObject*) { return Py_BuildValue("d", aiwar::core::Config::instance().MISSILE_SPEED); }
static PyObject* Config_MISSILE_DAMAGE(PyObject*) { return Py_BuildValue("I", aiwar::core::Config::instance().MISSILE_DAMAGE); }

static PyObject* Config_BASE_SIZE_X(PyObject*) { return Py_BuildValue("d", aiwar::core::Config::instance().BASE_SIZE_X); }
static PyObject* Config_BASE_SIZE_Y(PyObject*) { return Py_BuildValue("d", aiwar::core::Config::instance().BASE_SIZE_Y); }
static PyObject* Config_BASE_DETECTION_RADIUS(PyObject*) { return Py_BuildValue("d", aiwar::core::Config::instance().BASE_DETECTION_RADIUS); }
static PyObject* Config_BASE_MAX_LIFE(PyObject*) { return Py_BuildValue("I", aiwar::core::Config::instance().BASE_MAX_LIFE); }
static PyObject* Config_BASE_START_LIFE(PyObject*) { return Py_BuildValue("I", aiwar::core::Config::instance().BASE_START_LIFE); }
static PyObject* Config_BASE_MISSILE_PRICE(PyObject*) { return Py_BuildValue("I", aiwar::core::Config::instance().BASE_MISSILE_PRICE); }
static PyObject* Config_BASE_MININGSHIP_PRICE(PyObject*) { return Py_BuildValue("I", aiwar::core::Config::instance().BASE_MININGSHIP_PRICE); }
static PyObject* Config_BASE_FIGHTER_PRICE(PyObject*) { return Py_BuildValue("I", aiwar::core::Config::instance().BASE_FIGHTER_PRICE); }
static PyObject* Config_BASE_START_MINERAL_STORAGE(PyObject*) { return Py_BuildValue("I", aiwar::core::Config::instance().BASE_START_MINERAL_STORAGE); }
static PyObject* Config_BASE_MAX_MINERAL_STORAGE(PyObject*) { return Py_BuildValue("I", aiwar::core::Config::instance().BASE_MAX_MINERAL_STORAGE); }
static PyObject* Config_BASE_MEMORY_SIZE(PyObject*) { return Py_BuildValue("I", aiwar::core::Config::instance().BASE_MEMORY_SIZE); }
static PyObject* Config_BASE_REPAIR_RADIUS(PyObject*) { return Py_BuildValue("d", aiwar::core::Config::instance().BASE_REPAIR_RADIUS); }
static PyObject* Config_BASE_REFUEL_RADIUS(PyObject*) { return Py_BuildValue("d", aiwar::core::Config::instance().BASE_REFUEL_RADIUS); }
static PyObject* Config_BASE_GIVE_MISSILE_RADIUS(PyObject*) { return Py_BuildValue("d", aiwar::core::Config::instance().BASE_GIVE_MISSILE_RADIUS); }

static PyObject* Config_COMMUNICATION_RADIUS(PyObject*) { return Py_BuildValue("d", aiwar::core::Config::instance().COMMUNICATION_RADIUS); }

static PyMethodDef module_methods[] = {
    {"WORLD_SIZE_X", (PyCFunction)Config_WORLD_SIZE_X, METH_NOARGS, "Return the horizontal world size"},
    {"WORLD_SIZE_Y", (PyCFunction)Config_WORLD_SIZE_Y, METH_NOARGS, "Return the vertical world size"},

    {"MINERAL_SIZE_X", (PyCFunction)Config_MINERAL_SIZE_X, METH_NOARGS, "Return horizontal size of a mineral"},
    {"MINERAL_SIZE_Y", (PyCFunction)Config_MINERAL_SIZE_Y, METH_NOARGS, "Return vertical size of a mineral"},
    {"MINERAL_LIFE", (PyCFunction)Config_MINERAL_LIFE, METH_NOARGS, "Return mineral start life"},

    {"MININGSHIP_SIZE_X", (PyCFunction)Config_MININGSHIP_SIZE_X, METH_NOARGS, "Return horizontal size of a MiningShip"},
    {"MININGSHIP_SIZE_Y", (PyCFunction)Config_MININGSHIP_SIZE_Y, METH_NOARGS, "Return vertical size of a MiningShip"},
    {"MININGSHIP_SPEED", (PyCFunction)Config_MININGSHIP_SPEED, METH_NOARGS, "Return speed of a MiningShip"},
    {"MININGSHIP_DETECTION_RADIUS", (PyCFunction)Config_MININGSHIP_DETECTION_RADIUS, METH_NOARGS, "Return detection radius of a MiningShip"},
    {"MININGSHIP_MAX_LIFE", (PyCFunction)Config_MININGSHIP_MAX_LIFE, METH_NOARGS, "Return max life of a MiningShip"},
    {"MININGSHIP_START_LIFE", (PyCFunction)Config_MININGSHIP_START_LIFE, METH_NOARGS, "Return start life of a MiningShip"},
    {"MININGSHIP_START_FUEL", (PyCFunction)Config_MININGSHIP_START_FUEL, METH_NOARGS, "Return start fuel of a MiningShip"},
    {"MININGSHIP_MAX_FUEL", (PyCFunction)Config_MININGSHIP_MAX_FUEL, METH_NOARGS, "Return start fuel of a MiningShip"},
    {"MININGSHIP_MOVE_CONSO", (PyCFunction)Config_MININGSHIP_MOVE_CONSO, METH_NOARGS, "Return fuel consumption of one move for a MiningShip"},
    {"MININGSHIP_MINING_RADIUS", (PyCFunction)Config_MININGSHIP_MINING_RADIUS, METH_NOARGS, "Return mining radius of a MiningShip"},
    {"MININGSHIP_MINERAL_EXTRACT", (PyCFunction)Config_MININGSHIP_MINERAL_EXTRACT, METH_NOARGS, "Return max number of taken mineral per extraction for a MiningShip"},
    {"MININGSHIP_MAX_MINERAL_STORAGE", (PyCFunction)Config_MININGSHIP_MAX_MINERAL_STORAGE, METH_NOARGS, "Return mineral maximal capacity of storage for a MiningShip"},
    {"MININGSHIP_MEMORY_SIZE", (PyCFunction)Config_MININGSHIP_MEMORY_SIZE, METH_NOARGS, "Return number of memory slot for a MiningShip"},

    {"FIGHTER_SIZE_X", (PyCFunction)Config_FIGHTER_SIZE_X, METH_NOARGS, "Return horizontal size of a Fighter"},
    {"FIGHTER_SIZE_Y", (PyCFunction)Config_FIGHTER_SIZE_Y, METH_NOARGS, "Return vertical size of a Fighter"},
    {"FIGHTER_SPEED", (PyCFunction)Config_FIGHTER_SPEED, METH_NOARGS, "Return speed of a Fighter"},
    {"FIGHTER_DETECTION_RADIUS", (PyCFunction)Config_FIGHTER_DETECTION_RADIUS, METH_NOARGS, "Return detection radius of a Fighter"},
    {"FIGHTER_MAX_LIFE", (PyCFunction)Config_FIGHTER_MAX_LIFE, METH_NOARGS, "Return maximal life of a Fighter"},
    {"FIGHTER_START_LIFE", (PyCFunction)Config_FIGHTER_START_LIFE, METH_NOARGS, "Return start life of a Fighter"},
    {"FIGHTER_MOVE_CONSO", (PyCFunction)Config_FIGHTER_MOVE_CONSO, METH_NOARGS, "Return fule consumption of one move for a Fighter"},
    {"FIGHTER_START_FUEL", (PyCFunction)Config_FIGHTER_START_FUEL, METH_NOARGS, "Return start fuel of a Fighter"},
    {"FIGHTER_MAX_FUEL", (PyCFunction)Config_FIGHTER_MAX_FUEL, METH_NOARGS, "Return maximal fuel of a Fighter"},
    {"FIGHTER_MEMORY_SIZE", (PyCFunction)Config_FIGHTER_MEMORY_SIZE, METH_NOARGS, "Return number of memory slots of a Fighter"},
    {"FIGHTER_START_MISSILE", (PyCFunction)Config_FIGHTER_START_MISSILE, METH_NOARGS, "Return number of missiles in a new Fighter"},
    {"FIGHTER_MAX_MISSILE", (PyCFunction)Config_FIGHTER_MAX_MISSILE, METH_NOARGS, "Return maximal number of missiles that a Fighter can contain"},

    {"MISSILE_SIZE_X", (PyCFunction)Config_MISSILE_SIZE_X, METH_NOARGS, "Return horizontal size of a Missile"},
    {"MISSILE_SIZE_Y", (PyCFunction)Config_MISSILE_SIZE_Y, METH_NOARGS, "Return vertical size of a Missile"},
    {"MISSILE_LIFE", (PyCFunction)Config_MISSILE_LIFE, METH_NOARGS, "Return number of life points of a Missile"},
    {"MISSILE_MOVE_CONSO", (PyCFunction)Config_MISSILE_MOVE_CONSO, METH_NOARGS, "Return fuel consumption of one move for a Missile"},
    {"MISSILE_START_FUEL", (PyCFunction)Config_MISSILE_START_FUEL, METH_NOARGS, "Return fuel capacity of a new Missile"},
    {"MISSILE_MAX_FUEL", (PyCFunction)Config_MISSILE_MAX_FUEL, METH_NOARGS, "Return maximal fuel capacity of a Missile"},
    {"MISSILE_SPEED", (PyCFunction)Config_MISSILE_SPEED, METH_NOARGS, "Return speed of a Missile"},
    {"MISSILE_DAMAGE", (PyCFunction)Config_MISSILE_DAMAGE, METH_NOARGS, "Return number of life points taken by a Missile when he reaches its target"},

    {"BASE_SIZE_X", (PyCFunction)Config_BASE_SIZE_X, METH_NOARGS, "Return horizontal size of a Base"},
    {"BASE_SIZE_Y", (PyCFunction)Config_BASE_SIZE_Y, METH_NOARGS, "Return vertical size of a Base"},
    {"BASE_DETECTION_RADIUS", (PyCFunction)Config_BASE_DETECTION_RADIUS, METH_NOARGS, "Return detection radius of a Base"},
    {"BASE_MAX_LIFE", (PyCFunction)Config_BASE_MAX_LIFE, METH_NOARGS, "Return maximum number of life points for a Base"},
    {"BASE_START_LIFE", (PyCFunction)Config_BASE_START_LIFE, METH_NOARGS, "Return number of life points of a new Base"},
    {"BASE_MISSILE_PRICE", (PyCFunction)Config_BASE_MISSILE_PRICE, METH_NOARGS, "Return price of a Missile"},
    {"BASE_MININGSHIP_PRICE", (PyCFunction)Config_BASE_MININGSHIP_PRICE, METH_NOARGS, "Return price of a MiningShip"},
    {"BASE_FIGHTER_PRICE", (PyCFunction)Config_BASE_FIGHTER_PRICE, METH_NOARGS, "Return price of a Fighter"},
    {"BASE_START_MINERAL_STORAGE", (PyCFunction)Config_BASE_START_MINERAL_STORAGE, METH_NOARGS, "Return mineral storage of a new Base"},
    {"BASE_MAX_MINERAL_STORAGE", (PyCFunction)Config_BASE_MAX_MINERAL_STORAGE, METH_NOARGS, "Return maximum mineral storage capacity of a Base"},
    {"BASE_MEMORY_SIZE", (PyCFunction)Config_BASE_MEMORY_SIZE, METH_NOARGS, "Return number of memory slot of a Base"},
    {"BASE_REPAIR_RADIUS", (PyCFunction)Config_BASE_REPAIR_RADIUS, METH_NOARGS, "Return radius in which a ship must be placed to be repaired by a Base"},
    {"BASE_REFUEL_RADIUS", (PyCFunction)Config_BASE_REFUEL_RADIUS, METH_NOARGS, "Return radius in which a ship must be placed to be refueled by a Base"},
    {"BASE_GIVE_MISSILE_RADIUS", (PyCFunction)Config_BASE_GIVE_MISSILE_RADIUS, METH_NOARGS, "Return radius in which a fighter must be placed to received missiles from a Base"},

    {"COMMUNICATION_RADIUS", (PyCFunction)Config_COMMUNICATION_RADIUS, METH_NOARGS, "Return communication radius"},

    {NULL, NULL, 0, NULL}  /* Sentinel */
};

bool initPythonInterpreter(int /*argc*/, char* /*argv*/[])
{
    char *p = strdup("path");
    PyObject *path = PySys_GetObject(p);  // path is a borrowed ref, do not call Py_DECREF on it
    free(p);
    if(!path)
    {
        PyErr_Print();
        return false;
    }

    PyObject *point = PyString_FromString(".");
    if(!point)
    {
        PyErr_Print();
        return false;
    }

    int ret = PyList_Insert(path, 0, point);
    Py_DECREF(point);
    if(ret != 0)
    {
        PyErr_Print();
        return false;
    }

    return true;
}

// todo clean when an error occured
bool initAiwarModule()
{
    // init pItemBasedTuple
    pItemBasedTuple = PyTuple_New(8);
    if(!pItemBasedTuple)
    {
        std::cerr << "Fail to create pItemBasedTuple" << std::endl;
        PyErr_Print();
        return false;
    }
    unsigned int i = 0;
    Py_INCREF(&MiningShipType);
    PyTuple_SetItem(pItemBasedTuple, i++, (PyObject*)&MiningShipType);
    Py_INCREF(&MiningShipConstType);
    PyTuple_SetItem(pItemBasedTuple, i++, (PyObject*)&MiningShipConstType);
    Py_INCREF(&MineralType);
    PyTuple_SetItem(pItemBasedTuple, i++, (PyObject*)&MineralType);
    Py_INCREF(&MissileType);
    PyTuple_SetItem(pItemBasedTuple, i++, (PyObject*)&MissileType);
    Py_INCREF(&BaseType);
    PyTuple_SetItem(pItemBasedTuple, i++, (PyObject*)&BaseType);
    Py_INCREF(&BaseConstType);
    PyTuple_SetItem(pItemBasedTuple, i++, (PyObject*)&BaseConstType);
    Py_INCREF(&FighterType);
    PyTuple_SetItem(pItemBasedTuple, i++, (PyObject*)&FighterType);
    Py_INCREF(&FighterConstType);
    PyTuple_SetItem(pItemBasedTuple, i++, (PyObject*)&FighterConstType);

    PyObject* m;

    MiningShipType.tp_new = PyType_GenericNew;
    if(PyType_Ready(&MiningShipType) < 0)
        return false;

    MiningShipConstType.tp_new = PyType_GenericNew;
    if(PyType_Ready(&MiningShipConstType) < 0)
        return false;

    MineralType.tp_new = PyType_GenericNew;
    if(PyType_Ready(&MineralType) < 0)
        return false;

    MissileType.tp_new = PyType_GenericNew;
    if(PyType_Ready(&MissileType) < 0)
        return false;

    BaseType.tp_new = PyType_GenericNew;
    if(PyType_Ready(&BaseType) < 0)
        return false;

    BaseConstType.tp_new = PyType_GenericNew;
    if(PyType_Ready(&BaseConstType) < 0)
        return false;

    FighterType.tp_new = PyType_GenericNew;
    if(PyType_Ready(&FighterType) < 0)
        return false;

    FighterConstType.tp_new = PyType_GenericNew;
    if(PyType_Ready(&FighterConstType) < 0)
        return false;

    m = Py_InitModule3("aiwar", module_methods,
                       "Example module that creates an extension type.");

    if (m == NULL)
      return false;


    /* Add aiwar objects to the module */

    /* add MiningShip */
    Py_INCREF(&MiningShipType);
    PyModule_AddObject(m, "PlayableMiningShip", (PyObject*)&MiningShipType);

    /* add MiningShipConst */
    Py_INCREF(&MiningShipConstType);
    PyModule_AddObject(m, "MiningShip", (PyObject*)&MiningShipConstType);

    /* add Mineral */
    Py_INCREF(&MineralType);
    PyModule_AddObject(m, "Mineral", (PyObject*)&MineralType);

    /* add Missile */
    Py_INCREF(&MissileType);
    PyModule_AddObject(m, "Missile", (PyObject*)&MissileType);

    /* add Base */
    Py_INCREF(&BaseType);
    PyModule_AddObject(m, "PlayableBase", (PyObject*)&BaseType);

    /* add BaseConst */
    Py_INCREF(&BaseConstType);
    PyModule_AddObject(m, "Base", (PyObject*)&BaseConstType);

    /* add Fighter */
    Py_INCREF(&FighterType);
    PyModule_AddObject(m, "PlayableFighter", (PyObject*)&FighterType);

    /* add FighterConst */
    Py_INCREF(&FighterConstType);
    PyModule_AddObject(m, "Fighter", (PyObject*)&FighterConstType);

    return true;
}

#ifndef PyMODINIT_FUNC  /* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif
PyMODINIT_FUNC
initaiwar(void)
{
    initAiwarModule();
}
