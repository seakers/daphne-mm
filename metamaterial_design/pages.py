from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants
import pandas as pd
import numpy as np
import pickle as pickle


class MyPage(Page):

	def js_vars(self):
		nodes = self.subsession.nodes()
		edges = self.subsession.edges()
		return dict(
			data= self.session.vars,
			nodes= nodes,
			edges= edges
		)

class ResultsWaitPage(WaitPage):
	pass


class Results(Page):
	pass


page_sequence = [MyPage, ResultsWaitPage, Results]
