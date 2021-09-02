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

warnings.filterwarnings('ignore')

author = 'Ashish Chaudhari'

doc = """
Backend and frontend of a human-AI collaborative tool for metamaterial design
"""

class Constants(BaseConstants):
	name_in_url = 'automation_expt'
	players_per_group = None
	num_rounds = 1
	num_features = 5
	num_ticks = 100

	abstract_features = ["Feature 1", "Feature 2", "Feature 3", "Feature 4", "Feature 5"]
	semantic_attributes = ["Horizontal\nLines",	"Vertical Lines",	"Diagonals", "Triangles", "Three Stars"]
	feature_names = abstract_features+semantic_attributes

	attribute_keys = ['attr1', 'attr2', 'attr3', 'attr4', 'attr5']

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

	objectives = ['Vertical Stiffness', 'Volume Fraction']
	constraints = ['Feasibility', 'Stability']

	choices_sa_test = ['Strongly agree', 'Agree', 'Undecided', 'Diagree', 'Strongly disagree']

	# Different initial data for each treatment
	data_keys = ['Task1', 'Task2', 'Task3']

class Subsession(BaseSubsession):

	# decoder = tf.keras.models.load_model('metamaterial_design/static/bvae_decoder.h5')
	# encoder_bitstring = tf.keras.models.load_model('metamaterial_design/static/encoder_bitstring.h5')

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
			is_efficient[i] = np.all(np.any(costs[:i]>=c, axis=1)) and np.all(np.any(costs[i+1:]>=c, axis=1))
		return is_efficient

	def convert_to_img(self, x):
		pos = Constants.pos
		edgelist = Constants.edgelist

		plt.ioff()
		fig, ax = plt.subplots()
		truss_model.show_meshplot(pos, edgelist, x, ifMatrix=False, ax=ax)
		fig.savefig('image.png', bbox_inches='tight')
		img = Image.open('image.png').convert('L').resize((28,28))
		x = np.array(img)<255
		
		return x.astype('int')

	def add_pareto_column(self, data):
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
		return data
	
	def creating_session(self):
		if self.round_number == 1:
			cwd = os.getcwd()
			# Reading data #Columns = design stiffness	volume_fraction	feasibility	stability vertical_lines horizontal_lines	diagonals	triangles	three_stars	image
			#Store initial tradespace data for three treatments
			for i in range(3):
				data = pd.read_csv("./_static/metamaterial_designs_normalized_filtered"+str(i+1)+".csv")
				data = self.add_pareto_column(data)
				self.session.vars[Constants.data_keys[i]] = data.to_dict('list')

			#Set features used by the user
			for p in self.get_players():
				n = len(Constants.feature_names)
				idx = np.random.choice(n, replace=False, size=5)
				feature_ind = np.zeros(n)
				feature_ind[idx] = 1
				p.feature_ind = json.dumps(list(feature_ind))
				for data_key in Constants.data_keys:
					p.participant.vars[data_key] = dict()

	def get_design_pretests(self):
		# Read designs related to design comparison tests
		images_pre = pd.read_csv("./_static/"+Constants.name_in_url+"/design_pretests.csv", delimiter=',')
		images_pre = images_pre.to_dict('list')['image']

		return images_pre

	def get_design_tests(self):
		# Read designs related to design comparison tests
		images_dc_test = pd.read_csv("./_static/"+Constants.name_in_url+"/design_comparison_tests.csv", delimiter=',')
		images_dc_test = images_dc_test.to_dict('list')['image']

		return images_dc_test

	def get_design_test_answers(self):
		# Read designs related to design comparison tests
		dc_test_answers = pd.read_csv("./_static/"+Constants.name_in_url+"/design_comparison_answers.csv", delimiter=',')
		dc_test_answers = dc_test_answers.to_dict('list')['answers']

		return dc_test_answers 

	def get_design_feature_tests(self, indices):

		# Read features related to feature comparison tests
		images_dfi_test = pd.read_csv("./_static/design_feature_identification_tests.csv", delimiter=',')

		images_dfi_test = images_dfi_test[indices.astype(bool)].to_dict('list')['image']

		return images_dfi_test

	def get_design_feature_test_answers(self, indices):
		# Indices for two questions: vertical stiffness and volume fraction
		indices = np.repeat(indices, 2)

		# Read designs related to design identification tests
		dfi_test_answers = pd.read_csv("./_static/design_feature_identification_answers.csv", delimiter=',')
		
		dfi_test_answers = dfi_test_answers[indices.astype(bool)].to_dict('list')['answers']
		
		return dfi_test_answers

	def get_self_assessment_tests(self):
		# Read features related to feature comparison tests
		sa_test = pd.read_csv("./_static/self_assessment_questions.csv", delimiter=',')
		sa_test = sa_test.values.tolist()
		sa_test_dict = []
		for i in range(len(sa_test)):
			sa_test_dict.append({'id':i, 'text':sa_test[i][0]})
		return sa_test_dict


