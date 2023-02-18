from pygame import Surface, draw, font, display, event, Rect, init, QUIT, KEYDOWN, K_ESCAPE, K_UP, K_DOWN, K_LEFT, K_RIGHT, K_b, K_n
from numpy import sort, array, zeros, uint8, amax, amin, random, rot90, copy
from time import time
from random import gauss as gs
from os.path import join,dirname

class Species():

    def __init__(self, generation):
        self.idt, self.wRowsCleared, self.wMaxHeight, self.wMinHeight, self.wAmountHoles, self.wRoughness = random.randint(1,10000), 0, 0, 0, 0, 0
        self.mustasyonOranı = 0.05
        self.generation = generation
        self.score = 0

    def __str__(self):return f"Id : {str(self.idt)}\nSkor : {str(self.score)}\nBoş Satır : {str(self.wRowsCleared)}\nEngebelik : {str(self.wRoughness)}\nMak Yükseklik : {str(self.wMaxHeight)}\nMin Yükseklik  : {str(self.wMinHeight)}\nBoşluk Sayısı : {str(self.wAmountHoles)}\n" 

    # def initialSpecies(self):
    #     self.wRowsCleared = round(random.random() - 0.5,4)
    #     self.wMaxHeight = round(random.random() - 0.5,4)
    #     self.wMinHeight = round(random.random() - 0.5,4)
    #     self.wAmountHoles = round(random.random() - 0.5,4)
    #     self.wRoughness = round(random.random() - 0.5,4)

    def initialSpecies(self, gen, count):
        with open(join(dirname(__file__),"./datas.csv"), encoding='utf-8') as f_normal:
            datas = []
            for line in f_normal:
                datas.append(line.strip().split(','))
            self.idt = int(datas[gen*40+count][0])
            self.wAmountHoles = float(datas[gen*40+count][1])
            self.wMaxHeight = float(datas[gen*40+count][2])
            self.wMinHeight = float(datas[gen*40+count][3])
            self.wRoughness = float(datas[gen*40+count][4])
            self.wRowsCleared = float(datas[gen*40+count][5])
            if(gen*40+count<1000):
                self.score = datas[gen*40+count][6]
            else:
                self.score = 0  

    def crossingOver(self, ancestor1, ancestor2):
        self.wRowsCleared = round(random.choice([ancestor1.wRowsCleared, ancestor2.wRowsCleared]),4)
        self.wMaxHeight = round(random.choice([ancestor1.wMaxHeight, ancestor2.wMaxHeight]),4)
        self.wMinHeight = round(random.choice([ancestor1.wMinHeight, ancestor2.wMinHeight]),4)
        self.wAmountHoles = round(random.choice([ancestor1.wAmountHoles, ancestor2.wAmountHoles]),4)
        self.wRoughness = round(random.choice([ancestor1.wRoughness, ancestor2.wRoughness]),4)

    def mutation(self):
        if random.random() < self.mustasyonOranı:self.wRowsCleared = round(self.wRowsCleared + gs()/5,4)
        if random.random() < self.mustasyonOranı:self.wMaxHeight = round(self.wMaxHeight + gs()/5,4)
        if random.random() < self.mustasyonOranı:self.wMinHeight = round(self.wMinHeight + gs()/5,4)
        if random.random() < self.mustasyonOranı:self.wAmountHoles = round(self.wAmountHoles + gs()/5,4)
        if random.random() < self.mustasyonOranı:self.wRoughness = round(self.wRoughness + gs()/5,4)

    __repr__ = __str__

class Generation():

    def __init__(self, generation):
        self.generation = generation
        self.species = []
        self.elite = []
        for _ in range(40):self.species.append(Species(self.generation))

    def initialGeneration(self,gen):
        for i in range(40):self.species[i].initialSpecies(gen,i)

class Population():
    def __init__(self):
        self.gens = []
        for q in range(26):
            self.gens.append(Generation(q))
            self.gens[q].initialGeneration(q)

    def nextGen(self):
        cGen = len(self.gens)-1#cGen = Current Generation -> Şuanki Nesil
        nGen = cGen + 1 #nGen = Next Generation -> Sonraki Nesil
        scores = []
        i = 0
        for s in self.gens[cGen].species:
            scores.append((i,s.score))
            i+=1
        scores = sort(array(scores, dtype=[("index", int), ("score", int)]), order="score")#(index, score)
        elite = list(reversed([x[0] for x in scores[30:40]]))#indexes of elite species -> elite türlerin indeksleri
        self.gens[cGen].elite = elite
        self.gens.append(Generation(nGen))
        for i in range(40):
            if i<5:self.gens[nGen].species[i].crossingOver(self.gens[cGen].species[elite[i]], self.gens[cGen].species[elite[i]])#ilk 5 tane eliti kendileri ile çaprazlama
            else:
                r1 = random.randint(10)
                r2 = random.randint(10)
                self.gens[nGen].species[i].crossingOver(self.gens[cGen].species[elite[r1]], self.gens[cGen].species[elite[r2]])#10 tane eliti içinden random seçerek bunlardan 2 tanesini çaprazlama
            self.gens[nGen].species[i].mutation()

