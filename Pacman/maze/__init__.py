import random

mazeSizeW = 5
mazeSizeH = 6

ADD_COMMON_PATHS = False

mazeSizeTotal = (mazeSizeW * mazeSizeH)

def getIndex(i, j):
    return i * mazeSizeW + j

def getCoord(index):
    return (index // mazeSizeW, index % mazeSizeW)

nodes = [i for i in range(mazeSizeTotal)]
adj = [[] for _ in range(mazeSizeTotal)]
edges = []
edgeMap = {}
edgeMapReverse = {}

# i,j -> i*mazeSizeW+j -> y,x

edgeId = 0
def addEdge(u, v):
    global edgeId
    edges.append({
        "from": u,
        "to": v,
        "id": edgeId 
    })
    edgeMap[(u,v)] = edgeId
    edgeMap[(v,u)] = edgeId
    print("edge:", u, v, edgeId)
    edgeMapReverse[edgeId] = (u,v)

    edgeId += 1 
    adj[u].append(v)
    adj[v].append(u)

for i in range(mazeSizeH):
    for j in range(mazeSizeW):
        if i < mazeSizeH-1:
            addEdge(getIndex(i,j), getIndex(i+1,j))
        if j < mazeSizeW-1:
            addEdge(getIndex(i,j), getIndex(i,j+1))

def getAdj(node):
    return adj[node]

def getRandomAdj(node):
    # print("node adj:", adj[node], "random:", random.shuffle(adj[node]), adj[node])
    random.shuffle(adj[node])
    return getAdj(node)

# condition 1: no direct square -> remove one random edge
# condition 2: no dead end -> add one random edge
# condition 3: all nodes connected

# strategy: random dfs walk

def dfsWalk(prev, node, visited, path):
    visited[node] = True
    if(prev != None):
        path.append(edgeMap[(prev, node)])
    for nextNode in getRandomAdj(node):
        if not visited[nextNode]:
            dfsWalk(node, nextNode, visited, path)

path = []
visited = [False for _ in range(mazeSizeTotal)]
dfsWalk(None, 0, visited, path)
print(path)


def getCommonPaths():
    halfH = mazeSizeH // 2
    halfW = mazeSizeW // 2
    newPaths = []
    for i in range(mazeSizeH):
        for j in range(mazeSizeW):
            if i==halfH:
                node = getIndex(i,j)
                nextNode = getIndex(i,j+1)
                if (node, nextNode) in edgeMap:
                    newPaths.append(edgeMap[(node, nextNode)])
            if j==halfW:
                node = getIndex(i,j)
                nextNode = getIndex(i+1,j)
                if (node, nextNode) in edgeMap:
                    newPaths.append(edgeMap[(node, nextNode)])
    
    return newPaths
print("common:", getCommonPaths())
if ADD_COMMON_PATHS:
    path = getCommonPaths() + path

up = 0b010010000
down = 0b000010010
left = 0b000110000
right = 0b000011000

def printOutput(output):
    print([bin(i) for i in output])
    for i in range(mazeSizeH*3):
        for j in range(mazeSizeW*3):
            celly, cellx = i // 3, j // 3
            pixel = output[getIndex(celly, cellx)] & 1<<(8-(i % 3 * 3 + j % 3))
            print("o" if pixel else ".", end="")
        print()

class Output():
    sizeW: int
    sizeH: int
    def __init__(self, sizeW, sizeH, output):
        self.sizeW = sizeW
        self.sizeH = sizeH
        if output != None:
            self.output = output
        else:
            self.output = [0b000000000 for _ in range(sizeW*sizeH)]

    def setPixel(self, x, y, bitCode):
        self.output[y*self.sizeW+x] = bitCode
    
    def addRight(self, amount):
        for _ in range(amount):
            for row in range(1, self.sizeH+1):
                where = row * (self.sizeW+1) - 1
                self.output.insert(where, 0b000000000)
            self.sizeW += 1

    def shiftRight(self, amount):
        for _ in range(amount):
            for row in range(self.sizeH):
                where = row * (self.sizeW+1)
                self.output.insert(where, 0b000000000)
            self.sizeW += 1
    
    def addBottom(self, amount):
        for _ in range(amount):
            for _ in range(self.sizeW):
                self.output.append(0b000000000)
        self.sizeH += amount

    def shiftBottom(self, amount):
        for _ in range(amount):
            for _ in range(self.sizeW):
                self.output.insert(0, 0b000000000)
        self.sizeH += amount

    def getIndex(self, i, j):
        return i * self.sizeW + j

    def printOutput(self, charset = [".", "o"]):
        # print([bin(i) for i in self.output])
        for i in range(self.sizeH*3):
            for j in range(self.sizeW*3):
                celly, cellx = i // 3, j // 3
                pixel = self.output[self.getIndex(celly, cellx)] & 1<<(8-(i % 3 * 3 + j % 3))
                print(charset[1] if pixel else charset[0], end="")
            print()
    
    def printBoard(self):
        board = [[0 for _ in range(self.sizeW*3)] for _ in range(self.sizeH*3)]
        tex = [["empty" for _ in range(self.sizeW*3)] for _ in range(self.sizeH*3)]

        def getDefault(val):
            if val == -1:
                return True
            return not val
        
        def getPixel(i, j):
            if(i < 0 or i >= self.sizeH*3 or j < 0 or j >= self.sizeW*3):
                return -1
            celly, cellx = i // 3, j // 3
            ans = not not (self.output[self.getIndex(celly, cellx)] & (1<<(8-(i % 3 * 3 + j % 3))))
            # print("cevap:",ans)
            return ans
        
        def getDefaultPixel(i, j):
            return getDefault(getPixel(i, j))
        
        for i in range(self.sizeH*3):
            for j in range(self.sizeW*3):
                celly, cellx = i // 3, j // 3

                isDot = getPixel(i, j)
                # print(isDot)
                if isDot:
                    board[i][j] = 2
                else:
                    board[i][j] = 3

                    # print(getPixel(i-1, j))
                    up = (getDefaultPixel(i-1, j))
                    down = (getDefaultPixel(i+1, j))
                    left = (getDefaultPixel(i, j-1))
                    right = (getDefaultPixel(i, j+1))

                    if(up and down and left and right):
                        if(getDefaultPixel(i-1, j-1) == 0):
                            tex[i][j] = "lu"
                        elif(getDefaultPixel(i-1, j+1) == 0):
                            tex[i][j] = "ur"
                        elif(getDefaultPixel(i+1, j-1) == 0):
                            tex[i][j] = "ld"
                        elif(getDefaultPixel(i+1, j+1) == 0):
                            tex[i][j] = "dr"

                    elif(up and down):
                        tex[i][j] = "ud"
                    elif(left and right):
                        tex[i][j] = "lr"
                    elif(up and right):
                        tex[i][j] = "ur"
                    elif(up and left):
                        tex[i][j] = "lu"
                    elif(down and right):
                        tex[i][j] = "dr"
                    elif(down and left):
                        tex[i][j] = "ld"
                    else:
                        tex[i][j] = "empty"
        return board, tex
    def overlap(self, other):
        copied = Output(other.sizeW, other.sizeH, other.output[:])
        assert(self.sizeW == other.sizeW and self.sizeH == other.sizeH)
        for i in range(self.sizeH):
            for j in range(self.sizeW):
                copied.output[i*self.sizeW+j] |= self.output[i*self.sizeW+j]
        self.output = copied.output



def drawOutputFromPath(path):
    output = [0b000000000 for _ in range(mazeSizeTotal)]
    for i in range(len(path)):
        u, v = edgeMapReverse[path[i]]
        uy, ux = getCoord(u)
        vy, vx = getCoord(v)
        # print("path i:",path[i],"u,v:", u, v, "uy,ux:", uy, ux, "vy,vx:", vy, vx)
        if vy > uy:
            output[u] |= down
            output[v] |= up
        if vy < uy:
            output[u] |= up
            output[v] |= down
        if vx > ux:
            output[u] |= right
            output[v] |= left
        if vx < ux:
            output[u] |= left
            output[v] |= right
        # printOutput()
        # break
    return output

printOutput(drawOutputFromPath(path))

import itertools
def getDeadEnds(path):
    deadEnds = []
    newPath = []
    for i in range(mazeSizeTotal):
        adj = getAdj(i)
        # print("adj of",i, adj)
        edges = list(itertools.product([i], adj))
        edgeIds = [edgeMap[e] for e in edges]
        # print("edges:", edges, "edgeIds:", edgeIds)


        count = 0
        for p in path:
            # effectively mask the relevant section of path & current vertex
            if p in edgeIds:
                count += 1
        unusedEdges = list(set(edgeIds) - set(path))
        if count == 1:
            deadEnds.append(i)
            newPath.append(random.choice(unusedEdges))

        # if len(getAdj(i)) == 1:
        #     deadEnds.append(i)
    return deadEnds, newPath
deadEnds, addedEdges = getDeadEnds(path)
print(deadEnds, [edgeMapReverse[i] for i in addedEdges])
newPath = path + addedEdges
print(path, addedEdges, newPath)

# printOutput(drawOutputFromPath(newPath))

#strategy: determine longest linear path in the maze and then disqualify based on that
# hint: maybe check out each combination of vertices and check for the longest path between them (without backtracking) (note: not a good way)
# OR reduce the total amount of length, calculated by each pair of vertices, and their shortest path

# check if cutting an edge causes graph to be disconnected

def flipPath(path, x=True, y=True):
    newPath = []
    for i in range(len(path)):
        u, v = edgeMapReverse[path[i]]
        # print("path:",path[i],"u,v:", u, v)
        uy, ux = getCoord(u)
        vy, vx = getCoord(v)
        if x:
            ux = mazeSizeW-1-ux
            vx = mazeSizeW-1-vx
        if y:
            uy = mazeSizeH-1-uy
            vy = mazeSizeH-1-vy
        u = getIndex(uy, ux)
        v = getIndex(vy, vx)
        # print("path reversed:",path[i],"u,v:", u, v)
        newPath.append(edgeMap[(u, v)])
    return newPath

outputs = []
outputs.append(drawOutputFromPath(flipPath(newPath, x=False, y=False)))
outputs.append(drawOutputFromPath(flipPath(newPath, x=True, y=False)))
outputs.append(drawOutputFromPath(flipPath(newPath, x=False, y=True)))
outputs.append(drawOutputFromPath(flipPath(newPath, x=True, y=True)))
# def shiftOutput(output, x, y, sizeW, sizeH):
#     # shift to right
#     for i in range(x):
#         where = i * sizeW
#         output.insert(where, 0b000000000)
#     return output
outputs = [Output(mazeSizeW, mazeSizeH, o) for o in outputs]
outputs[0].addRight(mazeSizeW-1)
outputs[0].addBottom(mazeSizeH-1)

outputs[1].shiftRight(mazeSizeW-1)
outputs[1].addBottom(mazeSizeH-1)

outputs[2].shiftBottom(mazeSizeH-1)
outputs[2].addRight(mazeSizeW-1)

outputs[3].shiftRight(mazeSizeW-1)
outputs[3].shiftBottom(mazeSizeH-1)
out = outputs[0]
out.overlap(outputs[1])
out.overlap(outputs[2])
out.overlap(outputs[3])
board, tex = out.printBoard()
boardWidth = len(board[0])
boardHeight = len(board)
out.printOutput(charset=["██", ". "])
if __name__ == "__main__":
    # out.printOutput()
    out.printOutput(charset=["██", ". "])
    print("board:", board)
    print("tex:", tex)

# printOutput(shiftOutput(outputs[0], 1, 0, mazeSizeW, mazeSizeH))

# printOutput(drawOutputFromPath(flipPath(newPath, x=False, y=False)))
# printOutput(drawOutputFromPath(flipPath(newPath, x=False, y=True)))
# printOutput(drawOutputFromPath(flipPath(newPath, x=True, y=False)))
# printOutput(drawOutputFromPath(flipPath(newPath, x=True, y=True)))

outputToTitleMap = {
    "dr": 0b000011010,
    "ld": 0b000110010,
    "lr": 0b000111000,
    "lu": 0b010110000,
    "ud": 0b010010010,
    "ur": 0b010011000,
}



    
# marching squares algorithm

# def combinePaths(path1, path2, vertical=True):
#     newPath = []
#     for i in range(len(path1)):
#         u, v = edgeMapReverse[path1[i]]
#         uy, ux = getCoord(u)
#         vy, vx = getCoord(v)
#         newPath.append(edgeMap[(u, v)])
#     for i in range(len(path2)):
#         u, v = edgeMapReverse[path2[i]]
#         uy, ux = getCoord(u)
#         vy, vx = getCoord(v)
#         # u = uy*mazeSize+vx
#         # v = vy*mazeSize+ux
#         newPath.append(edgeMap[(u, v)])
#     return newPath
