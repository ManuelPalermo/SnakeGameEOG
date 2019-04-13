import time
import pygame
import random
import numpy as np
from collections import deque



class SnakeEngine(object):
	def __init__(self):
		self.csize = 20
		self.size = [15, 15]
		self.cells = [[Cell((x, y), self.csize) for x in range(self.size[0])] for y in range(self.size[1])]
		self.head = None
		self.body = deque()
		self.bodysize = 0
		self.lastmove = None
		self.win = DirectionsGUI(map_size=self.size, cell_size=self.csize)
		self.directions = self.create_dir_objects()
		self.reset()


	def reset(self):
		'Initializes game map and GUI'
		for y in range(self.size[1]):
			for x in range(self.size[0]):
				self.cells[y][x].state = "empty"
		self.CellReference = set([self.cells[y][x] for y in range(self.size[1]) for x in range(self.size[0])])
		self.bodysize = 0
		food = np.random.choice(list(self.CellReference - set(self.body + deque([self.head]))))
		food.state = "food"
		self.body = deque()
		self.spawn()
		self.win.drawGame(self.cells, self.directions.values())

	def create_dir_objects(self, r=35):
		'Cria circulos que indicam cada uma das direções'
		objetos = {}
		for cpos, d in zip((((self.csize*self.size[0])/2,        r + 10 + 20 + self.size[1]*self.csize),                        # cima
		                    ((self.csize*self.size[0])/2,        (20 + 2*self.size[1]*self.csize) - (r + 10)),                  # baixo
		                    (r + 10,                             (self.csize*self.size[1]/2) + 20 + self.csize*self.size[1]),   # esquerda
		                    (self.csize*self.size[0] - (r + 10), (self.csize*self.size[1]/2) + 20 + self.csize*self.size[1])),  # direita
		                   ('UP', 'DOWN', 'LEFT', 'RIGHT')):
			cpos = (int(np.round(cpos[0])), int(np.round(cpos[1])))
			c = Circle(d, cpos, r)
			objetos[d] = c
			self.win.draw_direction(c)
		return objetos

	def neighbours(self, pos):
		# returns the neighbours of a pos
		viz = []
		x, y = pos[0], pos[1]
		if x > len(self.cells[0]) - 1 or y > len(self.cells) - 1: return []
		if x > 0:                       viz.append([x - 1, y])
		if x < len(self.cells[0]) - 1:  viz.append([x + 1, y])
		if y > 0:                       viz.append([x, y - 1])
		if y < len(self.cells) - 1:     viz.append([x, y + 1])
		return viz

	def lastmove_init(self, head, body):
		# decides which is the starting direction of the snake
		if head[0] - 1 == body[0]: return "RIGHT"
		if head[0] + 1 == body[0]: return "LEFT"
		if head[1] - 1 == body[1]: return "DOWN"
		if head[0] + 1 == body[1]: return "UP"

	def spawn(self):
		# spawns the snake head in a random position
		start = random.choice(list(self.CellReference))
		startpos = [start.x, start.y]
		nearpos = random.choice(self.neighbours(startpos))
		nearcell = self.cells[nearpos[1]][nearpos[0]]
		self.lastmove = self.lastmove_init(startpos, nearpos)
		self.head = start
		self.body.appendleft(nearcell)
		start.state = "head"
		nearcell.state = "body"

	def spawnfood(self):
		# spawns food somewhere around the map, on valid positions
		cell = np.random.choice(list(self.CellReference - set(self.body + deque([self.head]))))
		cell.state = "food"
		self.win.drawCell(cell)

	def move(self, move):
		#ativa thresolds correspondentes
		self.ativa_direcoes(move)
		self.desativa_direcoes({"UP","DOWN", "RIGHT", "LEFT"}-move)
		#desempata moves simultaneos
		if not move:                                        next_move = self.lastmove
		if "LEFT" in move and self.lastmove != "RIGHT":     next_move = "LEFT"
		elif "UP" in move and self.lastmove != "DOWN":      next_move = "UP"
		elif "RIGHT" in move and self.lastmove != "LEFT":   next_move = "RIGHT"
		elif "DOWN" in move and self.lastmove != "UP":      next_move = "DOWN"
		else:                                               next_move = self.lastmove
		# atualiza estado do jogo
		x = self.head.x
		y = self.head.y
		self.body.appendleft(self.head)
		self.head.state = "body"
		self.win.drawCell(self.head)
		if next_move == "LEFT":
			if self.cells[y][x - 1].state == "body":
				print("You have lost!\n")
				self.reset()
			else:
				if self.cells[y][x - 1].state == "food":
					self.bodysize += 1
					self.spawnfood()
					self.win.drawScore(self.bodysize)
				else:
					tail = self.body.pop()
					tail.state = "empty"
					self.win.drawCell(tail)
				self.cells[y][x - 1].state = "head"
				self.head = self.cells[y][x - 1]
				self.win.drawCell(self.head)
				self.lastmove = "LEFT"

		elif next_move == "UP":
			if self.cells[y - 1][x].state == "body":
				print("You have lost!\n")
				self.reset()
			else:
				if self.cells[y - 1][x].state == "food":
					self.bodysize += 1
					self.spawnfood()
					self.win.drawScore(self.bodysize)
				else:
					tail = self.body.pop()
					tail.state = "empty"
					self.win.drawCell(tail)
				self.cells[y - 1][x].state = "head"
				self.head = self.cells[y - 1][x]
				self.win.drawCell(self.head)
				self.lastmove = "UP"

		elif next_move == "RIGHT":
			if x + 1 >= len(self.cells[0]): x = -1
			if self.cells[y][x + 1].state == "body":
				print("You have lost!\n")
				self.reset()
			else:
				if self.cells[y][x + 1].state == "food":
					self.bodysize += 1
					self.spawnfood()
					self.win.drawScore(self.bodysize)
				else:
					tail = self.body.pop()
					tail.state = "empty"
					self.win.drawCell(tail)
				self.cells[y][x + 1].state = "head"
				self.head = self.cells[y][x + 1]
				self.win.drawCell(self.head)
				self.lastmove = "RIGHT"

		elif next_move == "DOWN":
			if y + 1 >= len(self.cells): y = -1
			if self.cells[y + 1][x].state == "body":
				print("You have lost!\n")
				self.reset()
			else:
				if self.cells[y + 1][x].state == "food":
					self.bodysize += 1
					self.spawnfood()
					self.win.drawScore(self.bodysize)
				else:
					tail = self.body.pop()
					tail.state = "empty"
					self.win.drawCell(tail)
				self.cells[y + 1][x].state = "head"
				self.head = self.cells[y + 1][x]
				self.win.drawCell(self.head)
				self.lastmove = "DOWN"

		if pygame.event.peek(pygame.QUIT):   # verifica se foi acionado evento para fechar janela grafica
			pygame.event.clear(pygame.QUIT)
			return True


	def ativa_direcoes(self, dirs):
		'Ativa multiplas direçoes'
		for d in dirs:                                      # para cada uma das direcoes
			if self.directions[d].estado == False:          # se estao inativas
				self.directions[d].estado = True            # torna ativas
				self.win.draw_direction(self.directions[d]) # desenha objeto na janela

	def desativa_direcoes(self, dirs):
		'Desativa multiplas direçoes'
		for d in dirs:                                      # para cada uma das direcoes
			if self.directions[d].estado == True:           # se estao ativas
				self.directions[d].estado = False           # torna inativas
				self.win.draw_direction(self.directions[d]) # desenha objeto na janela

	def testGUI(self, nmoves=1000, fps=20):
		'Test GUI with random moves'
		for i in range(nmoves):
			time.sleep((1/fps))
			move = random.choice([{"UP"}, {"DOWN"}, {"RIGHT"}, {"LEFT"},
			                      {"UP", "LEFT"}, {"DOWN", "LEFT"}, {"RIGHT", "UP"}, {"RIGHT", "DOWN"},
			                      {"UP", "RIGHT"}, {"DOWN", "RIGHT"}, {"LEFT", "UP"}, {"LEFT", "DOWN"}])
			self.move(move)