class AI():
    def __init__(self, grid, score):
        self.grid = grid
        self.score = score
        self.population = Population()
        self.currentGeneration = 25
        self.currentSpecies = 0
        self.backupGrid = zeros([10, 20], dtype=uint8)
        self.backupTile = [0, 0, 0]

    def makeMove(self, tile):
        self.backupGrid = copy(self.grid.grid)
        self.grid.realAction = False
        self.backupTile = [tile.posX, tile.posY, tile.rot]
        bestRating = -10000000000000
        bestMove = 0
        bestRotate = 0
        for move in range(-5, 6):
            for rotate in range(0, 3):
                for _ in range(0, rotate):tile.rotCW()
                if move < 0:
                    for _ in range(0, -move):tile.decX()
                if move > 0:
                    for _ in range(0, move):tile.incX()
                tile.drop()
                tile.apply()
                self.grid.rmCompRows()
                if self.rateMove()[0] > bestRating:
                    bestMove = move
                    bestRotate = rotate
                    bestRating, gameover = self.rateMove()
                tile.posX, tile.posY, tile.rot = self.backupTile
                self.grid.grid = copy(self.backupGrid)
        self.grid.realAction = True
        self.grid.grid = copy(self.backupGrid)
        if gameover:
            self.population.gens[self.currentGeneration].species[self.currentSpecies].score = self.score.getScore()
            if self.currentSpecies == 39:
                self.currentSpecies = 0
                self.population.nextGen()
                self.currentGeneration += 1
            else:self.currentSpecies += 1
        for _ in range(0, bestRotate):tile.rotCW()
        if bestMove < 0:
            for _ in range(0, -bestMove):tile.decX()
        if bestMove > 0:
            for _ in range(0, bestMove):tile.incX()
        tile.drop()
        return bestMove, bestRotate, bestRating

    def rateMove(self):
        gameover = False
        cSpecies = self.population.gens[self.currentGeneration].species[self.currentSpecies]
        rating = 0
        rating += self.grid.RowsCleared * cSpecies.wRowsCleared
        rating += self.grid.MaxHeight * cSpecies.wMaxHeight
        rating += self.grid.MinHeight * cSpecies.wMinHeight
        rating += self.grid.AmountHoles * cSpecies.wAmountHoles
        rating += self.grid.Roughness * cSpecies.wRoughness
        if self.grid.checkForGameOver():
            rating -= 500
            gameover = True
        return rating, gameover

class Grid():

    def __init__(self, score):
        self.score = score
        self.grid = zeros([10, 20], dtype=uint8)
        self.realAction = True
        self.RowsCleared = 0
        self.MaxHeight = 0
        self.MinHeight = 0
        self.Roughness = 0
        self.AmountHoles = 0

    def checkField(self, posX, posY):
        if posX < 0 or posX > 9 or posY > 19 or posY < 0:return False
        if self.grid[posX, posY] != 0:return False
        return True

    def apply(self, posX, posY, idt):self.grid[posX, posY] = idt

    def rmCompRows(self):#remove completed rows
        rows = 0
        for y in range(19, -1, -1):
            while amin(self.grid.T[y]) != 0:
                rows += 1
                for y2 in range(y, 0, -1):
                    for x in range(10):self.grid[x, y2] = self.grid[x, y2 - 1]
        self.RowsCleared = rows
        heightData = []
        for column in self.grid:
            counter = 20
            for i in range(19, -1, -1):
                if column[i] != 0:counter = i
            heightData.append(20 - counter)
        self.MaxHeight = amax(heightData)
        self.MinHeight = amin(heightData)
        self.Roughness = 0
        for x in range(9):self.Roughness += abs(heightData[x] + heightData[x - 1])
        self.AmountHoles = 0
        for x in range(10):
            for y in range(19, 1, -1):
                if self.grid[x, y] == 0 and self.grid[x, y - 1] != 0:self.AmountHoles += 1
        if self.realAction:self.score.rowsCleared(rows)

    def checkForGameOver(self):
        for y in range(4):
            if amax(self.grid.T[y]) != 0:
                if self.realAction:self.reset()
                return True
        return False

    def reset(self):
        self.grid = zeros([10, 20], dtype=uint8)
        if self.realAction:self.score.reset()

