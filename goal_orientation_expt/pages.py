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

class Pretest(BasePage):

	page_name = 'Pretest'

	form_model = 'player'
	form_fields = ['answers0']

	def vars_for_template(self):
		images_pretest = self.subsession.get_design_pretests()
		return dict(
			ids_pretest = range(1, len(images_pretest)//2+1),
		)

	def js_vars(self):
		images_pretest = self.subsession.get_design_pretests()
		return dict(
			data = self.session.vars,
			response_data = self.participant.vars,
			images_dc_test = images_pretest,
		)

class Task1(BasePage):

	page_name = 'Task1'

	def get_timeout_seconds(self):
		return self.session.config['task_duration']

	def vars_for_template(self):
		return dict(
			instruction_url=self.subsession.get_instruction_url()
		)

	def js_vars(self):
		nodes = self.subsession.nodes()
		edges = self.subsession.edges()
		return dict(
			data = self.session.vars,
			response_data = self.participant.vars,
			nodes = nodes,
			edges = edges,
			feature_names = Constants.semantic_attributes if self.session.config['if_attributes']==1 else Constants.abstract_features,
			goals = self.subsession.get_goals()
		)

class Questionnaire1(BasePage):

	page_name = 'Questionnaire1'

	form_model = 'player'
	form_fields = ['answers1']

	def vars_for_template(self):
		images_dc_test, images_di_test = self.subsession.get_design_tests()
		return dict(
			ids_dc_test = range(1, len(images_dc_test)//2+1),
			ids_di_test = range(1, len(images_di_test)+1),
			instruction_url=self.subsession.get_instruction_url()
		)

	def js_vars(self):
		images_dc_test, images_di_test = self.subsession.get_design_tests()
		return dict(
			data = self.session.vars,
			response_data = self.participant.vars,
			images_dc_test = images_dc_test,
			images_di_test = images_di_test,
			goals = self.subsession.get_goals()
		)

class Task2(BasePage):

	page_name = 'Task2'

	def get_timeout_seconds(self):
		return self.session.config['task_duration']

	def vars_for_template(self):
		return dict(
			instruction_url=self.subsession.get_instruction_url()
		)

	def js_vars(self):
		nodes = self.subsession.nodes()
		edges = self.subsession.edges()
		return dict(
			data = self.session.vars,
			response_data = self.participant.vars,
			nodes = nodes,
			edges = edges,
			feature_images = self.subsession.get_feature_images(),
			feature_names = self.subsession.get_feature_names(),
			goals = self.subsession.get_goals()
		)

class Main(BasePage):

	page_name = 'Main'

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
		return dict(
			data = self.session.vars,
			response_data = self.participant.vars,
			nodes = nodes,
			edges = edges,
			feature_names = self.subsession.get_feature_names(),
			goals = self.subsession.get_goals()
		)

class Questionnaire2(BasePage):

	page_name = 'Questionnaire2'

	form_model = 'player'
	form_fields = ['answers2']

	def vars_for_template(self):
		images_fc_test, images_fi_test = self.subsession.get_feature_tests()
		return dict(
			ids_fc_test = range(1, len(images_fc_test)//2+1),
			ids_fi_test = range(1, len(images_fi_test)+1)
		)

	def js_vars(self):
		images_fc_test, images_fi_test = self.subsession.get_feature_tests()
		return dict(
			images_fc_test = images_fc_test,
			images_fi_test = images_fi_test,
			goals = self.subsession.get_goals()
		)

class Questionnaire3(BasePage):

	page_name = 'Questionnaire3'

	form_model = 'player'
	form_fields = ['answers3']

	def vars_for_template(self):
		questions_sa_test = self.subsession.get_self_assessment_tests()
		n_sa_test = len(questions_sa_test)
		return dict(
			questions_sa_test=questions_sa_test,
			choices_sa_test=Constants.choices_sa_test,
			n_choices = len(Constants.choices_sa_test)
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

page_sequence = [Main, Instructions, Pretest, Task1, Questionnaire1, Task2, Questionnaire2, Questionnaire3, Results]