class DirectionsGUI:
	def __init__(self, map_size, cell_size):
		################ Window size #######################
		self.map_size  = map_size                                       # size of the window (in cells)
		self.csize     = cell_size                                      # size of each cell (in pixels)
		self.win_size  = (self.map_size[0]*cell_size,                   # window x size(pixels)
		                  20 + 2*self.map_size[1]*cell_size)            # window y size(pixels)
		################ Pygame Window #####################
		pygame.init()
		self.window    = pygame.display.set_mode(self.win_size)         # game window using pygame
		pygame.display.set_caption('DirectionsInterfaceEOG')            # name of the window


	def drawGame(self, mapp, directions):
		'Displays all the cells in the screen (used to initialize the game screen)'
		#draw snake game
		self.window.fill(((10, 10, 10)))
		for y in range(self.map_size[1]):
			pygame.draw.line(self.window, (75, 75, 75), [0, y*self.csize],[self.win_size[0], y*self.csize])
			for x in range(self.map_size[0]):
				pygame.draw.line(self.window, (75, 75, 75), [x*self.csize, 0], [x*self.csize, self.win_size[1] -(20+self.map_size[1]*self.csize)])
				self.drawCell(mapp[y][x])
		# draw dividing line between directions and snake GUI
		pygame.draw.line(self.window,
		                 (75, 75, 75),
		                 [0, self.win_size[1] - (15 + self.map_size[1] * self.csize)],
		                 [self.win_size[0], self.win_size[1] - (15 + self.map_size[1] * self.csize)], 10)
		#draw directions
		for d in directions:
			self.draw_direction(d)
		#
		pygame.display.flip()

	def drawCell(self, cell):
		' Displays the cell on the board'
		if cell.state=="empty":
			pygame.draw.rect(self.window, (10, 10, 10), cell.bound_box)
		elif cell.state=="head":
			pygame.draw.rect(self.window, (0, 200, 0), cell.bound_box)
		elif cell.state=="body":
			pygame.draw.rect(self.window, (0, 100, 0), cell.bound_box)
		elif cell.state=="food":
			pygame.draw.rect(self.window, (255, 0, 0), cell.bound_box)
		pygame.display.update(cell.bound_box)

	def draw_direction(self, direction):
		if direction.estado == False:   # se a direcao nao foi ativada, desenha circulo cinzento
			pygame.draw.circle(self.window, (100, 100, 100), direction.pos, direction.r)
		else:                           # se a direcao foi ativada, desenha circulo amarelo
			pygame.draw.circle(self.window, (200, 200, 0), direction.pos, direction.r)
		pygame.display.update(direction.bound_box)  # atualiza objeto

	def drawScore(self, score):
		'Updates the score on the GUI'
		return