class Time():
    def __init__(self, interval):
        self.eventInterval = interval 
        self.lastTimedEvent = time()
        self.speedMode = 8
        self.speedSet = [0.125,0.25,0.5,0.75,1,2,5,10,20,50,100,200,500,1000,2000,5000]
    def incSpeed(self):self.speedMode = min(self.speedMode + 1, 15)
    def decSpeed(self):self.speedMode = max(self.speedMode - 1, 0)
    def getSpeed(self):return self.speedSet[self.speedMode]
    def timeEvent(self):
        if time() > self.lastTimedEvent + (self.eventInterval / self.speedSet[self.speedMode]):
            self.lastTimedEvent = time()
            return True
        return False

class Scorer():
    def __init__(self):
        self.score = 0
        self.highest = 37560
        self.clearPoints = [0, 40, 100, 300, 1200]
    def rowsCleared(self, rows):self.score += self.clearPoints[rows]
    def tileReleased(self):self.score += 100
    def getScore(self):return self.score
    def bestScore(self):return self.highest
    def reset(self):
        if self.score > self.highest:self.highest = self.score
        self.score = 0

class View():

    r1 = (24, 24, 24)#rgb(24,24,24)
    r2 = (255, 0, 0)#rgb(0,255,255)
    r3 = (0, 128, 255)#rgb(0,128,255)
    r4 = (0, 255, 128)#rgb(0,255,128)
    r5 = (255, 128, 0)#rgb(255,0,255)
    r6 = (255, 255, 0)#rgb(255,255,0)
    r7 = (128, 0, 255)#rgb(128,0,255)
    r8 = (255, 0, 128)#rgb(255,0,128)
    r9 = (255, 255, 255)#rgb(255,255,255)
    colors = [r1, r2, r3, r4, r5, r6, r7, r8]

    def __init__(self, grid, time, score, ai):
        self.ai = ai
        self.grid = grid
        self.time = time
        self.score = score
        self.abort = False
        self.update = True
        self.infoMode = 0
        self.genscr = [0, -1]
        self.aiState = True
        self.screen = display.set_mode((820, 720))
        display.set_caption("Tetris AI Game")
        init()
        self.fb = font.SysFont('Calibri', 60, True, False)
        self.fr = font.SysFont('Calibri', 24, True, False)
        self.fs = font.SysFont('Calibri', 17, True, False)
        self.updateStatic(True)

    def updateStatic(self, render=False):
        if not render:
            self.screen.blit(self.static, (0, 0))
            return
        static = Surface((840, 720))
        static.set_colorkey((0, 0, 0))
        static.fill(self.r1)
        for i in range(10):
            draw.line(static, self.r9, (30 * i + 60, 60), (30 * i + 60, 660))
            draw.line(static, self.r9, (60, 30 * i + 60), (360, 30 * i + 60), 1 + 2 * (i == 4))
            draw.line(static, self.r9, (60, 30 * i + 390), (360, 30 * i + 390))
        draw.line(static, self.r9, (360, 60), (360, 660))
        draw.line(static, self.r9, (60, 360), (360, 360))
        for i in range(5):
            draw.line(static, self.r9, (480, 30 * i + 180), (600, 30 * i + 180))
            draw.line(static, self.r9, (30 * i + 480, 180), (30 * i + 480, 300))
        label = self.fb.render("Tetris AI", 2, self.r9)
        size = self.fb.size("Tetris AI")[0]
        static.blit(label, (615 - size / 2, 30))
        self.static = static

    def setUpdate(self, update):self.update = update

    def setTile(self, cTile, nTile):
        self.cTile = cTile
        self.nTile = nTile

    def updateGrid(self):
        grid = self.grid.grid + self.cTile.render()
        for x in range(10):
            for y in range(20):
                color = self.colors[grid[x, y]]
                draw.rect(self.screen, color, Rect(30 * x + 65, 30 * y + 65, 21, 21), 0)

    def updateGameScreen(self):
        color = self.colors[self.nTile.idt]
        preview = self.nTile.renderPreview()
        for x in range(4):
            for y in range(4):
                if preview[x, y] != 0:draw.rect(self.screen,color,Rect(30 * x + 485, 30 * y + 185, 21, 21),0)
        label = self.fr.render(str(self.score.getScore()), 2, self.r9)
        size = self.fr.size(str(self.score.getScore()))[0]
        self.screen.blit(label, (780 - size, 180))
        label = self.fr.render(str(self.score.bestScore()), 2, self.r9)
        size = self.fr.size(str(self.score.bestScore()))[0]
        self.screen.blit(label, (780 - size, 240))

    def updateGeneralScreen(self):
        label = self.fr.render("Speed", 2, self.r4)
        self.screen.blit(label, (480, 450))
        label = self.fr.render(str(self.time.getSpeed()) + "x", 2, self.r3)
        size = self.fr.size(str(self.time.getSpeed()) + "x")[0]
        self.screen.blit(label, (780 - size, 450))
        label = self.fr.render("Generations", 2, self.r4)
        self.screen.blit(label, (480, 480))
        label = self.fr.render(str(self.ai.currentGeneration), 2, self.r3)
        size = self.fr.size(str(self.ai.currentGeneration))[0]
        self.screen.blit(label, (780 - size, 480))
        label = self.fr.render("Species", 2, self.r4)
        self.screen.blit(label, (480, 510))
        label = self.fr.render(str(self.ai.currentSpecies+1), 2, self.r3)
        size = self.fr.size(str(self.ai.currentSpecies))[0]
        self.screen.blit(label, (780 - size, 510))

    def updategenscr(self):
        label = self.fs.render(str(self.genscr[0])+ "/"+ str(len(self.ai.population.gens) - 1)+ ": "+ str(self.genscr[1]+1),2,self.r9)
        self.screen.blit(label, (480, 400))
        if self.genscr[1] == -1:
            for i in range(10):
                label = self.fs.render(f"{i+1}:", 2, self.r9)
                self.screen.blit(label, (445, 450 + 15 * i))
            for i in range(40):
                score = (self.ai.population.gens[self.genscr[0]].species[i].score)
                label = self.fs.render(str(score), 2, self.r9)
                self.screen.blit(label, (480 + 75 * int(i / 10), 450 + 15 * (i % 10)))
        else:
            i = 0
            for line in str(self.ai.population.gens[self.genscr[0]].species[self.genscr[1]]).split("\n"):
                if line != "":
                    label = self.fs.render(str(line), 2, self.r9)
                    self.screen.blit(label, (480, 450 + 15 * i))
                    i += 1

    def eventCheck(self):
        for eve in event.get():
            if eve.type == QUIT:self.abort = True
            if eve.type == KEYDOWN:
                if eve.key == K_ESCAPE:event.post(event.Event(QUIT))
                if eve.key == K_b:self.infoMode = 0
                if eve.key == K_n:self.infoMode = 1
                if self.infoMode == 0:
                    if eve.key == K_LEFT:self.time.decSpeed()
                    if eve.key == K_RIGHT:self.time.incSpeed()
                if self.infoMode == 1:
                    if eve.key == K_UP:self.genscr[1] = min(39, self.genscr[1] + 1)
                    if eve.key == K_DOWN:self.genscr[1] = max(-1, self.genscr[1] - 1)
                    if eve.key == K_LEFT:self.genscr[0] = max(0, self.genscr[0] - 1)
                    if eve.key == K_RIGHT:self.genscr[0] = min(len(self.ai.population.gens) - 1,self.genscr[0] + 1)

    def updateEverything(self):
        self.eventCheck()
        if not self.update:return
        self.updateStatic()
        self.updateGrid()
        self.updateGameScreen()
        if self.infoMode == 0:self.updateGeneralScreen()
        if self.infoMode == 1:self.updategenscr()
        display.flip()

