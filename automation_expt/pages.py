from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants, Subsession, Player
import pandas as pd
import numpy as np
import pickle as pickle
import json

class BasePage(Page):

	live_method = 'live_method'


class Instructions(BasePage):

	page_name = 'Instructions'
	
	def vars_for_template(self):
		return dict(
			instr_duration=self.session.config['instr_duration'],
			instruction_url=self.subsession.get_instruction_url(),
			files_path=Constants.name_in_url,
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
			images_dc_test = images_pretest,
		)

class Main(BasePage):

	page_name = 'Main'
	data_key = Constants.data_keys[0]

	title_str = ''
	page_instructions = ''


	def get_timeout_seconds(self):
		return self.session.config['task_duration']

	def vars_for_template(self):
		return dict(
			instruction_url = self.subsession.get_instruction_url(),
			task = self.page_name + ": " + self.title_str
		)

	def js_vars(self):
		nodes = self.subsession.nodes()
		edges = self.subsession.edges()
		indices = json.loads(self.player.feature_ind)
		if self.page_name == 'Task 3':
			indices = [1-i for i in indices]
			
		return dict(
			data_key = self.data_key,
			data = self.session.vars[self.data_key],
			response_data = self.participant.vars[self.data_key],
			nodes = nodes,
			edges = edges,
			feature_ind = indices,
			feature_names = self.player.get_feature_names(indices),
			goals = self.subsession.get_goals(),
			page_instructions=self.page_instructions
		)

class Task1(Main):

	page_name = 'Task 1'
	data_key = Constants.data_keys[0]

	title_str = 'Change Design'
	page_instructions = "<br>".join(['<b>Exploring different metamaterials to (1) learn what good metamaterials have in common and (2) improve the Pareto front </b>',
						' &nbsp; 1. Select a metamaterial by clicking on the tradespace plot',
						' &nbsp; 2. Add or remove links using "Change Design" functionality',
						' &nbsp; 3. Test the new metamaterial',
						' &nbsp; 4. Repeat with different metamaterials '])

	# '<b> Goal </b>: Create better metamaterials and improve the Pareto front' + '<br>' + 
	# 			'<pre style="background-color:#ffffe6;">1. Select a metamaterial by clicking on the tradespace plot. ' + '<br>' + 
	# 			'2. Add or remove links using "Change Design" functionality. ' + '<br>' + 
	# 			'3. Test new metamaterial using the "Test metamaterial" button.' + '<br>' + 
	# 			'4. Repeat with different metamaterials </pre>';

