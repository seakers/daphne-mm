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
import json
import _static.design_evaluator.python as truss_model
import matplotlib.pyplot as plt
import PIL.Image as Image
import warnings
import os
from pygmo import hypervolume
from scipy.stats import rankdata

warnings.filterwarnings('ignore')

author = 'Ashish Chaudhari'

doc = """
Backend and frontend of a human-AI collaborative tool for metamaterial design
"""

class Constants(BaseConstants):
	name_in_url = 'outreach_activity'
	players_per_group = None
	num_rounds = 1
	num_features = 5
	num_ticks = 100
	
	#Mechanical metamaterial related variables
	E = 0.7e09; # Young's Modulus for polymeric material (example: 10000 Pa)
	sel = 0.01; # Unit square side length (NOT individual truss length) (example: 5 cm)
	r = 5e-4 #element radius in m
	edgelist = np.array([[1,2], [1,6], [1,5], [1,4], [1,8], [2,3], [2,6], [2,5], [2,4], [2,7],
					[2,9], [3,6], [3,5], [3,4], [3,8], [5,6], [6,7], [6,8], [6,9], [4,5], 
					[5,7], [5,8], [5,9], [4,7], [4,8], [4,9], [7,8], [8,9]])-1;
	nucFac = 1;
	sidenum = (2*nucFac) + 1; 
	pos = truss_model.generateNC(sel, sidenum);
	target_c_ratio = 1; # Ratio of C22/C11 to target
	ref_point = [0, 1] #Order of objectives [Vertical Stifness, Volume Fraction]
	score_magnifier = 1
	objectives = ['Vertical Stiffness', 'Volume Fraction']
	constraints = ['Feasibility', 'Material']
	materials = {#Young's Modulus
		'Polyethylene HDPE': 0.8e09,
		'PVC': 4e09,
		'Aluminium 6061-T6': 69e09,
		'Copper': 117e09,
		'Steel ASTM-A36': 200e09
	}
	radii = {
		'0.2 mm': 0.0002,
		'0.3 mm': 0.0003,
		'0.4 mm': 0.0004
	}

	data_keys = ['Main']


class Subsession(BaseSubsession):

	def get_goals(self):
		return ['Maximize', 'Minimize']

	def get_instruction_url(self):
		instruction_url= Constants.name_in_url + "/" + "instructions_automation.html"
		return instruction_url

	def nodes(self):
		pos = Constants.pos
		sel = Constants.sel
		nodes = list()
		for i, p in enumerate(pos):
			nodes.append({'id':int(i), 'x':float(p[0]/sel), 'y':float(p[1]/sel)})
		return nodes

	def edges(self):
		edgelist = Constants.edgelist
		nodes = self.nodes()
		edges = list()
		for i in range(len(edgelist)):
			e = edgelist[i]
			edges.append({'id': str(e[0])+'-'+str(e[1]), 'index':i, 'source':nodes[e[0]], 'target':nodes[e[1]]})
		return edges

	def is_pareto_efficient(self, costs):
		"""
		Find the pareto-efficient points
		:param costs: An (n_points, n_costs) array
		:return: A (n_points, ) boolean array, indicating whether each point is Pareto efficient
		"""
		is_efficient = np.ones(costs.shape[0], dtype = bool)
		for i, c in enumerate(costs):
			is_efficient[i] = np.all(np.any(costs[:i]>=c, axis=1)) and np.all(np.any(costs[i+1:]>=c, axis=1))
		return is_efficient

	def convert_to_img(self, x, r):
		pos = Constants.pos
		edgelist = Constants.edgelist
		max_r = max(Constants.radii.values())
		min_r = min(Constants.radii.values())
		lw = 20*np.array(r)/max_r

		plt.ioff()
		fig, ax = plt.subplots()
		truss_model.show_meshplot(pos, edgelist, x, lw, ifMatrix=False, ax=ax)
		fig.savefig('image.png', bbox_inches='tight')
		img = Image.open('image.png').convert('L').resize((50,50))
		x = np.array(img)<255
		
		return x.astype('int')
	
	def creating_session(self):
		if self.round_number == 1:
			cwd = os.getcwd()
			# Reading data #Columns = design stiffness	volume_fraction	feasibility	stability vertical_lines horizontal_lines	diagonals	triangles	three_stars	image
			data = pd.read_csv("./_static/metamaterial_designs_normalized_filtered1.csv")
			data = data.drop_duplicates(subset=['obj1', 'obj2'], ignore_index=True)
			data = data.sort_values(['obj1', 'obj2'], ascending=[True, True], ignore_index=True)
			n_data = data.shape[0]

			# Adding pareto front information
			costs = data[['obj1', 'obj2']].values*np.array([[-1, 1]]) #Maximize stiffness and minimize volume fraction
			# Check if feasibility constraint is satisfied
			is_constr1 = data['constr1'] == 1
			ret = self.is_pareto_efficient(costs[is_constr1])	# Pareto front of the historic data
			data['is_pareto'] = np.zeros((n_data,)).astype(bool)
			data['is_pareto'][is_constr1] = ret
			for p in self.get_players():
				player_id = p.id_in_subsession
				data['is_pareto_response'+str(player_id)] = data['is_pareto']	# Pareto front after considering new responses evaluated by the designer
			data['id'] = np.arange(data.shape[0])
			self.session.vars = data.to_dict('list')

			#Storing the reference hypervolume
			ref_hv = hypervolume(costs[is_constr1]).compute(Constants.ref_point)
			self.session.vars['reference_hv'] = ref_hv

			#Initialize initial ranks and scores
			for g in self.get_groups():
				g.update_scoreboard(initialize=True)