class Tile():
    def __init__(self, layout, idt):
        self.layout = array(layout, dtype=uint8)
        self.idt = idt

class MovableTile(Tile):
    def __init__(self, layout, idt, grid, posX, rot=-1):
        Tile.__init__(self, layout, idt)
        self.grid = grid
        self.posX = posX
        self.posY = 0
        if rot == -1:self.rot = random.randint(0, 4)
        else:self.rot = rot

    def incX(self):#move right
        rotated = rot90(self.layout, self.rot)
        for rowIndex in range(4):
            row = rotated.T[rowIndex]
            lastBlock = -1
            for columnIndex in range(4):
                if row[columnIndex] == 1:lastBlock = columnIndex
            if lastBlock != -1:
                if not self.grid.checkField(self.posX + lastBlock + 1, self.posY + rowIndex):return False
        self.posX += 1
        return True

    def decX(self):#move left
        rotated = rot90(self.layout, self.rot)
        for rowIndex in range(4):
            row = rotated.T[rowIndex]
            firstBlock = -1
            for columnIndex in range(3, -1, -1):
                if row[columnIndex] == 1:firstBlock = columnIndex
            if firstBlock != -1:
                if not self.grid.checkField(self.posX + firstBlock - 1, self.posY + rowIndex):return False
        self.posX -= 1
        return True

    def incY(self):#move down
        rotated = rot90(self.layout, self.rot)
        for columnIndex in range(4):
            column = rotated[columnIndex]
            lowestBlock = -1
            for rowIndex in range(4):
                if column[rowIndex] == 1:lowestBlock = rowIndex
            if lowestBlock != -1:
                if not self.grid.checkField(self.posX + columnIndex, self.posY + lowestBlock + 1):return False
        self.posY += 1
        return True

    def drop(self):#drop down
        while self.incY():pass

    def rotCW(self):#rotate clockwise
        rotated = rot90(self.layout, (self.rot + 1) % 4)
        for x in range(4):
            for y in range(4):
                if rotated[x, y] == 1:
                    if not self.grid.checkField(self.posX + x, self.posY + y):return False
        self.rot = (self.rot + 1) % 4
        return True

    def render(self):#render the tile
        grid = zeros([10, 20], dtype=uint8)
        rotated = rot90(self.layout, self.rot)
        for x in range(4):
            for y in range(4):
                if -1 < x + self.posX < 10 and -1 < y + self.posY < 20:grid[x + self.posX, y + self.posY] = rotated[x, y] * self.idt
        return grid

    def renderPreview(self):#render preview of the tile
        return rot90(self.layout, self.rot)

    def apply(self):#apply the tile to the grid
        for x in range(10):
            for y in range(20):
                if self.render()[x, y] != 0:self.grid.apply(x, y, self.idt)
        self.grid.rmCompRows()