class Questionnaire1(BasePage):

	page_name = 'Questionnaire1'

	form_model = 'player'
	form_fields = ['answers1']

	def vars_for_template(self):
		images_dc_test = self.subsession.get_design_tests()
		return dict(
			ids_dc_test = range(1, len(images_dc_test)//2+1),
		)

	def js_vars(self):
		images_dc_test = self.subsession.get_design_tests()
		return dict(
			# data = self.session.vars,
			# response_data = self.participant.vars,
			images_dc_test = images_dc_test,
			# goals = self.subsession.get_goals(),
		)

class Task2(Main):

	page_name = 'Task 2'
	data_key = Constants.data_keys[1]

	title_str = 'Change Feature'
	page_instructions = "<br>".join(['<b>Explore different features to (1) learn their effects on the objectives and (2) improve the Pareto front </b>',
						' &nbsp; 1. Select a metamaterial by clicking on the tradespace plot.',
						' &nbsp; 2. Increase or decrease the feature(s) using the "Change Feature" functionality.',
						' &nbsp; 3. Test the generated metamaterial using the "Test metamaterial" button.',
						' &nbsp; 4. Repeat with different metamaterials'])

class Task3(Main):

	page_name = 'Task 3'
	data_key = Constants.data_keys[2]

	title_str = 'Automated Feature Change'
	page_instructions = "<br>".join(['<b>Explore different features to (1) learn their effects on the objectives and (2) improve the Pareto front </b>',
						' &nbsp; 1. Select a metamaterial by clicking on the tradespace plot.',
						' &nbsp; 2. Select the overall change. The higher the overall change, the more the tool explores far away from the selected metamaterial.',
						' &nbsp; 3. Review the suggested feature changes and test using the "Test metamaterial" button.',
						' &nbsp; 4. Repeat with different metamaterials '])

class Questionnaire2(BasePage):

	page_name = 'Questionnaire2'

	form_model = 'player'
	form_fields = ['answers2']

	def vars_for_template(self):
		indices = np.array(json.loads(self.player.feature_ind))
		feature_names = self.player.get_feature_names(indices)
		images_dfi_test = self.subsession.get_design_feature_tests(indices)
		return dict(
			feature_names = feature_names,
			ids_dfi_test = range(1, len(images_dfi_test)//2+1),
		)

	def js_vars(self):
		indices = np.array(json.loads(self.player.feature_ind))
		images_dfi_test = self.subsession.get_design_feature_tests(indices)
		return dict(
			images_dfi_test = images_dfi_test,
		)

class Questionnaire3(BasePage):

	page_name = 'Questionnaire3'

	form_model = 'player'
	form_fields = ['answers3']

	def vars_for_template(self):
		indices = 1 - np.array(json.loads(self.player.feature_ind))
		feature_names = self.player.get_feature_names(indices)
		images_dfi_test = self.subsession.get_design_feature_tests(indices)
		return dict(
			feature_names = feature_names,
			ids_dfi_test = range(1, len(images_dfi_test)//2+1),
		)

	def js_vars(self):
		indices = 1 - np.array(json.loads(self.player.feature_ind))
		images_dfi_test = self.subsession.get_design_feature_tests(indices)
		return dict(
			images_dfi_test = images_dfi_test,
		)

class Questionnaire4(BasePage):

	page_name = 'Questionnaire4'

	form_model = 'player'
	form_fields = ['answers4']

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
		#Questionnaire 2
		test1_answers = self.subsession.get_design_test_answers()
		test1_player_answers = [int(a) for a in json.loads(self.player.answers1)]
		test1_ifcorrect = [x==y for x, y in zip(test1_answers, test1_player_answers)]

		#Questionnaire 3
		idx1 = np.array(json.loads(self.player.feature_ind))
		feature_names1 = self.player.get_feature_names(idx1)
		test2_answers = self.subsession.get_design_feature_test_answers(idx1)
		test2_player_answers = [int(a) for a in json.loads(self.player.answers2)]
		test2_ifcorrect1 = [x==y for x, y in zip(test2_answers, test2_player_answers)]

		#Questionnaire 4
		idx2 = 1 - np.array(json.loads(self.player.feature_ind))
		feature_names2 = self.player.get_feature_names(idx2)
		test3_answers = self.subsession.get_design_feature_test_answers(idx2)
		test3_player_answers = [int(a) for a in json.loads(self.player.answers3)]
		test3_ifcorrect1 = [x==y for x, y in zip(test3_answers, test3_player_answers)]

		return dict(
			ids_dc_test = range(1, len(test1_answers)//2+1),
			feature_names = feature_names1 + feature_names2,
			n_correct = sum(test1_ifcorrect) + sum(test2_ifcorrect1) + sum(test3_ifcorrect1),
			n_questions = len(test1_player_answers) + len(test2_player_answers) + len(test3_player_answers)
		)


	def js_vars(self):
				#Questionnaire 2
		images_dc_test = self.subsession.get_design_tests()
		dc_test_answers = self.subsession.get_design_test_answers()
		dc_test_player_answers = [int(a) for a in json.loads(self.player.answers1)]
		dc_test_ifcorrect = [x==y for x, y in zip(dc_test_answers, dc_test_player_answers)]

		#Questionnaire 3
		idx1 = np.array(json.loads(self.player.feature_ind))
		feature_names1 = self.player.get_feature_names(idx1)
		images_dfi_test1 = self.subsession.get_design_feature_tests(idx1)
		dfi_test_answers1 = self.subsession.get_design_feature_test_answers(idx1)
		dfi_test_player_answers1 = [int(a) for a in json.loads(self.player.answers2)]
		dfi_test_ifcorrect1 = [x==y for x, y in zip(dfi_test_answers1, dfi_test_player_answers1)]

		#Questionnaire 4
		idx2 = 1 - np.array(json.loads(self.player.feature_ind))
		feature_names2 = self.player.get_feature_names(idx2)
		images_dfi_test2 = self.subsession.get_design_feature_tests(idx2)
		dfi_test_answers2 = self.subsession.get_design_feature_test_answers(idx2)
		dfi_test_player_answers2 = [int(a) for a in json.loads(self.player.answers3)]
		dfi_test_ifcorrect2 = [x==y for x, y in zip(dfi_test_answers2, dfi_test_player_answers2)]

		return dict(
			data = self.session.vars[Constants.data_keys[-1]],
			response_data = self.participant.vars[Constants.data_keys[-1]],
			images_dc_test = images_dc_test,
			images_dfi_test = images_dfi_test1+images_dfi_test2,
			dc_test_player_answers = dc_test_player_answers,
			dc_test_answers = dc_test_answers,
			dc_test_ifcorrect = dc_test_ifcorrect,
			dfi_test_answers = dfi_test_answers1+dfi_test_answers2,
			dfi_test_player_answers = dfi_test_player_answers1+dfi_test_player_answers2,
			dfi_ifcorrect = dfi_test_ifcorrect1+dfi_test_ifcorrect2,
			goals = self.subsession.get_goals()
		)

page_sequence = [Instructions, Pretest, Task3, Questionnaire3, Task2, Questionnaire2, Task1, Questionnaire1, Questionnaire4, Results]
