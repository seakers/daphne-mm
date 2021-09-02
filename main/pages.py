from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants, Subsession, Player
import pandas as pd
import numpy as np
import pickle as pickle
import json

class BasePage(Page):

	def is_displayed(self):
		return self.page_name in self.session.config['page_sequence']

	live_method = 'live_method'


class Instructions(BasePage):

	page_name = 'Instructions'
	
	def vars_for_template(self):
		return dict(
			instr_duration=self.session.config['instr_duration'],
			instruction_url=self.subsession.get_instruction_url()
		)


class Main(BasePage):

	page_name = 'Main'
	data_key = Constants.data_keys[0]

	def get_timeout_seconds(self):
		return self.session.config['task_duration']

	def vars_for_template(self):
		return dict(
			instruction_url = self.subsession.get_instruction_url(),
			task = 'Mechanical Metamaterial Design'
		)

	def js_vars(self):
		nodes = self.subsession.nodes()
		edges = self.subsession.edges()
		indices = json.loads(self.player.feature_ind)
		if self.page_name == 'Task3':
			indices = [1-i for i in indices]
			
		return dict(
			data_key = data_key,
			data = self.session.vars[data_key],
			response_data = self.participant.vars[data_key],
			nodes = nodes,
			edges = edges,
			feature_ind = indices,
			feature_names = self.player.get_feature_names(json.loads(self.player.feature_ind)),
			goals = self.subsession.get_goals(),
		)



class Results(BasePage):

	page_name = 'Results'

	def vars_for_template(self):
		design_test_answers = self.subsession.get_design_test_answers()
		player_answers1 = [int(a) for a in json.loads(self.player.answers1)]
		design_test_answers_ifcorrect = [x==y for x, y in zip(design_test_answers, player_answers1)]

		feature_test_answers = self.subsession.get_feature_test_answers()
		player_answers2 = [int(a) for a in json.loads(self.player.answers2)]
		feature_test_answers_ifcorrect = [x==y for x, y in zip(feature_test_answers, player_answers2)]

		images_dc_test, images_di_test = self.subsession.get_design_tests()
		images_fc_test, images_fi_test = self.subsession.get_feature_tests()
		return dict(
			ids_dc_test = range(1, len(images_dc_test)//2+1),
			ids_di_test = range(1, len(images_di_test)+1),
			ids_fc_test = range(1, len(images_fc_test)//2+1),
			ids_fi_test = range(1, len(images_fi_test)+1),
			n_correct = sum(feature_test_answers_ifcorrect) + sum(design_test_answers_ifcorrect),
			n_questions = len(feature_test_answers) + len(design_test_answers)
		)


	def js_vars(self):
		design_test_answers = self.subsession.get_design_test_answers()
		player_answers1 = [int(a) for a in json.loads(self.player.answers1)]
		design_test_answers_ifcorrect = [x==y for x, y in zip(design_test_answers, player_answers1)]

		feature_test_answers = self.subsession.get_feature_test_answers()
		player_answers2 = [int(a) for a in json.loads(self.player.answers2)]
		feature_test_answers_ifcorrect = [x==y for x, y in zip(feature_test_answers, player_answers2)]

		images_dc_test, images_di_test = self.subsession.get_design_tests()
		images_fc_test, images_fi_test = self.subsession.get_feature_tests()
		return dict(
			data = self.session.vars,
			response_data = self.participant.vars,
			images_dc_test = images_dc_test,
			images_di_test = images_di_test,
			images_fc_test = images_fc_test,
			images_fi_test = images_fi_test,
			player_answers1 = player_answers1,
			player_answers2 = player_answers2,
			design_test_answers = design_test_answers,
			design_test_answers_ifcorrect = design_test_answers_ifcorrect,
			feature_test_answers = feature_test_answers,
			feature_test_answers_ifcorrect = feature_test_answers_ifcorrect,
			goals = self.subsession.get_goals()
		)

page_sequence = [Main]