class TileCon():
    def __init__(self, grid):
        self.tileSet, self.grid = [
            Tile([[1, 0, 0, 0], [1, 1, 0, 0], [1, 0, 0, 0], [0, 0, 0, 0]], 1),#T
            Tile([[0, 1, 0, 0], [0, 1, 0, 0], [0, 1, 0, 0], [0, 1, 0, 0]], 2),#I
            Tile([[0, 0, 0, 0], [0, 1, 1, 1], [0, 1, 0, 0], [0, 0, 0, 0]], 3),#L
            Tile([[0, 1, 0, 0], [0, 1, 1, 1], [0, 0, 0, 0], [0, 0, 0, 0]], 4),#L(Reverse)
            Tile([[0, 0, 0, 0], [0, 1, 1, 0], [0, 1, 1, 0], [0, 0, 0, 0]], 5),#O
            Tile([[1, 1, 0, 0], [0, 1, 1, 0], [0, 0, 0, 0], [0, 0, 0, 0]], 6),#Z
            Tile([[0, 0, 0, 0], [0, 1, 1, 0], [1, 1, 0, 0], [0, 0, 0, 0]], 7) #Z(Reverse)
        ],grid

    def getRandomTile(self):
        pattern = self.tileSet[random.randint(0, 6)]
        return MovableTile(pattern.layout, pattern.idt, self.grid, 3)

class Main():

    def __init__(self):
        self.sc  = Scorer()
        self.gc = Grid(self.sc)
        self.tlc = TileCon(self.gc)
        self.aI = AI(self.gc, self.sc)
        self.tC = Time(1)
        self.vc = View(self.gc, self.tC, self.sc, self.aI)
        self.cTile = self.tlc.getRandomTile()#cTile = Current Tile,
        self.nTile = self.tlc.getRandomTile()#nTile = Next Tile
        self.vc.setTile(self.cTile, self.nTile)
        self.startGame()

    def startGame(self):
        while not self.vc.abort:
            if self.tC.timeEvent():
                if self.vc.aiState:move, rotate, rating = self.aI.makeMove(self.cTile)
                if not self.cTile.incY():
                    self.cTile.apply()
                    if not self.gc.checkForGameOver():self.sc.tileReleased()
                    self.cTile = self.nTile
                    self.nTile = self.tlc.getRandomTile()
                    self.vc.setTile(self.cTile, self.nTile)
            self.vc.updateEverything()

if __name__ == '__main__':
    Main()
