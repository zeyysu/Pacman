fork from https://github.com/DevinLeamy/Pacman

With following enhancements:

Maze generation: A labyrinth creation algorithm creates a brand-new maze on the fly for every session.

Strategy-AI: Controls how ghosts are strategically placed, controlling both the initial spawning and reinforcements that come after. Four ghosts appear at the beginning. Every minute that passes without Pac-Man winning, a new ghost with different color appears.

Tactical-AI: Ghosts are equipped with Tactical AI, enabling dynamic decisions based on their own sensing mechanisms. With a sensing distance of 10 steps, ghosts strategically navigate the maze, creating unique and responsive encounters. 

Analytics: This module systematically logs detailed information about the movements and interactions of each entity within the game. 

# Pacman
The 80s classic Pacman in all its beauty <br/> <br/>
<!-- <img src="Pacman/Media/menu.png" alt="Pacman Menu Screen" width="400"/> -->

**Deployment:**
<br/>

    1. Download the Pacman folder
    
    2. Download Python3 [https://www.python.org/downloads/]
    
    3. Install pygame(2.0.0) [pip3 and homebrew are easy options]
    
    4. In terminal, navigate to the file Pacman.py
    
    5. In terminal type python3 Pacman.py and hit enter
<br/>