class Group(BaseGroup):
	pass

class Player(BasePlayer):

	feature_ind = models.TextField()

	answers0 = models.TextField()
	answers1 = models.TextField()
	answers2 = models.TextField()
	answers3 = models.TextField()
	answers4 = models.TextField()

	def get_feature_names(self, indices):
		return [Constants.feature_names[i] for i,t in enumerate(indices) if t==1]

	def update_pareto(self, data_key):
		# Historic dataset
		data = self.session.vars[data_key]

		# Gather old responses
		prev_response = self.participant.vars[data_key]
		
		# Gathering objectives data
		tem1 = np.array([data.get(key) for key in ['obj1', 'obj2']]).T #dictionary
		n_data = tem1.shape[0]
		tem2 = np.array([prev_response.get(key) for key in ['obj1', 'obj2']]).T  #dictionary
		n_response = tem2.shape[0]

		costs = np.vstack([tem1, tem2])*np.array([[-1, 1]]) #Maximize stiffness and minimize volume fraction
		# Constraint Feasibility=1 should be satisfied
		if_constr1 = np.array([v==1 for v in data['constr1']] + [v==1 for v in prev_response['constr1']])
		# Find new pareto and update databse
		ret = self.subsession.is_pareto_efficient(costs[if_constr1])
		is_pareto = np.zeros((n_data+n_response,)).astype(bool)
		is_pareto[if_constr1] = ret

		# self.session.vars['is_pareto_new'] = ret[0:n_data].tolist()
		prev_response['is_pareto'] =  is_pareto[n_data:].tolist()
		data['is_pareto_response' + str(self.id_in_subsession)] =  is_pareto[0:n_data].tolist()
		
		return is_pareto[0:n_data].tolist()

	def update_response_database(self, response, data_key):
		# Gather old responses
		if data_key not in self.participant.vars.keys():
			self.participant.vars[data_key] = dict()

		prev_response = self.participant.vars[data_key]
		for key in response.keys():
			if key not in prev_response:
				prev_response[key]=[]
			prev_response[key].append(response[key])

	def live_method(self, data):

		if data['message']=='clean image':
			#For cleaning data
			x = np.array(data['x'])
			x[x>0.25]=1
			x[x<0.25]=0
			x_img = self.subsession.convert_to_img(x)
			image = x_img.tolist()

			return {self.id_in_group: dict(message='clean image',image=image)}

		elif data['message']=='test design':
			#Load data even if it may be empty
			# x is a bitstring design vector
			# z is a feature vector
			x = np.array(data['x'])
			x[x>0.25]=1
			x[x<0.25]=0
			
			# z = np.array([data['z']])
			# if ~np.any(np.isin(z, ['', None, 'nan'])):
			# 	x_img = self.subsession.decoder(z)
			# 	x = self.subsession.encoder_bitstring(x_img).numpy()[0]
			# 	x[x>0.25]=1
			# 	x[x<0.25]=0

			if np.any(np.isin(x, ['', None, 'nan'])):
				x = np.ones(Constants.edgelist.shape[0])
				
			# Running the design evaluator and creating a response
			# Repeat the edges in a 2d place
			x = truss_model.repeatable_des(x)
			obj1, obj2 = truss_model.multiobjectives(x, Constants.nucFac, Constants.sel, Constants.E, Constants.r, Constants.edgelist, 1)
			edges_des = Constants.edgelist[x.astype(bool)]
			constr1 = truss_model.feasibility(Constants.pos, edges_des)
			constr2 = 0#truss_model.stability(Constants.sidenum, edges_des, Constants.pos)
			x_img = self.subsession.convert_to_img(x)
			image = json.dumps(x_img.tolist())
			design = json.dumps(x.tolist())

			response = dict(design_bitstring=design, obj1=obj1, obj2=obj2, constr1=constr1, constr2=constr2, image=image,
			is_pareto=None)
			response.update(data)
			# Check if any element is int32
			for k, v in response.items():
				if isinstance(v, np.int32) or isinstance(v, np.int64):
					response[k] = int(v)

			# Update databse and Check if pareto
			data_key = data['data_key']
			self.update_response_database(response, data_key)

			# Update pareto information; Returns pareto infroamtion for historic data
			is_pareto_response = self.update_pareto(data_key)

			# Retrive updated data rom database
			response_data = self.participant.vars[data_key]

			return {self.id_in_group: dict(message='test design',response_data=response_data, is_pareto_response=is_pareto_response)}

def custom_export(players):

	# Different datasets for different treatments
	data_keys = Constants.data_keys

	ctr=0
	for p in players:
		for data_key in data_keys:
			data = p.participant.vars[data_key]
			if data:
				if ctr==0:
					keys = list(data.keys())
					# header row
					yield ['session', 'participant_code'] + keys
					ctr+=1
				n_data = len(data[keys[0]])
				for i in range(n_data):
					row = [p.session.code, p.participant.code]
					row = row + [data[k][i] for k in keys]
					yield row