class Group(BaseGroup):
	
	def update_scoreboard(self, initialize=False):
		players = self.get_players()

		if not initialize:
			#Calculate scores
			#First approach
			scores = []
			for p in players:
				if 'hv' not in p.participant.vars.keys():
					scores.append(self.session.vars['reference_hv'])
				else:
					scores.append(p.participant.vars['hv'])
			#Second approach
			# scores = [sum(p.participant.vars['is_pareto']*p.participant.vars['is_unique']) for p in players]
			#third approach
			# is_pareto = p.participant.vars['is_pareto']
			# objs = np.array(p.participant.vars[['obj1', 'obj2']])[is_pareto]
			# utopia = 1 - np.array(ref_point)[None,:]
			# scores = np.mean(np.sqrt(np.sum((objs-utopia)**2, axis=1)), axis=1)
			
			names = []
			for p in players:
				if p.user_firstname:
					names.append(p.user_firstname + ' ' + p.user_lastname)
				else:
					names.append(str(p.id_in_subsession))
		
		else:
			#First approach
			ref_hv = self.session.vars['reference_hv']
			scores = [Constants.score_magnifier*ref_hv for p in players]
			names = [str(p.id_in_subsession) for p in players]
			#Third approach
			# scores = [0 for p in players]

		ranks = rankdata(-1*np.array(scores), method='min')
		
		#Store the current ranks and scores
		scoreboard = dict()
		for i in range(len(players)):
			scoreboard[players[i].id_in_subsession] = dict(
						rank=int(ranks[i]),
						score=scores[i],
						name=names[i])
		self.session.vars['scoreboard'] = scoreboard

