	// Use liveRecv to receive data from python
	function liveRecv(input) {

		if (input['message']=='clean image') {
				
			update_design_visualization(input['image'], '', 'generated')

		} else if (input['message']=='test design') {
			// Store response data from all previous rounds
			response_data = input['response_data']
			n_response = response_data.obj1.length
			data['is_pareto_response' + player_id.toFixed(0)] = input['is_pareto_response']  // New pareto information for historic data
				
			// Update plots in the tradespace
			update_tradespace_response(response_data)
			update_pareto_response(data, response_data)
			update_generated_point(response_data, response_data.obj1.length-1)

			// Update design visualization
			plot_design(1, response_data.obj1.length-1, 'tested')

			//Reset database variables
			x_selected = []
			z_selected = []
			z_generated = []

			if ("{{ Constants.name_in_url }}" === "outreach_activity") {
				scoreboard = Object.values(input['scoreboard'])
				update_scoreboard(scoreboard)
			}
		}

	}