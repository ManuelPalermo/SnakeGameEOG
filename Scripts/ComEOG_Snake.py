import os
import time
import serial
import numpy as np
import pyqtgraph as pg
from collections import deque
from Snake import SnakeEngine



class ComHandler(object):
	"""Displays data trough the communication protocol"""
	def __init__(self, com_port, baud=4800, channel_count=2, data_resolution=7, graph_points=1000,
	             show_only_graphs=False, window_fps=60, game_fps=5):
		# inicia canal de comunicacao
		self.com_port = com_port         # porta serie a usar para a comunicacao
		self.ser = self.open_coms(baud)  # inicia comunicacao pela porta serie

		self.channel_count = channel_count  # numero de canais a fazer display
		self.dresol = data_resolution       # resolucao maxima dos dados a fazer display
		self.graph_points = graph_points    # numero de pontos a fazer display simultaneamente em cada canal

		# lista de queues com dados a ser mostrados em cada canal(cada canal é inicializado com 0s)
		self.channel_queues = [deque([0 for _ in range(graph_points)], maxlen=graph_points) for _ in
		                       range(channel_count)]

		# criacao da janela grafica EOG e seus parametros
		self.win = pg.GraphicsWindow(title="DisplayEOG")    # inicia janela grafica(onde serao colocados os graficos)
		self.resize_window()                                # dimensiona a janela grafica
		self.channels_plot = self.init_channels()           # cria lista com graficos para cada canal
		pg.QtGui.QGuiApplication.processEvents()            # mostra janela grafica
		self.graph_actualization_time = (1 / window_fps)    # frequencia de atualizaçao da janela grafica
		self.graph_timer = time.perf_counter()              # contador para atualizar janelas graficas

		# criacao da janela grafica das direçoes e do SNAKE e parametros associados
		self.show_only_graphs = show_only_graphs
		if not show_only_graphs:
			# cria janela para mostrar thresholds e jogo SNAKE
			self.threshold_win = SnakeEngine()
			self.game_actualization_time = (1 / game_fps)   # frequencia de atualização da janela de Direcoes/SNAKE
			self.game_timer = time.perf_counter()           # contador para atualizar o snake e thresolds
			self.thresholds = {'UP': 2.75, 'DOWN': 2.25, 'LEFT': 2.75, 'RIGHT': 2.25}  # definicao dos niveis de threshold

		self.data_history = []  # historia de todos os dados recebidos pelo sistema
	################################################################################################################

	def open_coms(self, baud):
		"""Starts comunication through a serial port"""
		# definição dos parametros de comunicação a usar
		ser = serial.Serial(port=self.com_port,  # nome/caminho da porta a usar para a comunicacao
		                    baudrate=baud,  # taxa de transmissao de dados(baud rate)
		                    # bytesize=serial.EIGHTBITS,         # numero de bits por byte enviado
		                    # parity=serial.PARITY_NONE,         # uso ou nao de bits de paridade automaticos
		                    # stopbits=serial.STOPBITS_ONE,      # numero de stop bits por cada dado enviado
		                    # rtscts=False,                      # controlo de fluxo por hardware (RTS/CTS)
		                    # dsrdtr=False                       # controlo de fluxo por hardware (DSR/DTR)
		                    )
		if not ser.isOpen():  # aviso caso a porta nao tenha sido aberta
			print('Serial Port could not be opened!')
		else:
			print('Serial Port is open!')   # indicação que a porta foi aberta
			ser.reset_input_buffer()        # esvaziamento dos buffers de entrada e saida
			ser.reset_output_buffer()
			return ser                      # retorna canal de comunicação configurada


	def resize_window(self):
		"""Resizes the graphical window"""
		if self.channel_count <= 2:                         # se é usado numero reduzido de canais
			self.win.resize(1000, self.channel_count * 325) # diminui o tamanho standard do grafico
		else:
			self.win.resize(1000, 650)                      # usa janela com dimensoes (1100x650)


	def init_channels(self):
		"""Initializes channels_plot list"""
		channels_plot = []  # cria lista para colocar os graficos(1 por canal)
		for i in range(self.channel_count):  # ciclo para configurar e colocar graficos na lista
			new_plot = self.win.addPlot(row=i, col=1)  # adiciona canal a janela grafica
			new_plot.hideAxis('bottom')  # esconde o eixo X
			new_plot.showGrid(y=True, alpha=0.2)
			new_plot.setLabel('left', text=f'Canal {i}')  # adiciona nome ao eixo Y
			new_plot.setYRange(0, 5, padding=0.01)  # seleciona escala do eixo Y
			channels_plot.append(new_plot.plot())  # adiciona grafico a lista e "desenha-o" na janela
		return channels_plot  # retorna lista graficos para cada canal


	def receiver_loop(self):
		"""Plots random data to see how how the window reacts"""
		while True:
			if self.ser.in_waiting > 0:
				# acede ao buffer e retira varios pacotes para serem processados
				for pack in (int.from_bytes(self.ser.read(), 'big') for _ in range(min(self.ser.in_waiting, 16))):
					bpack = self.value_to_bin(pack, 8)  # converte pacote para binario
					value = self.bin_to_volt_value(bpack[0:7])  # seleciona valor e converte para volts
					canal = int(bpack[7])  # seleciona canal e converte para int
					self.channel_queues[canal].append(value)  # adiciona valor a queue do canal
					self.data_history.append((canal, value))  # grava dados na historia

					# faz display da janela dos graficos a frequencia especificada
					if time.perf_counter() - self.graph_timer >= self.graph_actualization_time:
						self.graph_timer = time.perf_counter()  # faz reset ao timer
						self.update_graphs()  # atualiza display do canal

					# faz display da janela das direcoes e do SNAKE a frequencia especificada
					if not self.show_only_graphs and time.perf_counter() - self.game_timer >= self.game_actualization_time:
						self.game_timer = time.perf_counter()  # faz reset ao timer
						directions = self.thresold_handler_simples()  # verifica direcao(thresholds)
						exit_event = self.threshold_win.move(directions)  # atualiza janela que mostra direçoes e SNAKE
						if exit_event:  # se for acionado um evento de exit
							self.save_data_history()  # grava dados recebidos num ficheiro
							return


	def update_graphs(self):
		"""Updates window´s desired channel with new data"""
		self.channels_plot[0].setData(self.channel_queues[0])  # faz update dos dados do canal0
		self.channels_plot[1].setData(self.channel_queues[1])  # faz update dos dados do canal1
		pg.QtGui.QGuiApplication.processEvents()  # atualiza display na janela


	def thresold_handler_simples(self):
		'''Determina quais direçoes devem estar acessas na janela dos thresolds'''
		valueV = self.channel_queues[0][-1]  # seleciona ultimo valor do canal0 - Vertical
		valueH = self.channel_queues[1][-1]  # seleciona ultimo valor do canal1 - Horizontal
		directions = []
		if valueV > self.thresholds['UP']:  # se ultrapassar o threshold vertical de cima
			directions.append("UP")
		elif valueV < self.thresholds['DOWN']:  # se ultrapassar o threshold vertical de baixo
			directions.append("DOWN")
		if valueH > self.thresholds['LEFT']:  # se ultrapassar o threshold horizontal de esquerda
			directions.append("LEFT")
		elif valueH < self.thresholds['RIGHT']:  # se ultrapassar o threshold horizontal de direita
			directions.append("RIGHT")
		return set(directions)  # retorna direcoes onde foram ultrapassados thresholds


	def thresold_handler_medias(self):
		'''Determina quais direçoes devem estar acessas na janela dos thresolds'''
		valueV = self.channel_queues[0][-1] - sum(self.channel_queues[0]) / self.graph_points
		valueH = self.channel_queues[1][-1] - sum(self.channel_queues[1]) / self.graph_points
		directions = []
		if valueV > self.thresholds['UP']:
			directions.append('UP')
		elif valueV < self.thresholds['DOWN']:
			directions.append('DOWN')
		if valueH > self.thresholds['LEFT']:
			directions.append('LEFT')
		elif valueH < self.thresholds['RIGHT']:
			directions.append('RIGHT')
		return set(directions)


	def thresold_handler_derivadas(self, nvalues=125):
		'''Determina quais direçoes devem estar acessas na janela dos thresolds'''
		derivsV = [(self.channel_queues[0][-i] - self.channel_queues[0][-(i + 1)]) for i in range(1, nvalues + 1)]
		derivsH = [(self.channel_queues[1][-i] - self.channel_queues[1][-(i + 1)]) for i in range(1, nvalues + 1)]
		directions = []
		if sum(derivsV) / (nvalues / 244) > self.thresholds['UP']:
			directions.append('UP')
		elif sum(derivsV) / (nvalues / 244) < self.thresholds['DOWN']:
			directions.append('DOWN')
		if sum(derivsH) / (nvalues / 244) > self.thresholds['LEFT']:
			directions.append('LEFT')
		elif sum(derivsH) / (nvalues / 244) < self.thresholds['RIGHT']:
			directions.append('RIGHT')
		return set(directions)


	def value_to_bin(self, value, size):
		return format(value, f'0{size}b')  # converte e retorna o valor de inteiro para binario


	def bin_to_volt_value(self, bvalue):
		return (int(bvalue, 2) * 5 / (2 ** self.dresol))  # converte e retorna o valor de binario para escala em Volts


	def save_data_history(self, save_option='channel'):
		"""Saves data history to a file, data can be saved by:
			-> ordered - saves data to list as it has been received((channel, value))
			-> channel - saves data by list of values for each channel"""
		if save_option not in ['ordered', 'channel']:
			print('Invalid save options used!')
			return
		print(f"Saving data... ({len(self.data_history)} data points)")
		os.makedirs('./Saves', exist_ok=True)  # cria diretoria para gravar ficheiro
		with open(f'./Saves/DataSave_{save_option}.txt', 'w') as f:
			if save_option == 'ordered':  # grava dados de forma "ordenada"
				for c, v in self.data_history:
					f.write(f"({c},{v})")
			elif save_option == 'channel':  # grava dados por canal
				channels = [[] for _ in range(self.channel_count)]
				for c, v in self.data_history:
					channels[c].append(v)
				for channel in channels:
					for v in channel:
						f.write(f'({v})')
					f.write('\n')
		self.data_history.clear()  # limpa dados antigos
		print(f"EOG data has successfully been saved to:  './Saves/DataSave_{save_option}.txt'")


	def test_window(self, n=np.inf):
		"""Plots random data to see how how the window reacts"""
		i = -1
		while i < n:
			i += 1

			# cria valor aleatorio
			v1 = self.bin_to_volt_value(self.value_to_bin(np.random.randint(0, 2 ** self.dresol), 7))
			v2 = self.bin_to_volt_value(self.value_to_bin(np.random.randint(0, 2 ** self.dresol), 7))

			# faz update dos dados do canal
			self.channel_queues[0].append(v1)
			self.channel_queues[1].append(v2)

			# adiciona dado a historia
			self.data_history.append((0, v1))
			self.data_history.append((1, v2))

			# atualiza janela dos graficos a frequencia especificada
			if time.perf_counter() - self.graph_timer >= self.graph_actualization_time:
				self.graph_timer = time.perf_counter()
				self.update_graphs()  # atualiza display do canal

			# atualiza janela das direcoes e SNAKE a frequencia especificada
			if not self.show_only_graphs and time.perf_counter() - self.game_timer >= self.game_actualization_time:
				self.game_timer = time.perf_counter()
				directions = self.thresold_handler_simples()
				exit_event = self.threshold_win.move(directions)
				if exit_event:
					self.save_data_history()
					return


if __name__ == "__main__":
	com = ComHandler(com_port=None)
	com.test_window()
