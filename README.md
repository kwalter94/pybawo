# PyBawo
PyBawo is an implementation of the East African board game, Bao or Bawo.

## Requirements
* [Python 3](https://python.org) (preferable Python 3.6).
* [Python Imaging](http://www.pythonware.com/products/pil/) or [Pillow](https://pillow.readthedocs.io/en/5.1.x/).
* SleekXMPP (Can do without this at the moment).

## Installation
### For the impatient Windows user
-----------------------------------------------
1) Grab an executable from [Sourceforge](https://sourceforge.net/projects/pybawo/files/PyBawo.exe/download)

### For the slightly patient Windows user
------------------------------------------------------
1) Download Python 3.6 from [here](https://python.org) and install it.
2) Then set up Pillow by following the instructions [here](https://pillow.readthedocs.io/en/5.1.x/)

### For those who know what they are doing
--------------------------------------------------------
1) Install Python 3.6
2) Install the requirements as follows
```sh
python3 -m pip install -r requirements.txt
```

## Running PyBawo
Run main.py to start game. Networked game play is yet to be implemented.

## How to play Bawo/Bao
You can find the rules of how to play bawo at
[Game Cabinet](http://www.gamecabinet.com/rules/bao.html). The page at
gamecabinet has rules on how to play the beginner (yawana) and advanced
(yabambo) variants of Bawo. The ntchuwa variant available in the game is
similar to the advanced version with no nyumba.

NOTE: PyBawo does not yet implement the Takasia rule.

PyBawo adds some few rules of its own to make computer play easy (possible).

1) Takata moves that exceed the long_move_limit (defaults at 200) in terms of
   number of sows (steps) are deemed infinite and illegal. Never ending moves
   have been proven to exist and are all takata moves (see "Towards a
   Quasi-Endgame-Based Bao Solver" by Tom Kronenburg, and
   "Never Ending Moves in Bao" by Tom Kronenburg, Jeroen Donkers,
   and Alex J. de Voogt)
2) In Namua, a capture move that ends on the nyumba ends there. There is no
   option to continue or not continue the move as part of the same move.
   The player is simply requested to make another move in which the player
   may sow the nyumba or leave it by making a null move (see below for how
   this is done).
   
* Perfoming moves in PyBawo
--------------------------
To perform a normal move, left click on the hole where the move must start 
then click on the hole to the left or right depending on which direction you
want the move to go. NOTE: you do not have to click on the store when in Namua,
the nkhomo is introduced into the game automatically after you select your
move.

To perform a null move, left click twice on your nyumba.

To cancel a move, right click after selecting (by left clicking) the hole where
you want the move to start. You can only cancel a move before the second right
click. A move in execution can not be cancelled but it can be undone after its
finished execution.

## Copyleft
The source and all artwork used and distributed as part of the main
distribution (coming from me, the author) is under the GNU Public License
version 3 (GPLv3) or any later versions of the license. A copy of the
license is available at: http://www.gnu.org/licenses/gpl-3.0.html
