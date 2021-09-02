from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants, Subsession, Player
import pandas as pd
import numpy as np
import pickle as pickle
import json


class UserInput(Page):

	form_model = 'player'
	form_fields = ['user_firstname', 'user_lastname']

	def vars_for_template(self):
		pass

	def before_next_page(self):
		my_name = self.player.user_firstname + ' ' + self.player.user_lastname
		my_id = self.player.id_in_subsession

		#Update the name in the database
		scoreboard = self.session.vars['scoreboard']
		scoreboard[my_id]['name'] = my_name

class Instructions(Page):

	page_name = 'Instructions'
	
	def vars_for_template(self):
		return dict(
			instr_duration=self.session.config['instr_duration'],
			instruction_url=self.subsession.get_instruction_url()
		)


class OutreachMain(Page):

	page_name = 'Outreach_Main'
	live_method = 'live_method'

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
			data_key = Constants.data_keys[0],
			data = self.session.vars,
			response_data = self.participant.vars,
			nodes = nodes,
			edges = edges,
			radii = Constants.radii,
			materials = Constants.materials,
			goals = self.subsession.get_goals(),
		)

class Results(Page):

	page_name = 'Results'

	def vars_for_template(self):
		pass


	def js_vars(self):
		pass

page_sequence = [UserInput, OutreachMain]
