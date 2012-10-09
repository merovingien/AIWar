from distutils.core import setup, Extension

cxxsrc = ["config.cpp", "item.cpp", "living.cpp", "movable.cpp", "playable.cpp", "memory.cpp", "mineral.cpp", "base.cpp", "miningship.cpp", "fighter.cpp", "missile.cpp", "item_manager.cpp", "game_manager.cpp", "python_wrapper.cpp"]


setup(name="aiwar", version="1.0-beta1",
      ext_modules=[
        Extension("aiwar", cxxsrc, libraries=["tinyxml"])
        ])
