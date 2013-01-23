AIWar
=====

Create your Artificial Intelligence to win the war


AIWar is a game that let you create artificial intelligences to control space ships. The goal is to assemble a fighter army to destroy the ennemy base. To do that, you must get minerals with miningship and create fighters with your ressources. And you should also defend yourself again the ennemy army. The first team that destroies the ennemy base wins the match !


*COMPILE*

This section describes the compilation process. If you prefer use a pre-compiled version (currently available for Windows only) of the program, just go to section INSTALL below.

Direct dependancies:
- tinyxml
- python (2.7 is the only tested version)
- SDL
- SDL_gfx
- SDL_ttf

SDL_ttf needs libfreetype that needs zlib to run.

Currently AIWar only works on Linux and Windows. Other platforms have not been tested yet.

_Linux_

To compile AIWar, just install dev packages of the libraries listed above, and run 'make CPP=g++ LD=g++' (or just 'make' if you have clang compiler installed).

_Windows_

You need Visual C++ 2008 (Express Edition works fine), TinyXML, SDL, SDL_gfx and SDL_ttf headers, and python 2.7 (python headers are distributed with the python installer).
Open AIWar.sln and compile in Release mode (to compile in Debug mode, you must have a debug version of python, which is not distributed by the python maintainers on windows, but if you compile it yourself, it should work !).
You also need dlls of libfreetype and zlib. See SDL_tff requierements.

*INSTALL*

If you have compiled the program, there is nothing to do, just go the the RUN section below.

If you use a pre-compile version for Windows, you must have the Visual Studio 2008 SP1 Redistributable Package (x86) installed. You can find it on the Microsoft website : http://www.microsoft.com/en-us/download/details.aspx?id=5582.
It's free.

You can find compiled versions for AIWar here: https://www.dropbox.com/sh/b6p8w3j7kfbuua9/0Zp4-5rdwS

Then unzip the archive in a folder, where you want on your computer, and keep going to the next section.

*RUN*

'./AIWar' or 'AIWar.exe'

That's it !

More options are available, './AIWar --help' will help you...

To create your own AI, you can create a python file, and provide three functions : play_base(base), play_miningship(miningship) and play_fighter(fighter). See embtest.py for details and examples. Then you add a <player> section in config.xml and set your player name in one of the two teams : blue or red.

*CONTRIBUTE*

If you have suggestions or bug report, do not hesitate to post them in the tracker.

Have fun !
