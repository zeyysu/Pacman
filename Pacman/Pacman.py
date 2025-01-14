import pygame
import math
from random import randrange
import random
import copy
import os
import time

import maze

BoardPath = "Assets/boardTextures/"
ElementPath = "Assets/ElementImages/"
TextPath = "Assets/TextImages/"
DataPath = "Assets/Data/"
MusicPath = "Assets/Music/"

pygame.mixer.init()
pygame.init()
print(pygame.mixer.music.get_busy())

# print(maze.board)


originalGameBoard = maze.board
boardTextureNames = maze.tex

margin = 3

boardWidth = maze.boardWidth
boardHeight = maze.boardHeight + margin * 2

boardCenter = (boardHeight // 2, boardWidth // 2) # in y, x format
pacmanStart = (boardCenter[0] + 6, boardCenter[1]) # in y, x format

# add margins for the board
for i in range(margin):
    originalGameBoard.insert(0, [3] * boardWidth)
    originalGameBoard.append([3] * boardWidth)
    boardTextureNames.insert(0, ['empty'] * boardWidth)
    boardTextureNames.append(['empty'] * boardWidth)

# make sure pacman is free
for i in range(10):
    if originalGameBoard[pacmanStart[0]][pacmanStart[1]] == 3:
        pacmanStart = (pacmanStart[0] + 1, pacmanStart[1])

pacmanStart = (pacmanStart[0], pacmanStart[1])

emptySpaces = []
crossways = []
pacmanCrosswayRadius = 5

def getCrossways(pacmanRow, pacmanCol):
    eligible = []
    for i in crossways:
        if abs(i[0] - pacmanRow) + abs(i[1] - pacmanCol) <= pacmanCrosswayRadius:
            eligible.append(i)
    return eligible

for i in range(len(originalGameBoard)):
    for j in range(len(originalGameBoard[i])):
        val = originalGameBoard[i][j]
        if val == 2:
            emptySpaces.append((i, j))

            adjacents = [(i, j + 1), (i, j - 1), (i + 1, j), (i - 1, j)]
            vals = [originalGameBoard[y][x] for y, x in adjacents]
            if vals.count(2) == 3 or vals.count(2) == 4:
                crossways.append((i, j))

berryPos = random.choice(emptySpaces)

def addRandomSpecialTicTaks():
    global originalGameBoard

    def check(special):
        closeness = 8
        # check if any pair is too close
        for i in range(len(special)):
            for j in range(i + 1, len(special)):
                if abs(special[i][0] - special[j][0]) + abs(special[i][1] - special[j][1]) < closeness:
                    return True
        print("Found good special tic-tak placement")
        return False

    for i in range(1000):
        # pick 10 random empty spaces to be special tic-taks
        special = random.choices(emptySpaces, k=10)
        if not check(special):
            break

    for i,j in special:
        originalGameBoard[i][j] = 6

addRandomSpecialTicTaks()

imgDict = {}
def getImage(name):
    if name in imgDict:
        return imgDict[name]
    img = pygame.image.load(name)
    imgDict[name] = img
    return img

gameBoard = copy.deepcopy(originalGameBoard)
ghostColors = ["red", "blue", "pink", "orange"]
spriteRatio = 3/2
square = 25 # Size of each unit square
spriteOffset = square * (1 - spriteRatio) * (1/2)
(width, height) = (len(gameBoard[0]) * square, len(gameBoard) * square) # Game screen
screen = pygame.display.set_mode((width, height))
pygame.display.flip()
musicPlaying = 0 # 0: Chomp, 1: Important, 2: Siren
# pelletColor = (165, 93, 53)
pelletColor = (222, 161, 133)

def getTexture(imageName):
    try:
        tileImage = getImage(BoardPath + imageName + '.png')
    except:
        print("Error: Could not find file", imageName)
        tileImage = getImage(BoardPath + 'empty' + '.png')

    tileImage = pygame.transform.scale(tileImage, (square, square))
    return tileImage


PLAYING_KEYS = {
    "up":[pygame.K_w, pygame.K_UP],
    "down":[pygame.K_s, pygame.K_DOWN],
    "right":[pygame.K_d, pygame.K_RIGHT],
    "left":[pygame.K_a, pygame.K_LEFT]
}

class StragetyAI:
    def calculate_quadrant(self, ghost, pacman):
        if ghost.row <= pacman.row and ghost.col <= pacman.col:
            return "top-left"
        elif ghost.row >= pacman.row and ghost.col <= pacman.col:
            return "bottom-left"
        elif ghost.row <= pacman.row and ghost.col >= pacman.col:
            return "top-right"
        elif ghost.row >= pacman.row and ghost.col >= pacman.col:
            return "bottom-right"
        else:
            return "unknown"
        
    def spawn_new_ghost(self, pacman, ghosts):
        # Example: Spawning new ghost in the quadrant opposite to where most ghosts are
        quadrant_count = {"top-left": 0, "top-right": 0, "bottom-left": 0, "bottom-right": 0}

        for ghost in ghosts:
            quadrant = self.calculate_quadrant(ghost, pacman)
            quadrant_count[quadrant] += 1

        #print(f"Quadrant count: {quadrant_count}")
        # Choose the quadrant with the least ghosts
        min_quadrant = min(quadrant_count, key=quadrant_count.get)

        # Spawn the new ghost in the chosen quadrant
        newGhost = self.spawn_location_based_on_quadrant(min_quadrant, pacman, ghosts)

        # Check if the spawn point is valid and adjust if necessary
        return newGhost
    
    def calculate_distance(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def spawn_location_based_on_quadrant(self, quadrant, pacman, ghosts):
        maze_offset = 10  # Minimum distance from Pac-Man
        print(f"Spawning ghost in {quadrant} quadrant")

        # Define the valid ranges for each quadrant
        valid_ranges = {
            "top-left": (range(0, int(pacman.row)), range(0, int(pacman.col))),
            "bottom-left": (range(int(pacman.row), len(gameBoard) -1), range(0, int(pacman.col))),
            "top-right": (range(0, int(pacman.row)), range(int(pacman.col),len(gameBoard[0]) -1)),
            "bottom-right": (range(int(pacman.row), len(gameBoard) -1), range(int(pacman.col), len(gameBoard[0]) -1)),
        }

        color = ghostColors[len(ghosts)%4]
        spawnLocation = [0, 0]
        newGhost = Ghost(spawnLocation[0], spawnLocation[1], color, len(ghosts))


        # Try to find a valid location in the specified quadrant
        for _ in range(100):  # Limit the number of attempts to avoid infinite loops
            x = random.choice(valid_ranges[quadrant][0])
            y = random.choice(valid_ranges[quadrant][1])

            # Check if the chosen location is at least 10 units away from Pac-Man and is valid
            if newGhost.isValid(x, y) and self.calculate_distance((x, y), (pacman.row, pacman.col)) > maze_offset:
                if all(self.calculate_distance((x,y), (ghost.row, ghost.col)) >= 4 for ghost in ghosts):
                    newGhost.row = x
                    newGhost.col = y
                    return newGhost
            
        while True:
                spawnLocation[0] = randrange(0, len(gameBoard) - 1)
                spawnLocation[1] = randrange(0, len(gameBoard[0]) -1)
                if (self.calculate_distance((spawnLocation[0], spawnLocation[1]), (pacman.row, pacman.col) > maze_offset)) and newGhost.isValid(spawnLocation[0], spawnLocation[1]):
                    newGhost.row = spawnLocation[0]
                    newGhost.col = spawnLocation[1]
                    return newGhost


class Game:
    def __init__(self, level, score):
        self.paused = True
        self.ghostUpdateDelay = 1
        self.ghostUpdateCount = 0
        self.pacmanUpdateDelay = 1
        self.pacmanUpdateCount = 0
        self.tictakChangeDelay = 60
        self.tictakChangeCount = 0
        #spawn ghost every minute
        self.ghostSpawnDelay = 60
        self.ghostLastSpawn = time.time()
        self.ghostsAttacked = False
        self.highScore = self.getHighScore()
        self.score = score
        self.level = level
        self.lives = 3
        self.ghosts = []
        self.strategyAI = StragetyAI()

        # ghosts are spawned after the game is initialized (in the global scope, see game = Game(1, 0) below )
        # self.ghosts = [Ghost(14.0, 13.5, "red", 0), Ghost(17.0, 11.5, "blue", 1), Ghost(17.0, 13.5, "pink", 2), Ghost(17.0, 15.5, "orange", 3)]
        self.pacman = Pacman(pacmanStart[0], pacmanStart[1]) # Center of Second Last Row
        print(f"Pacman spawned at {self.pacman.row}, {self.pacman.col}")
        self.total = self.getCount()
        self.ghostScore = 200
        self.levels = [[350, 250], [150, 450], [150, 450], [0, 600]]
        random.shuffle(self.levels)
        # Level index and Level Progress
        self.ghostStates = [[1, 0], [0, 0], [1, 0], [0, 0]]
        index = 0
        for state in self.ghostStates:
            state[0] = randrange(2)
            state[1] = randrange(self.levels[index][state[0]] + 1)
            index += 1
        self.collected = 0
        self.started = False
        self.gameOver = False
        self.gameOverCounter = 0
        self.points = []
        self.pointsTimer = 10
        # Berry Spawn Time, Berry Death Time, Berry Eaten
        self.berryState = [200, 400, False]
        self.berryLocation = [berryPos[0], berryPos[1]]
        self.berries = ["tile080.png", "tile081.png", "tile082.png", "tile083.png", "tile084.png", "tile085.png", "tile086.png", "tile087.png"]
        self.berriesCollected = []
        self.levelTimer = 0
        self.berryScore = 100
        self.lockedInTimer = 100
        self.lockedIn = True
        self.extraLifeGiven = False
        self.musicPlaying = 0

    # Driver method: The games primary update method
    def update(self):
        # pygame.image.unload()
        # print(self.ghostStates)
        if self.gameOver:
            self.gameOverFunc()
            return
        if self.paused or not self.started:
            self.drawTilesAround(21, 10)
            self.drawTilesAround(21, 11)
            self.drawTilesAround(21, 12)
            self.drawTilesAround(21, 13)
            self.drawTilesAround(21, 14)
            self.drawReady()
            pygame.display.update()
            return

        self.levelTimer += 1
        self.ghostUpdateCount += 1
        self.pacmanUpdateCount += 1
        self.tictakChangeCount += 1
        self.ghostsAttacked = False

        if self.score >= 10000 and not self.extraLifeGiven:
            self.lives += 1
            self.extraLifeGiven = True
            self.forcePlayMusic("pacman_extrapac.wav")

        # Draw tiles around ghosts and pacman
        self.clearBoard()
        for ghost in self.ghosts:
            if ghost.attacked:
                self.ghostsAttacked = True

        # Check if the ghost should case pacman
        index = 0
        for state in self.ghostStates:
            state[1] += 1
            if state[1] >= self.levels[index][state[0]]:
                state[1] = 0
                state[0] += 1
                state[0] %= 2
            index += 1

        index = 0
        for ghost in self.ghosts:
            if not ghost.attacked and not ghost.dead and self.ghostStates[index][0] == 0:
                ghost.pickCrossway(self.pacman.row, self.pacman.col)
            index += 1

        if self.levelTimer == self.lockedInTimer:
            self.lockedIn = False

        self.checkSurroundings
        if self.ghostUpdateCount == self.ghostUpdateDelay:
            for ghost in self.ghosts:
                ghost.update()
            self.ghostUpdateCount = 0

        if self.tictakChangeCount == self.tictakChangeDelay:
            #Changes the color of special Tic-Taks
            self.flipColor()
            self.tictakChangeCount = 0

        if time.time() - self.ghostLastSpawn > self.ghostSpawnDelay:
            self.ghostLastSpawn = time.time()
            self.spawn_ghost()

        if self.pacmanUpdateCount == self.pacmanUpdateDelay:
            self.pacmanUpdateCount = 0
            self.pacman.update()
            self.pacman.col %= len(gameBoard[0])
            if self.pacman.row % 1.0 == 0 and self.pacman.col % 1.0 == 0:
                if gameBoard[int(self.pacman.row)][int(self.pacman.col)] == 2:
                    self.playMusic("munch_1.wav")
                    gameBoard[int(self.pacman.row)][int(self.pacman.col)] = 1
                    self.score += 10
                    self.collected += 1
                    # Fill tile with black
                    pygame.draw.rect(screen, (0, 0, 0), (self.pacman.col * square, self.pacman.row * square, square, square))
                elif gameBoard[int(self.pacman.row)][int(self.pacman.col)] == 5 or gameBoard[int(self.pacman.row)][int(self.pacman.col)] == 6:
                    self.forcePlayMusic("power_pellet.wav")
                    print(f"Pacman ate special Tic-Tak at {self.pacman.row}, {self.pacman.col}")
                    gameBoard[int(self.pacman.row)][int(self.pacman.col)] = 1
                    self.collected += 1
                    # Fill tile with black
                    pygame.draw.rect(screen, (0, 0, 0), (self.pacman.col * square, self.pacman.row * square, square, square))
                    self.score += 50
                    self.ghostScore = 200
                    for ghost in self.ghosts:
                        ghost.attackedCount = 0
                        ghost.setAttacked(True)
                        ghost.setTarget()
                        self.ghostsAttacked = True
        self.checkSurroundings()
        self.highScore = max(self.score, self.highScore)

        global running
        if self.collected == self.total:
            print("New Level")
            self.forcePlayMusic("intermission.wav")
            self.level += 1
            self.newLevel()

        if self.level - 1 == 8: #(self.levels[0][0] + self.levels[0][1]) // 50:
            print("You win", self.level, len(self.levels))
            running = False
        self.softRender()

    # Spawns a ghost
    def spawn_ghost(self):
        newGhost = self.strategyAI.spawn_new_ghost(self.pacman, self.ghosts)
        self.ghosts.append(newGhost)
        self.ghostStates.append([0, 0])
        self.levels.append([350, 250])
        print(f"Spawned {newGhost.color}-colored ghost at {newGhost.row}, {newGhost.col}")
            
    # Render method
    def render(self):
        screen.fill((0, 0, 0)) # Flushes the screen
        # Draws game elements

        for i in range(3, len(gameBoard) - 2):
            for j in range(len(gameBoard[0])):
                if gameBoard[i][j] == 3: # Draw wall
                    tileImage = getTexture(boardTextureNames[i][j])
                    #Display image of tile
                    screen.blit(tileImage, (j * square, i * square, square, square))

                    # pygame.draw.rect(screen, (0, 0, 255),(j * square, i * square, square, square)) # (x, y, width, height)
                elif gameBoard[i][j] == 2: # Draw Tic-Tak
                    pygame.draw.circle(screen, pelletColor,(j * square + square//2, i * square + square//2), square//4)
                elif gameBoard[i][j] == 5: #Black Special Tic-Tak
                    pygame.draw.circle(screen, (0, 0, 0),(j * square + square//2, i * square + square//2), square//2)
                elif gameBoard[i][j] == 6: #White Special Tic-Tak
                    pygame.draw.circle(screen, pelletColor,(j * square + square//2, i * square + square//2), square//2)

        # Draw Sprites
        for ghost in self.ghosts:
            ghost.draw()
        self.pacman.draw()

        self.displayLives()
        self.displayScore()
        # Updates the screen
        pygame.display.update()


    def softRender(self):
        pointsToDraw = []
        for point in self.points:
            if point[3] < self.pointsTimer:
                pointsToDraw.append([point[2], point[0], point[1]])
                point[3] += 1
            else:
                self.points.remove(point)
                self.drawTilesAround(point[0], point[1])

        for point in pointsToDraw:
            self.drawPoints(point[0], point[1], point[2])

        # Draw Sprites
        for ghost in self.ghosts:
            ghost.draw()
        self.pacman.draw()
        self.displayScore()
        self.displayBerries()
        self.displayLives()
        # for point in pointsToDraw:
        #     self.drawPoints(point[0], point[1], point[2])
        self.drawBerry()
        # Updates the screen
        pygame.display.update()

    def playMusic(self, music):
        # return False # Uncomment to disable music
        global musicPlaying
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.unload()
            pygame.mixer.music.load(MusicPath + music)
            pygame.mixer.music.queue(MusicPath + music)
            pygame.mixer.music.play()
            if music == "munch_1.wav":
                musicPlaying = 0
            elif music == "siren_1.wav":
                musicPlaying = 2
            else:
                musicPlaying = 1

    def forcePlayMusic(self, music):
        # return False # Uncomment to disable music
        pygame.mixer.music.unload()
        pygame.mixer.music.load(MusicPath + music)
        pygame.mixer.music.play()
        global musicPlaying
        musicPlaying = 1

    def clearBoard(self):
            # Draw tiles around ghosts and pacman
            for ghost in self.ghosts:
                self.drawTilesAround(ghost.row, ghost.col)
            self.drawTilesAround(self.pacman.row, self.pacman.col)
            self.drawTilesAround(self.berryLocation[0], self.berryLocation[1])
            # Clears Ready! Label
            self.drawTilesAround(20, 10)
            self.drawTilesAround(20, 11)
            self.drawTilesAround(20, 12)
            self.drawTilesAround(20, 13)
            self.drawTilesAround(20, 14)

    def checkSurroundings(self):
        # Check if pacman got killed
        for ghost in self.ghosts:
            if self.touchingPacman(ghost.row, ghost.col) and not ghost.attacked and not ghost.isDead():
                print(f"Pacman got killed by {ghost.color} ghost")
                if self.lives == 1:
                    print("Pacman lose")
                    self.forcePlayMusic("death_1.wav")
                    self.gameOver = True
                    #Removes the ghosts from the screen
                    for ghost in self.ghosts:
                        self.drawTilesAround(ghost.row, ghost.col)
                    self.drawTilesAround(self.pacman.row, self.pacman.col)
                    self.pacman.draw()
                    pygame.display.update()
                    pause(10000000)
                    return
                self.started = False
                self.forcePlayMusic("pacman_death.wav")
                reset()
            elif self.touchingPacman(ghost.row, ghost.col) and ghost.isAttacked() and not ghost.isDead():
                print(f"Pacman killed {ghost.color} ghost")
                ghost.setDead(True)
                ghost.setTarget()
                ghost.ghostSpeed = 1
                ghost.row = math.floor(ghost.row)
                ghost.col = math.floor(ghost.col)
                self.score += self.ghostScore
                self.points.append([ghost.row, ghost.col, self.ghostScore, 0])
                self.ghostScore *= 2
                self.forcePlayMusic("eat_ghost.wav")
                pause(10000000)
        if self.touchingPacman(self.berryLocation[0], self.berryLocation[1]) and not self.berryState[2] and self.levelTimer in range(self.berryState[0], self.berryState[1]):
            print("Pacman ate berry")
            self.berryState[2] = True
            self.score += self.berryScore
            self.points.append([self.berryLocation[0], self.berryLocation[1], self.berryScore, 0])
            self.berriesCollected.append(self.berries[(self.level - 1) % 8])
            self.forcePlayMusic("eat_fruit.wav")
    # Displays the current score
    def displayScore(self):
        textOneUp = ["tile033.png", "tile021.png", "tile016.png"]
        textHighScore = ["tile007.png", "tile008.png", "tile006.png", "tile007.png", "tile015.png", "tile019.png", "tile002.png", "tile014.png", "tile018.png", "tile004.png"]
        index = 0
        scoreStart = 5
        highScoreStart = 11
        for i in range(scoreStart, scoreStart+len(textOneUp)):
            tileImage = getImage(TextPath + textOneUp[index])
            tileImage = pygame.transform.scale(tileImage, (square, square))
            screen.blit(tileImage, (i * square, 4, square, square))
            index += 1
        score = str(self.score)
        if score == "0":
            score = "00"
        index = 0
        for i in range(0, len(score)):
            digit = int(score[i])
            tileImage = getImage(TextPath + "tile0" + str(32 + digit) + ".png")
            tileImage = pygame.transform.scale(tileImage, (square, square))
            screen.blit(tileImage, ((scoreStart + 2 + index) * square, square + 4, square, square))
            index += 1

        index = 0
        for i in range(highScoreStart, highScoreStart+len(textHighScore)):
            tileImage = getImage(TextPath + textHighScore[index])
            tileImage = pygame.transform.scale(tileImage, (square, square))
            screen.blit(tileImage, (i * square, 4, square, square))
            index += 1

        highScore = str(self.highScore)
        if highScore == "0":
            highScore = "00"
        index = 0
        for i in range(0, len(highScore)):
            digit = int(highScore[i])
            tileImage = getImage(TextPath + "tile0" + str(32 + digit) + ".png")
            tileImage = pygame.transform.scale(tileImage, (square, square))
            screen.blit(tileImage, ((highScoreStart + 6 + index) * square, square + 4, square, square))
            index += 1

    def drawBerry(self):
        if self.levelTimer in range(self.berryState[0], self.berryState[1]) and not self.berryState[2]:
            # print("here")
            berryImage = getImage(ElementPath + self.berries[(self.level - 1) % 8])
            berryImage = pygame.transform.scale(berryImage, (int(square * spriteRatio), int(square * spriteRatio)))
            screen.blit(berryImage, (self.berryLocation[1] * square, self.berryLocation[0] * square, square, square))


    def drawPoints(self, points, row, col):
        pointStr = str(points)
        index = 0
        for i in range(len(pointStr)):
            digit = int(pointStr[i])
            tileImage = getImage(TextPath + "tile" + str(224 + digit) + ".png")
            tileImage = pygame.transform.scale(tileImage, (square//2, square//2))
            screen.blit(tileImage, ((col) * square + (square//2 * index), row * square - 20, square//2, square//2))
            index += 1

    def drawReady(self):
        ready = ["tile274.png", "tile260.png", "tile256.png", "tile259.png", "tile281.png", "tile283.png"]
        for i in range(len(ready)):
            letter = getImage(TextPath + ready[i])
            letter = pygame.transform.scale(letter, (int(square), int(square)))
            screen.blit(letter, ((11 + i) * square, 20 * square, square, square))

    def gameOverFunc(self):
        global running
        if self.gameOverCounter == 12:
            running = False
            self.recordHighScore()
            return

        # Resets the screen around pacman
        self.drawTilesAround(self.pacman.row, self.pacman.col)

        # Draws new image
        pacmanImage = getImage(ElementPath + "tile" + str(116 + self.gameOverCounter) + ".png")
        pacmanImage = pygame.transform.scale(pacmanImage, (int(square * spriteRatio), int(square * spriteRatio)))
        screen.blit(pacmanImage, (self.pacman.col * square + spriteOffset, self.pacman.row * square + spriteOffset, square, square))
        pygame.display.update()
        pause(5000000)
        self.gameOverCounter += 1

    def displayLives(self):
        for i in range(self.lives - 1):
            lifeImage = getImage(ElementPath + "tile054.png")
            lifeImage = pygame.transform.scale(lifeImage, (int(square * spriteRatio), int(square * spriteRatio)))
            location = [boardHeight-2, 2*i+1]
            screen.blit(lifeImage, (location[1] * square, location[0] * square - spriteOffset, square, square))

    def displayBerries(self):
        firstBerrie = [boardHeight -2, boardWidth - 2]
        for i in range(len(self.berriesCollected)):
            berrieImage = getImage(ElementPath + self.berriesCollected[i])
            berrieImage = pygame.transform.scale(berrieImage, (int(square * spriteRatio), int(square * spriteRatio)))
            screen.blit(berrieImage, ((firstBerrie[1] - (2*i)) * square, firstBerrie[0] * square + 5, square, square))

    def touchingPacman(self, row, col):
        if row - 0.5 <= self.pacman.row and row >= self.pacman.row and col == self.pacman.col:
            return True
        elif row + 0.5 >= self.pacman.row and row <= self.pacman.row and col == self.pacman.col:
            return True
        elif row == self.pacman.row and col - 0.5 <= self.pacman.col and col >= self.pacman.col:
            return True
        elif row == self.pacman.row and col + 0.5 >= self.pacman.col and col <= self.pacman.col:
            return True
        elif row == self.pacman.row and col == self.pacman.col:
            return True
        return False

    def newLevel(self):
        reset(True)
        self.lives = 3
        print("New Level")
        print(f"Pacman lives: {self.lives}")
        self.collected = 0
        self.started = False
        self.berryState = [200, 400, False]
        self.levelTimer = 0
        self.lockedIn = True
        for level in self.levels:
            level[0] = min((level[0] + level[1]) - 100, level[0] + 50)
            level[1] = max(100, level[1] - 50)
        random.shuffle(self.levels)
        index = 0
        for state in self.ghostStates:
            state[0] = randrange(2)
            state[1] = randrange(self.levels[index][state[0]] + 1)
            index += 1
        global gameBoard
        gameBoard = copy.deepcopy(originalGameBoard)
        self.render()

    def drawTilesAround(self, row, col):
        row = math.floor(row)
        col = math.floor(col)
        for i in range(row-2, row+3):
            for j in range(col-2, col+3):
                if i >= 3 and i < len(gameBoard) - 2 and j >= 0 and j < len(gameBoard[0]):
                    imageName = str(((i - 3) * len(gameBoard[0])) + j)
                    if len(imageName) == 1:
                        imageName = "00" + imageName
                    elif len(imageName) == 2:
                         imageName = "0" + imageName
                    # Get image of desired tile
                    imageName = "tile" + imageName + ".png"
                    tileImage = getTexture(boardTextureNames[i][j])
                    #Display image of tile
                    screen.blit(tileImage, (j * square, i * square, square, square))

                    if gameBoard[i][j] == 2: # Draw Tic-Tak
                        pygame.draw.circle(screen, pelletColor,(j * square + square//2, i * square + square//2), square//4)
                    elif gameBoard[i][j] == 5: #Black Special Tic-Tak
                        pygame.draw.circle(screen, (0, 0, 0),(j * square + square//2, i * square + square//2), square//2)
                    elif gameBoard[i][j] == 6: #White Special Tic-Tak
                        pygame.draw.circle(screen, pelletColor,(j * square + square//2, i * square + square//2), square//2)

    # Flips Color of Special Tic-Taks
    def flipColor(self):
        global gameBoard
        for i in range(3, len(gameBoard) - 2):
            for j in range(len(gameBoard[0])):
                if gameBoard[i][j] == 5:
                    gameBoard[i][j] = 6
                    pygame.draw.circle(screen, pelletColor,(j * square + square//2, i * square + square//2), square//2)
                elif gameBoard[i][j] == 6:
                    gameBoard[i][j] = 5
                    pygame.draw.circle(screen, (0, 0, 0),(j * square + square//2, i * square + square//2), square//2)

    def getCount(self):
        total = 0
        for i in range(3, len(gameBoard) - 2):
            for j in range(len(gameBoard[0])):
                if gameBoard[i][j] == 2 or gameBoard[i][j] == 5 or gameBoard[i][j] == 6:
                    total += 1
        return total

    def getHighScore(self):
        file = open(DataPath + "HighScore.txt", "r")
        highScore = int(file.read())
        file.close()
        return highScore

    def recordHighScore(self):
        file = open(DataPath + "HighScore.txt", "w").close()
        file = open(DataPath + "HighScore.txt", "w+")
        file.write(str(self.highScore))
        file.close()

class Pacman:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.mouthOpen = False
        self.pacSpeed = 1/4
        self.mouthChangeDelay = 5
        self.mouthChangeCount = 0
        self.dir = 0 # 0: North, 1: East, 2: South, 3: West
        self.newDir = 0

    def update(self):
        if self.newDir == 0:
            if canMove(math.floor(self.row - self.pacSpeed), self.col) and self.col % 1.0 == 0:
                self.row -= self.pacSpeed
                if(self.dir != self.newDir):
                    self.dir = self.newDir
                    print(f"Pacman changed direction to up")
                return
        elif self.newDir == 1:
            if canMove(self.row, math.ceil(self.col + self.pacSpeed)) and self.row % 1.0 == 0:
                self.col += self.pacSpeed
                if(self.dir != self.newDir):
                    self.dir = self.newDir
                    print(f"Pacman changed direction to right")
                return
        elif self.newDir == 2:
            if canMove(math.ceil(self.row + self.pacSpeed), self.col) and self.col % 1.0 == 0:
                self.row += self.pacSpeed
                if(self.dir != self.newDir):
                    self.dir = self.newDir
                    print(f"Pacman changed direction to down")
                return
        elif self.newDir == 3:
            if canMove(self.row, math.floor(self.col - self.pacSpeed)) and self.row % 1.0 == 0:
                self.col -= self.pacSpeed
                if(self.dir != self.newDir):       
                    self.dir = self.newDir         
                    print(f"Pacman changed direction to left")  
                return

        if self.dir == 0:
            if canMove(math.floor(self.row - self.pacSpeed), self.col) and self.col % 1.0 == 0:
                self.row -= self.pacSpeed
        elif self.dir == 1:
            if canMove(self.row, math.ceil(self.col + self.pacSpeed)) and self.row % 1.0 == 0:
                self.col += self.pacSpeed
        elif self.dir == 2:
            if canMove(math.ceil(self.row + self.pacSpeed), self.col) and self.col % 1.0 == 0:
                self.row += self.pacSpeed
        elif self.dir == 3:
            if canMove(self.row, math.floor(self.col - self.pacSpeed)) and self.row % 1.0 == 0:
                self.col -= self.pacSpeed

    # Draws pacman based on his current state
    def draw(self):
        if not game.started:
            pacmanImage = getImage(ElementPath + "tile112.png")
            pacmanImage = pygame.transform.scale(pacmanImage, (int(square * spriteRatio), int(square * spriteRatio)))
            screen.blit(pacmanImage, (self.col * square + spriteOffset, self.row * square + spriteOffset, square, square))
            return

        if self.mouthChangeCount == self.mouthChangeDelay:
            self.mouthChangeCount = 0
            self.mouthOpen = not self.mouthOpen
        self.mouthChangeCount += 1
        # pacmanImage = getImage("Sprites/tile049.png")
        if self.dir == 0:
            if self.mouthOpen:
                pacmanImage = getImage(ElementPath + "tile049.png")
            else:
                pacmanImage = getImage(ElementPath + "tile051.png")
        elif self.dir == 1:
            if self.mouthOpen:
                pacmanImage = getImage(ElementPath + "tile052.png")
            else:
                pacmanImage = getImage(ElementPath + "tile054.png")
        elif self.dir == 2:
            if self.mouthOpen:
                pacmanImage = getImage(ElementPath + "tile053.png")
            else:
                pacmanImage = getImage(ElementPath + "tile055.png")
        elif self.dir == 3:
            if self.mouthOpen:
                pacmanImage = getImage(ElementPath + "tile048.png")
            else:
                pacmanImage = getImage(ElementPath + "tile050.png")

        pacmanImage = pygame.transform.scale(pacmanImage, (int(square * spriteRatio), int(square * spriteRatio)))
        screen.blit(pacmanImage, (self.col * square + spriteOffset, self.row * square + spriteOffset, square, square))

        # eligiblePoints = getCrossways(self.row, self.col)
        # for point in eligiblePoints:
        #     pygame.draw.circle(screen, (255, 0, 0),(point[1] * square + square//2, point[0] * square + square//2), square//2)

class Ghost:
    def __init__(self, row, col, color, changeFeetCount):
        self.row = row
        self.col = col
        self.attacked = False
        self.color = color
        self.dir = randrange(4)
        self.dead = False
        self.changeFeetCount = changeFeetCount
        self.changeFeetDelay = 5
        self.target = [-1, -1]
        self.ghostSpeed = 1/4
        self.lastLoc = [-1, -1]
        self.attackedTimer = 240
        self.attackedCount = 0
        self.deathTimer = 150
        self.deathCount = 0

        self.followedPoint = (-1, -1)
        self.followingPacman = False

    def followPoint(self, point, followingPacman=False):

        if(followingPacman and not self.followingPacman):
            print(f"Ghost {self.color} is now following pacman")

        self.followingPacman = followingPacman
        
        if self.followedPoint == point:
            return
        
        if point != (-1, -1):
            if not followingPacman:
                print(f"Ghost {self.color} is now following {point}")
        else:
            print(f"Ghost {self.color} is now moving randomly")

        self.followedPoint = point
        self.target = [point[0], point[1]]

    def getVisibleCrossways(self, pacmanRow, pacmanCol):
        visibleCrossways = []
        allCrossways = getCrossways(pacmanRow, pacmanCol)
        for crossway in allCrossways:
            if abs(crossway[0] - self.row) + abs(crossway[1] - self.col) <= 10:
                visibleCrossways.append(crossway)
        return visibleCrossways

    def pickCrossway(self, pacmanRow, pacmanCol):

        if abs(self.row - pacmanRow) + abs(self.col - pacmanCol) <= pacmanCrosswayRadius:
            self.followPoint((pacmanRow, pacmanCol), True)
            return

        visibleCrossways = self.getVisibleCrossways(pacmanRow, pacmanCol)
        if len(visibleCrossways) == 0:
            self.followPoint((-1, -1))
            return

        closest = visibleCrossways[0]
        for crossway in visibleCrossways:
            if abs(crossway[0] - self.row) + abs(crossway[1] - self.col) < abs(closest[0] - self.row) + abs(closest[1] - self.col):
                closest = crossway


        self.followPoint(closest)

    def update(self):
        # print(self.row, self.col)
        if self.target == [-1, -1] or (self.row == self.target[0] and self.col == self.target[1]) or gameBoard[int(self.row)][int(self.col)] == 4 or self.dead:
            self.setTarget()
        self.setDir()
        self.move()

        if self.attacked:
            self.attackedCount += 1

        if self.attacked and not self.dead:
            self.ghostSpeed = 1/8

        if self.attackedCount == self.attackedTimer and self.attacked:
            if not self.dead:
                self.ghostSpeed = 1/4
                self.row = math.floor(self.row)
                self.col = math.floor(self.col)

            self.attackedCount = 0
            self.attacked = False
            self.setTarget()

        #if self.dead and gameBoard[self.row][self.col] == 4:
        if self.dead:
            self.deathCount += 1
            self.attacked = False
            if self.deathCount == self.deathTimer:
                self.deathCount = 0
                self.dead = False
                print(f"Ghost {self.color} respawned")
                self.ghostSpeed = 1/4

    def draw(self): # Ghosts states: Alive, Attacked, Dead Attributes: Color, Direction, Location
        ghostImage = getImage(ElementPath + "tile152.png")
        currentDir = ((self.dir + 3) % 4) * 2
        if self.changeFeetCount == self.changeFeetDelay:
            self.changeFeetCount = 0
            currentDir += 1
        self.changeFeetCount += 1
        if self.dead:
            tileNum = 152 + currentDir
            ghostImage = getImage(ElementPath + "tile" + str(tileNum) + ".png")
        elif self.attacked:
            if self.attackedTimer - self.attackedCount < self.attackedTimer//3:
                if (self.attackedTimer - self.attackedCount) % 31 < 26:
                    ghostImage = getImage(ElementPath + "tile0" + str(70 + (currentDir - (((self.dir + 3) % 4) * 2))) + ".png")
                else:
                    ghostImage = getImage(ElementPath + "tile0" + str(72 + (currentDir - (((self.dir + 3) % 4) * 2))) + ".png")
            else:
                ghostImage = getImage(ElementPath + "tile0" + str(72 + (currentDir - (((self.dir + 3) % 4) * 2))) + ".png")
        else:
            if self.color == "blue":
                tileNum = 136 + currentDir
                ghostImage = getImage(ElementPath + "tile" + str(tileNum) + ".png")
            elif self.color == "pink":
                tileNum = 128 + currentDir
                ghostImage = getImage(ElementPath + "tile" + str(tileNum) + ".png")
            elif self.color == "orange":
                tileNum = 144 + currentDir
                ghostImage = getImage(ElementPath + "tile" + str(tileNum) + ".png")
            elif self.color == "red":
                tileNum = 96 + currentDir
                if tileNum < 100:
                    ghostImage = getImage(ElementPath + "tile0" + str(tileNum) + ".png")
                else:
                    ghostImage = getImage(ElementPath + "tile" + str(tileNum) + ".png")

        ghostImage = pygame.transform.scale(ghostImage, (int(square * spriteRatio), int(square * spriteRatio)))
        screen.blit(ghostImage, (self.col * square + spriteOffset, self.row * square + spriteOffset, square, square))

    def isValidTwo(self, cRow, cCol, dist, visited):
        if cRow < 3 or cRow >= len(gameBoard) - 5 or cCol < 0 or cCol >= len(gameBoard[0]) or gameBoard[cRow][cCol] == 3:
            return False
        elif visited[cRow][cCol] <= dist:
            return False
        return True

    def isValid(self, cRow, cCol):
        if cCol < 0 or cCol > len(gameBoard[0]) - 1:
            return True
        for ghost in game.ghosts:
            if ghost.row == cRow and ghost.col == cCol and not self.dead:
                return False
        if not ghostGate.count([cRow, cCol]) == 0:
            if self.dead and self.row < cRow:
                return True
            elif self.row > cRow and not self.dead and not self.attacked and not game.lockedIn:
                return True
            else:
                return False
        if gameBoard[cRow][cCol] == 3:
            return False
        return True

    def setDir(self): #Very inefficient || can easily refactor
        # BFS search -> Not best route but a route none the less
        dirs = [[0, -self.ghostSpeed, 0],
                [1, 0, self.ghostSpeed],
                [2, self.ghostSpeed, 0],
                [3, 0, -self.ghostSpeed]
        ]
        random.shuffle(dirs)
        best = 10000
        bestDir = -1
        for newDir in dirs:
            if self.calcDistance(self.target, [self.row + newDir[1], self.col + newDir[2]]) < best:
                if not (self.lastLoc[0] == self.row + newDir[1] and self.lastLoc[1] == self.col + newDir[2]):
                    if newDir[0] == 0 and self.col % 1.0 == 0:
                        if self.isValid(math.floor(self.row + newDir[1]), int(self.col + newDir[2])):
                            bestDir = newDir[0]
                            best = self.calcDistance(self.target, [self.row + newDir[1], self.col + newDir[2]])
                    elif newDir[0] == 1 and self.row % 1.0 == 0:
                        if self.isValid(int(self.row + newDir[1]), math.ceil(self.col + newDir[2])):
                            bestDir = newDir[0]
                            best = self.calcDistance(self.target, [self.row + newDir[1], self.col + newDir[2]])
                    elif newDir[0] == 2 and self.col % 1.0 == 0:
                        if self.isValid(math.ceil(self.row + newDir[1]), int(self.col + newDir[2])):
                            bestDir = newDir[0]
                            best = self.calcDistance(self.target, [self.row + newDir[1], self.col + newDir[2]])
                    elif newDir[0] == 3 and self.row % 1.0 == 0:
                        if self.isValid(int(self.row + newDir[1]), math.floor(self.col + newDir[2])):
                            bestDir = newDir[0]
                            best = self.calcDistance(self.target, [self.row + newDir[1], self.col + newDir[2]])
        self.dir = bestDir

    def calcDistance(self, a, b):
        dR = a[0] - b[0]
        dC = a[1] - b[1]
        return math.sqrt((dR * dR) + (dC * dC))

    def setTarget(self):
        if gameBoard[int(self.row)][int(self.col)] == 4 and not self.dead:
            self.target = [ghostGate[0][0] - 1, ghostGate[0][1]+1]
            return
        elif gameBoard[int(self.row)][int(self.col)] == 4 and self.dead:
            self.target = [self.row, self.col]
        elif self.dead:
            self.target = [14, 13]
            return

        # Records the quadrants of each ghost's target
        quads = [0, 0, 0, 0]
        for ghost in game.ghosts:
            # if ghost.target[0] == self.row and ghost.col == self.col:
            #     continue
            if ghost.target[0] <= 15 and ghost.target[1] >= 13:
                quads[0] += 1
            elif ghost.target[0] <= 15 and ghost.target[1] < 13:
                quads[1] += 1
            elif ghost.target[0] > 15 and ghost.target[1] < 13:
                quads[2] += 1
            elif ghost.target[0]> 15 and ghost.target[1] >= 13:
                quads[3] += 1

        # Finds a target that will keep the ghosts dispersed
        while True:
            self.target = [randrange(boardHeight), randrange(boardWidth)]
            quad = 0
            if self.target[0] <= 15 and self.target[1] >= 13:
                quad = 0
            elif self.target[0] <= 15 and self.target[1] < 13:
                quad = 1
            elif self.target[0] > 15 and self.target[1] < 13:
                quad = 2
            elif self.target[0] > 15 and self.target[1] >= 13:
                quad = 3
            if not gameBoard[self.target[0]][self.target[1]] == 3 and not gameBoard[self.target[0]][self.target[1]] == 4:
                break
            elif quads[quad] == 0:
                break

    def move(self):
        # print(self.target)
        self.lastLoc = [self.row, self.col]
        if self.dir == 0:
            self.row -= self.ghostSpeed
        elif self.dir == 1:
            self.col += self.ghostSpeed
        elif self.dir == 2:
            self.row += self.ghostSpeed
        elif self.dir == 3:
            self.col -= self.ghostSpeed

        # Incase they go through the middle tunnel
        self.col = self.col % len(gameBoard[0])
        if self.col < 0:
            self.col = len(gameBoard[0]) - 0.5



    def setAttacked(self, isAttacked):
        self.attacked = isAttacked

    def isAttacked(self):
        return self.attacked

    def setDead(self, isDead):
        self.dead = isDead

    def isDead(self):
        return self.dead

game = Game(1, 0)
ghostsafeArea = [15, 13] # The location the ghosts escape to when attacked
ghostGate = [[15, 13], [15, 14]]
game.spawn_ghost()
game.spawn_ghost()
game.spawn_ghost()
game.spawn_ghost()

def canMove(row, col):
    
    if col == -1 or col == len(gameBoard[0]):
        return True
    if gameBoard[int(row)][int(col)] == 7:
        return True
    if gameBoard[int(row)][int(col)] != 3:
        return True
    return False

# Reset after death
def reset(newLevel = False):
    print("Resetting level")
    global game
    #game.ghosts = [Ghost(14.0, 13.5, "red", 0), Ghost(17.0, 11.5, "blue", 1), Ghost(17.0, 13.5, "pink", 2), Ghost(17.0, 15.5, "orange", 3)]
    # game.spawn_ghost()
    # game.spawn_ghost()
    # game.spawn_ghost()
    # game.spawn_ghost()
    game.pacman = Pacman(pacmanStart[0], pacmanStart[1])
    game.lives -= 1
    print(f"Pacman spawned at {game.pacman.row}, {game.pacman.col}")
    length = len(game.ghosts)
    if(newLevel):
        length = 4
        game.ghostLastSpawn = time.time()
    else:
        print(f"Pacman lives: {game.lives}")
    game.ghosts = []
    for i in range(length):
        game.spawn_ghost()
    for ghost in game.ghosts:
        ghost.setTarget()
    game.paused = True
    game.render()

def displayLaunchScreen():
    # Draw Pacman Title
    pacmanTitle = ["tile016.png", "tile000.png", "tile448.png", "tile012.png", "tile000.png", "tile013.png"]
    for i in range(len(pacmanTitle)):
        letter = getImage(TextPath + pacmanTitle[i])
        letter = pygame.transform.scale(letter, (int(square * 4), int(square * 4)))
        screen.blit(letter, ((2 + 4 * i) * square, 2 * square, square, square))

    # Draw Character / Nickname
    characterTitle = [
        #Character
        "tile002.png", "tile007.png", "tile000.png", "tile018.png", "tile000.png", "tile002.png", "tile020.png", "tile004.png", "tile018.png",
        # /
        "tile015.png", "tile042.png", "tile015.png",
        # Nickname
        "tile013.png", "tile008.png", "tile002.png", "tile010.png", "tile013.png", "tile000.png", "tile012.png", "tile004.png"
    ]
    for i in range(len(characterTitle)):
        letter = getImage(TextPath + characterTitle[i])
        letter = pygame.transform.scale(letter, (int(square), int(square)))
        screen.blit(letter, ((4 + i) * square, 10 * square, square, square))

    #Draw Characters and their Nickname
    characters = [
        # Red Ghost
        [
            "tile449.png", "tile015.png", "tile107.png", "tile015.png", "tile083.png", "tile071.png", "tile064.png", "tile067.png", "tile078.png", "tile087.png",
            "tile015.png", "tile015.png", "tile015.png", "tile015.png",
            "tile108.png", "tile065.png", "tile075.png", "tile072.png", "tile077.png", "tile074.png", "tile089.png", "tile108.png"
        ],
        # Pink Ghost
        [
            "tile450.png", "tile015.png", "tile363.png", "tile015.png", "tile339.png", "tile336.png", "tile324.png", "tile324.png", "tile323.png", "tile345.png",
            "tile015.png", "tile015.png", "tile015.png", "tile015.png",
            "tile364.png", "tile336.png", "tile328.png", "tile333.png", "tile330.png", "tile345.png", "tile364.png"
        ],
        # Blue Ghost
        [
            "tile452.png", "tile015.png", "tile363.png", "tile015.png", "tile193.png", "tile192.png", "tile211.png", "tile199.png", "tile197.png", "tile213.png", "tile203.png",
            "tile015.png", "tile015.png", "tile015.png",
            "tile236.png", "tile200.png", "tile205.png", "tile202.png", "tile217.png", "tile236.png"
        ],
        # Orange Ghost
        [
            "tile451.png", "tile015.png", "tile363.png", "tile015.png", "tile272.png", "tile270.png", "tile266.png", "tile260.png", "tile281.png",
            "tile015.png", "tile015.png", "tile015.png", "tile015.png", "tile015.png",
            "tile300.png", "tile258.png", "tile267.png", "tile281.png", "tile259.png", "tile260.png", "tile300.png"
        ]
    ]
    for i in range(len(characters)):
        for j in range(len(characters[i])):
            if j == 0:
                    letter = getImage(TextPath + characters[i][j])
                    letter = pygame.transform.scale(letter, (int(square * spriteRatio), int(square * spriteRatio)))
                    screen.blit(letter, ((2 + j) * square - square//2, (12 + 2 * i) * square - square//3, square, square))
            else:
                letter = getImage(TextPath + characters[i][j])
                letter = pygame.transform.scale(letter, (int(square), int(square)))
                screen.blit(letter, ((2 + j) * square, (12 + 2 * i) * square, square, square))
    # Draw Pacman and Ghosts
    event = ["tile449.png", "tile015.png", "tile452.png", "tile015.png",  "tile015.png", "tile448.png", "tile453.png", "tile015.png", "tile015.png", "tile015.png",  "tile453.png"]
    for i in range(len(event)):
        character = getImage(TextPath + event[i])
        character = pygame.transform.scale(character, (int(square * 2), int(square * 2)))
        screen.blit(character, ((4 + i * 2) * square, 24 * square, square, square))
    # Draw PlatForm from Pacman and Ghosts
    wall = ["tile454.png", "tile454.png", "tile454.png", "tile454.png", "tile454.png", "tile454.png", "tile454.png", "tile454.png", "tile454.png", "tile454.png", "tile454.png", "tile454.png", "tile454.png", "tile454.png", "tile454.png"]
    for i in range(len(wall)):
        platform = getImage(TextPath + wall[i])
        platform = pygame.transform.scale(platform, (int(square * 2), int(square * 2)))
        screen.blit(platform, ((i * 2) * square, 26 * square, square, square))
    # Credit myself
    credit = ["tile003.png", "tile004.png", "tile022.png", "tile008.png", "tile013.png", "tile015.png", "tile011.png", "tile004.png", "tile000.png", "tile012.png", "tile025.png", "tile015.png", "tile418.png", "tile416.png", "tile418.png", "tile416.png"]
    for i in range(len(credit)):
        letter = getImage(TextPath + credit[i])
        letter = pygame.transform.scale(letter, (int(square), int(square)))
        screen.blit(letter, ((6 + i) * square, 30 * square, square, square))
    # Press Space to Play
    instructions = ["tile016.png", "tile018.png", "tile004.png", "tile019.png", "tile019.png", "tile015.png", "tile019.png", "tile016.png", "tile000.png", "tile002.png", "tile004.png", "tile015.png", "tile020.png", "tile014.png", "tile015.png", "tile016.png", "tile011.png", "tile000.png", "tile025.png"]
    for i in range(len(instructions)):
        letter = getImage(TextPath + instructions[i])
        letter = pygame.transform.scale(letter, (int(square), int(square)))
        screen.blit(letter, ((4.5 + i) * square, 35 * square - 10, square, square))

    pygame.display.update()

running = True
onLaunchScreen = True
displayLaunchScreen()
clock = pygame.time.Clock()

def pause(time):
    cur = 0
    while not cur == time:
        cur += 1

while running:
    clock.tick(40)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            game.recordHighScore()
        elif event.type == pygame.KEYDOWN:
            game.paused = False
            game.started = True
            if event.key in PLAYING_KEYS["up"]:
                if not onLaunchScreen:
                    game.pacman.newDir = 0
            elif event.key in PLAYING_KEYS["right"]:
                if not onLaunchScreen:
                    game.pacman.newDir = 1
            elif event.key in PLAYING_KEYS["down"]:
                if not onLaunchScreen:
                    game.pacman.newDir = 2
            elif event.key in PLAYING_KEYS["left"]:
                if not onLaunchScreen:
                    game.pacman.newDir = 3
            elif event.key == pygame.K_SPACE:
                if onLaunchScreen:
                    onLaunchScreen = False
                    game.paused = True
                    game.started = False
                    game.render()
                    pygame.mixer.music.load(MusicPath + "pacman_beginning.wav")
                    pygame.mixer.music.play()
                    musicPlaying = 1
            elif event.key == pygame.K_q:
                running = False
                game.recordHighScore()

    if not onLaunchScreen:
        game.update()