class Player(BasePlayer):

	user_firstname = models.TextField()
	user_lastname = models.TextField()

	def update_pareto(self):
		# Historic dataset
		data = np.array([self.session.vars.get(key) for key in ['obj1', 'obj2']]).T #dictionary
		n_data = data.shape[0]

		# Gather old responses
		prev_response = np.array([self.participant.vars.get(key) for key in ['obj1', 'obj2']]).T  #dictionary
		n_response = prev_response.shape[0]

		# Gathering objectives data
		tem1 = data
		tem2 = prev_response
		costs = np.vstack([tem1, tem2])*np.array([[-1, 1]]) #Maximize stiffness and minimize volume fraction
		# Constraint Feasibility=1 should be satisfied
		if_constr1 = np.array([v==1 for v in self.session.vars['constr1']] + [v==1 for v in self.participant.vars['constr1']])
		# Find new pareto and update databse
		ret = self.subsession.is_pareto_efficient(costs[if_constr1])
		is_pareto = np.zeros((n_data+n_response,)).astype(bool)
		is_pareto[if_constr1] = ret

		# self.session.vars['is_pareto_new'] = ret[0:n_data].tolist()
		self.participant.vars['is_pareto'] =  is_pareto[n_data:].tolist()
		self.session.vars['is_pareto_response' + str(self.id_in_subsession)] =  is_pareto[0:n_data].tolist()
		
		#Calculate the hypervolume improvement
		hv = hypervolume(costs[if_constr1]).compute(Constants.ref_point)
		self.participant.vars['hv'] = np.around(hv,3)

		#Store boolean on whether designs are unique
		_, indices = np.unique(costs, axis=0, return_index=True)
		is_unique = np.zeros(n_data+n_response, dtype=bool)
		is_unique[indices] = True	
		self.participant.vars['is_unique'] = is_unique[n_data:].tolist()
		self.session.vars['is_unique' + str(self.id_in_subsession)] =  is_unique[0:n_data].tolist()

		return is_pareto[0:n_data].tolist()

	def update_response_database(self, response):
		# Gather old responses
		prev_response = self.participant.vars
		for key in response.keys():
			if key not in prev_response:
				prev_response[key]=[]
			prev_response[key].append(response[key])

	def live_method(self, data):

		if data['message']=='clean image':
			#For cleaning data
			x = np.array(data['x'])
			r = data['r']#Must in meters
			x[x>0.25]=1
			x[x<0.25]=0
			x_img = self.subsession.convert_to_img(x, r)
			image = x_img.tolist()
			
			return {self.id_in_group: dict(message='clean image',image=image)}

		elif data['message']=='test design':
			#Load data even if it may be empty
			# x is a bitstring design vector
			# z is a feature vector
			x = np.array(data['x'])
			x[x>0.25]=1
			x[x<0.25]=0

			r = data['r']#Must in meters
			E = data['E']#Must be in Pa

			if np.any(np.isin(x, ['', None, 'nan'])):
				x = np.ones(Constants.edgelist.shape[0])

			# Running the design evaluator and creating a response
			x = truss_model.repeatable_des(x)
			r = truss_model.repeatable_des(r)
			obj1, obj2 = truss_model.multiobjectives(x, Constants.sidenum, Constants.sel, E, r, Constants.edgelist, 1)
			edges_des = Constants.edgelist[x.astype(bool)]
			constr1 = truss_model.feasibility(Constants.pos, edges_des, Constants.sidenum)
			constr2 = [key for key, value in Constants.materials.items() if value==E]
			x_img = self.subsession.convert_to_img(x, r)
			image = json.dumps(x_img.tolist())
			design = json.dumps(x.tolist())

			response = dict(design_bitstring=design, obj1=obj1, obj2=obj2, constr1=constr1, constr2=constr2, image=image,
			is_pareto=None)
			# response.update(data)

			# Check if any element is int32
			for k, v in response.items():
				if isinstance(v, np.int32) or isinstance(v, np.int64):
					response[k] = int(v)

			# Update databse and Check if pareto
			self.update_response_database(response)

			# Update pareto information; Returns pareto information for historic data
			is_pareto_response = self.update_pareto()

			# Retrive updated data rom database
			response_data = self.participant.vars

			#scoreboard
			self.group.update_scoreboard()
			scoreboard = self.session.vars['scoreboard']
			print(scoreboard)
			return {self.id_in_group: dict(message='test design',response_data=response_data, is_pareto_response=is_pareto_response, scoreboard=scoreboard)}

def custom_export(players):
	# header row
	ctr=0
	for p in players:
		data = p.participant.vars
		if data:
			if ctr==0:
				keys = list(data.keys())
				yield ['session', 'participant_code'] + keys
				ctr+=1
			n_data = len(data[keys[0]])

			for i in range(n_data):
				row = [p.session.code, p.participant.code]
				row = row + [data[k][i] for k in keys]
				yield row