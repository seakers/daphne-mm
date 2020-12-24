from otree.api import (
	models,
	widgets,
	BaseConstants,
	BaseSubsession,
	BaseGroup,
	BasePlayer,
	Currency as c,
	currency_range,
)
import numpy as np
import pandas as pd


author = 'Ashish Chaudhari'

doc = """
Backend and frontend of human-AI collaborative tool for metamaterial design
"""


class Constants(BaseConstants):
	name_in_url = 'metamaterial_design'
	players_per_group = None
	num_rounds = 1
	num_features = 8
	num_ticks = 13

	pos = [[0,0], [0,0.5], [0,1], [0.5,0], [0.5,0.5], [0.5,1], [1,0], [1,0.5], [1,1]]
	edgelist = [[0, 1], [0, 2], [0, 3], [0, 4], [0, 5], [0, 6], [0, 7], [0, 8], [1, 2], [1, 3], [1, 4], [1, 5],
       [1, 6], [1, 7], [1, 8], [2, 3], [2, 4], [2, 5], [2, 6], [2, 7], [2, 8], [3, 4], [3, 5], [3, 6], [3, 7], [3, 8],
       [4, 5], [4, 6], [4, 7], [4, 8], [5, 6], [5, 7], [5, 8], [6, 7], [6, 8], [7, 8]]

class Subsession(BaseSubsession):

	def nodes(self):
		pos = Constants.pos
		nodes = list()
		for i, p in enumerate(pos):
			nodes.append({'id':int(i), 'x':float(p[0]), 'y':float(p[1])})
		return nodes

	def edges(self):
		edgelist = Constants.edgelist
		nodes = self.nodes()
		edges = list()
		for e in edgelist:
			edges.append({'id': str(e[0])+'-'+str(e[1]), 'source':nodes[e[0]], 'target':nodes[e[1]]})
		return edges

	def is_pareto_efficient(self, costs):
		"""
		Find the pareto-efficient points
		:param costs: An (n_points, n_costs) array
		:return: A (n_points, ) boolean array, indicating whether each point is Pareto efficient
		"""
		is_efficient = np.ones(costs.shape[0], dtype = bool)
		for i, c in enumerate(costs):
			is_efficient[i] = np.all(np.any(costs[:i]>c, axis=1)) and np.all(np.any(costs[i+1:]>c, axis=1))
		return is_efficient

	
	def creating_session(self):
		if self.round_number == 1:
			# Reading data
			data = pd.read_csv("./metamaterial_design/static/bitstring_image_designs_filtered.csv")

			# Adding pareto front information
			costs = -1*data[['obj1', 'obj2']].values
			data['is_pareto'] = self.is_pareto_efficient(costs)
			data['id'] = np.arange(data.shape[0])
			self.session.vars = data.to_dict('list')

class Group(BaseGroup):
	pass


class Player(BasePlayer):
	pass
