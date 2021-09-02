from os import environ

SESSION_CONFIGS = [
		dict(
			name='main',
			display_name="Metamaterial Design - Main",
			num_demo_participants=3,
			app_sequence=['main'],
			task_duration=180*60,
			instr_duration=5*60,
			if_performance_goal=1, #[0:'learning', 1:'performance']
			if_attributes=1, #[0:'Do not show semantic attributes', 1:'Show semantic attributes']
			dse_mode=0, #[0:'all', 1:'build_your_own', 2:'change_features', 3:'auto_suggestions'],
			page_sequence=['Main'],#'Instructions', 'Pretest', 'Task1', 'Questionnaire1', 'Task2', 'Questionnaire2', 'Questionnaire3', 'Results'],
			doc=
			"""
		    	| 'task_duration': Number of seconds user spends on the task\n
		    	| 'instr_duration': Minimum number of seconds a user should reads instructions\n
		    	| 'performance_goal': [0:'learning', 1:'performance']\n
				| 'if_atttributes': [0:'Do not show semantic attributes', 1:'Show semantic attributes']\n
				| 'dse_mode':[0:'all', 1:'build_your_own', 2:'change_features', 3:'auto_suggestions']\n
		    """
		),
		dict(
			name='outreach_activity',
			display_name="Metamaterial Design - Outreach",
			num_demo_participants=3,
			app_sequence=['outreach_activity'],
			task_duration=180*60,
			instr_duration=5*60,
			doc=
			"""
		    	| 'task_duration': Number of seconds user spends on the task\n
		    	| 'instr_duration': Minimum number of seconds a user should reads instructions\n
		    """
		),
		dict(
			name='goal_orientation_expt',
			display_name="Metamaterial Design - Effects of Goal Orientation",
			num_demo_participants=3,
			app_sequence=['goal_orientation_expt'],
			task_duration=15*60,
			instr_duration=5*60,
			if_performance_goal=1, #[0:'learning', 1:'performance']
			if_attributes=0, #[0:'Do not show semantic attributes', 1:'Show semantic attributes']
			dse_mode=0, #[0:'all', 1:'build_your_own', 2:'change_features', 3:'auto_suggestions'],
			page_sequence=['Instructions', 'Pretest', 'Task1', 'Questionnaire1', 'Task2', 'Questionnaire2', 'Questionnaire3', 'Results'],
			doc=
			"""
		    	| 'task_duration': Number of seconds user spends on the task\n
		    	| 'instr_duration': Minimum number of seconds a user should reads instructions\n
		    	| 'performance_goal': [0:'learning', 1:'performance']\n
				| 'if_atttributes': [0:'Do not show semantic attributes', 1:'Show semantic attributes']\n
				| 'dse_mode':[0:'all', 1:'build_your_own', 2:'change_features', 3:'auto_suggestions']\n
		    """
		),
		dict(
			name='automation_expt',
			display_name="Metamaterial Design - Effects of Automation",
			num_demo_participants=3,
			app_sequence=['automation_expt'],
			task_duration=8*60,
			instr_duration=5*60,
			if_performance_goal=1, #[0:'learning', 1:'performance']
			if_attributes=1, #[0:'Do not show semantic attributes', 1:'Show semantic attributes']
			doc=
			"""
		    	| 'task_duration': Number of seconds user spends on the task\n
		    	| 'instr_duration': Minimum number of seconds a user should reads instructions\n
		    	| 'performance_goal': [0:'learning', 1:'performance']\n
				| 'if_atttributes': [0:'Do not show semantic attributes', 1:'Show semantic attributes']\n
				| 'dse_mode':[0:'all', 1:'build_your_own', 2:'change_features', 3:'auto_suggestions']\n
		    """
		)
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
		real_world_currency_per_point=1.00, participation_fee=0.00, doc=""
)

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = True

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = '_@*(t&)rk+@ak2std=cap8f$in!u$65*8hf-m7gv5cibh+#k3t'

# if an app is included in SESSION_CONFIGS, you don't need to list it here
INSTALLED_APPS = ['otree']