class Cell:
	def __init__(self, pos, csize):
		self.x = pos[0]
		self.y = pos[1]
		self.state = "empty"
		self.bound_box = pygame.Rect((self.x * csize + 1,
		                              self.y * csize + 1,
		                              csize - 1,
		                              csize - 1))

class Circle:
	def __init__(self, direcao, pos, radius):
		self.direcao = direcao                  # direcao do circulo(Cima/Baixo/Esq/Direita)
		self.pos = pos                          # posicao na janela
		self.r = radius                         # raio do circulo
		self.estado = False                     # estado(ativo/inativo)
		self.bound_box = pygame.Rect(self.pos[0] - self.r,
		                             self.pos[1] - self.r,
		                             self.r * 2,
		                             self.r * 2)



if __name__ == "__main__":
	eng = SnakeEngine()
	eng.testGUI()

	'''
	# keyboard game
	clock = pygame.time.Clock()
	fps = 5

	running = True
	while running:
		moves = []
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False

			pressed = pygame.key.get_pressed()
			if pressed[pygame.K_UP]: moves.append("UP")
			if pressed[pygame.K_DOWN]: moves.append("DOWN")
			if pressed[pygame.K_LEFT]: moves.append("LEFT")
			if pressed[pygame.K_RIGHT]: moves.append("RIGHT")
			pygame.event.clear()

		eng.move(set(moves))
		clock.tick(fps)
	'''
