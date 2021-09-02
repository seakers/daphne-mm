	// Helper functions

// ---------------------------------------------------------------

function update_scoreboard(_scoreboard) {

	// Add the link to instructions
	const scoreboard_div = document.getElementById("ScoreboardTable");

   	_scoreboard = _scoreboard.sort((a, b) => (a.rank > b.rank) ? 1 : -1)

   	//set header of table
	let table = `
		<table class="table table-bordered table-hover table-sm" id = "myTable">
		  <thead class="thead-light">
		    <tr>
		    	<th scope="col"> Rank </th>
		      <th scope="col"> Name </th>
		      <th scope="col"> Score* </th>
		    </tr>
		  </thead>
		  <tfoot><tr><td colspan="3"> *Score is equal to the hypervolume, i.e., area enclosed by Pareto points and point [1,0] </td></tr></tfoot>
		  <tbody>
		`;
		//create//append rows
		for(i = 0; i < Math.min(_scoreboard.length,max_ranks); i++){
			row = _scoreboard[i]
			// td_color = CellColor(change,i,3)
		    table = table +
		    `<tr>
		      <td scope="row"> ${row.rank} </td>
		      <td>${row.name}</td>
		      <td>${row.score.toFixed(3)}</td>
		    </tr>`
		}
		//close off table
		table = table +
		  `</tbody>
		  </table>`;
	
	scoreboard_div.innerHTML = table;
}

// -------------------------------------------------------------------------------------

	// TRADESPACE PLOT
	function filter_points(x, th){
		if (x > th) {
			return 1 // Opacity of selected points
		} else {
			return 0.01
		}
	}

	// Hover info
	function get_hover_text (_data, is_response=false) {
		if (is_response) {
			data_str = '-new' // Response data, new
		} else {
			data_str = '-old' // Historic data, old
		}

		len = Object.keys(_data).length
		if (len === undefined || len === 0) {
			return ' '
		} else {
			var hover_text = _data.constr1.map(function(x,i){
				text = '<br>{{Constants.constraints.0}}: ' + label_constr(x.toFixed(1)) 
						+ '<br>{{Constants.constraints.1}}: ' + _data.constr2[i]
						+ '<br>Design #' + (i+1).toFixed(0) + data_str

				return text
			});
			return hover_text
		}
	}

	function pareto_response_data(_data, _response_data) {

		len = Object.keys(_response_data).length
		if (len === undefined || len === 0) {
			return {'obj1': [], 'obj2':[] }
		} else {
			var_str = 'is_pareto_response' + player_id.toFixed(0)
			obj1 = _response_data.obj1.filter((x,i) =>_response_data.is_pareto[i])
								.concat( _data.obj1.filter((x,i) => _data[var_str][i]) )
								.map(x => around(x, 3))
			obj2 = _response_data.obj2.filter((x,i) =>_response_data.is_pareto[i])
								.concat( _data.obj2.filter((x,i) => _data[var_str][i]) )
								.map(x => around(x, 3))
			
			// Sort with the first objective and with the sec ond objective
			// obj2, indeces = sortWithIndeces(obj2)
			// obj1 = indeces.map(i => obj1[i])
			// obj1, indeces = sortWithIndeces(obj1)
			// obj2 = indeces.map(i => obj2[i])
			dummy_arr = obj1.map( function (x, i) { return [x, obj2[i]] });
			dummy_arr.sort(function (a, b) {
			    return a[0] - b[0] || a[1] - b[1];
			});
			dummy = {
				'obj1': dummy_arr.map( function (x, i) { return x[0] }),
				'obj2': dummy_arr.map( function (x, i) { return x[1] })
			}
			return dummy
		}
	}

	function update_tradespace_response(_response_data) {
		// This function updates the tradespace plot upon response from the design evaluator, which a designer triggers with input
		symbols_response = Array.apply(null, new Array(n_response)).map(function(){return response_symbol;})
		sizes_response = Array.apply(null, new Array(n_response)).map(function(){return big_size;})
		var data_update = {
		    'x': [_response_data.obj1],
			'y': [_response_data.obj2],
			'text': [get_hover_text(_response_data, is_response=true)],
			'marker.size': [sizes_response],
			'marker.symbol': [symbols_response],
		};

		var layout_update = {
			'updatemenus[1].buttons[1].args': [{'marker.opacity': [ _response_data.constr1.map( x => filter_points(x, 0.9))] }, [1] ],
		}
		Plotly.update(tsViz, data_update, layout_update, [1])
	}

	function update_pareto_response(_data, _response_data) {
		pareto_data = pareto_response_data(_data, _response_data)
		var data_update = {
		    'x': [pareto_data.obj1],
			'y': [pareto_data.obj2],
		};
		Plotly.update(tsViz, data_update, {}, [3])
	}

	function change_selected_design(curveNumber, pointNumber) {
		// Highlight the selected point by increasing its size
		_sizes = [...sizes]
		_symbols = [...symbols]
		_colors = [...colors]
		symbols_response = Array.apply(null, new Array(n_response)).map(function(){return response_symbol;})
		sizes_response = Array.apply(null, new Array(n_response)).map(function(){return big_size;})
		// Change size of the selected point for the historic tradespace only
		if (curveNumber === 0){
			_data = data
			is_response = false
			_sizes[pointNumber] = select_size;
			_symbols[pointNumber] = select_symbol;
			_colors[pointNumber] = select_color
			var update0 = {
				'marker.size': [_sizes],
				'marker.symbol': [_symbols],
				'marker.color': [_colors],	
			}
			var update1 = {
				'marker.size': [sizes_response],
				'marker.symbol': [symbols_response],
			}
		}
		if (curveNumber === 1 && n_response>0){
			_data = response_data
			is_response = true
			symbols_response[pointNumber] = select_symbol
			sizes_response[pointNumber] = select_size
			var update1 = {
				'marker.size': [sizes_response],
				'marker.symbol': [symbols_response],
			}
			var update0 = {
				'marker.size': [_sizes],
				'marker.symbol': [_symbols],
				'marker.color': [_colors],	
			}	
		}
		Plotly.restyle(tsViz, update0, {}, [0]);
		Plotly.restyle(tsViz, update1, {}, [1]);

		//Automatically update the design plot using bitsting design
		x = JSON.parse(_data.design_bitstring[pointNumber])
		update_design_creation_plot(x)
		// Store which points are tested before this and change the main selected design
		x_selected.push(x)

		// Store new curve id and new point id
		selected_curve = curveNumber;
		selected_point = pointNumber;
	}

	function update_generated_point(_data, id=null) {
		if (id === null){
			id = _data.obj1.length-1
		}
		var update = {
		    x: [[_data.obj1[id]]],
			y: [[_data.obj2[id]]],
		};
		Plotly.restyle(tsViz, update, [6])
	}

// -------------------------------------------------------------------------------------
	// FEATURE PLOT
	function CellColor(value, row, index) {
		var backColor = '';

		// if (value > 0) {
		// 	backColor = "#ccffcc";
		// }
		// else if (value < 0) {
		// 	backColor = "#ffcccc";
		// } else {
		// 	backColor = "#FFFFFF";
		// }
		var perc = clamp(100*(Number(value)+1)/2,0,100);
		backColor = perc2color(perc)

		return backColor
	}

	function perc2color(perc) {
		var r, g, b = 0;
		if(perc < 50) {
			r = 255;
			g = Math.round(5.1 * perc);
		}
		else {
			g = 255;
			r = Math.round(510 - 5.10 * perc);
		}
		var h = r * 0x10000 + g * 0x100 + b * 0x1;
		return '#' + ('000000' + h.toString(16)).slice(-6);
	}

	async function update_automated_suggestions_table(names, default_values, new_values) {

		let tableData = document.getElementById("AutomatedSuggestionsTable"); 
		//set header of table
		let table = `
		<table class="table table-borderless" id = "myTable">
		  <thead>
		    <tr>
		      <th scope="col"> Name </th>
		      <th scope="col"> Selected </th>
		      <th scope="col"> Suggested (Change*) </th>
		    </tr>
		  </thead>
		  <tfoot><tr><td colspan="3">*Positive change represent an increase. </td></tr></tfoot>
		  <tbody>
		`;
		//create//append rows
		for(i = 0; i < default_values.length; i++){
			change = (new_values[i]-default_values[i]).toFixed(2)
			td_color = CellColor(change,i,3)
		    table = table +
		    `<tr>
		      <td scope="row">${names[i]}</td>
		      <td>${default_values[i].toFixed(2)}</td>
		      <td style="background-color:${td_color}">${around(new_values[i],2)} (${change})</td>
		    </tr>`
		}
		//close off table
		table = table +
		  `</tbody>
		  </table>`;

		tableData.innerHTML = table;
	} 

// -------------------------------------------------------------------------------------
	// DESIGN PLOT

	function update_design_creation_plot(x) {
		document.getElementById("clearAll").click()
		d3.selectAll('line.link').filter(function(d, i) { return Boolean(x[i])}).classed('hide', false)
	}

	// Plot from selected points
	function plot_design(curveNumber, pointNumber, heading=null) {
		image = get_image(curveNumber, pointNumber)
		annotation = get_annotation(curveNumber, pointNumber)
		update_design_visualization(image, annotation, heading)
	}

	// Restyle for new selected design
	function update_design_visualization(image, annotation, heading=null){
		image = design_grid(image)
		image = image.map( x => subtract_arr_from_1(x) )
		Plotly.restyle(desViz, 'z', [image]);
		Plotly.relayout(desViz, 'annotations', [annotation])
		update_design_visualization_heading(heading)
	}

	function update_design_visualization_heading(heading){
		heading_dom = document.getElementById("desViz").parentElement.children[0];
		if (heading.includes("generated")) {
			heading_dom.innerHTML = "Metamaterial Visualization -  Newly Generated "
		} else if (heading.includes("selected")) {
			heading_dom.innerHTML = "Metamaterial Visualization -  Selected " + big_plus
		} else if (heading.includes("tested")){
			heading_dom.innerHTML = "Metamaterial Visualization -  Newly Generated and Tested" + green_triangle
		}
	}

		// Create a 3x3 grid layout for metamaterial visualization
	function design_grid(image){
		n=-5//Must be negative smaller than equal to -1
		alpha = 0.3

		x_trim = image.slice(1,-1).map(function(el, i) {return el.slice(1,-1)})
		x_alpha = multiple_by_constant2D(x_trim, alpha)

		row1 = stitch(x_alpha, x_alpha, n, axis=1)
		row1 = stitch(row1, x_alpha, n, axis=1)

		row2 = stitch(x_alpha, x_trim, n, axis=1)
		row2 = stitch(row2, x_alpha, n, axis=1)

		row3 = stitch(x_alpha, x_alpha, n, axis=1)
		row3 = stitch(row3, x_alpha, n, axis=1)

		x_stitched = stitch(row1, row2, n, axis=0)
		x_stitched = stitch(x_stitched, row3, n, axis=0)

		return x_stitched
	}

		// Text detailing the properties of selected designs
	function get_annotation(curveNumber, pointNumber){
		if (curveNumber === 1) {
			_data = response_data
			data_str = '-new' // Response data, new
		} else {
			_data = data
			data_str = '-existing' // Historic data, old
		}
		if (pointNumber < _data.obj1.length) {
			text = 'Design #' + (pointNumber+1) + data_str + 
					'<br>{{Constants.objectives.0}}: ' + _data.obj1[pointNumber].toFixed(2) + '  {{Constants.objectives.1}}: ' + _data.obj2[pointNumber].toFixed(2) 
					+ '<br>{{Constants.constraints.0}}: ' + label_constr(_data.constr1[pointNumber].toFixed(1)) 
					+ '<br>{{Constants.constraints.1}}: ' +  _data.constr2[pointNumber]
		} else {
			text = ""
		}
		annotation = {
			xref: 'paper',
			yref: 'paper',
			x: -0.15,
			xanchor: 'left',
			y: 1.35,
			yanchor: 'top',
			text: text,
			showarrow: false,
			font: {
			  color: "black",
			  size: 16
			},
			align: 'left',
		  }
		return annotation
	}

	function get_image(curveNumber, pointNumber) {
		if (curveNumber === 1) {
			_data = response_data// Response data, new
		} else {
			_data = data // Historic data, old
		}
		return JSON.parse(_data.image[pointNumber])
	}

	function get_attributes(curveNumber, pointNumber) {
		if (curveNumber === 1) {
			_data = response_data// Response data, new
		} else {
			_data = data // Historic data, old
		}
		attribute_keys = ['attr1', 'attr2', 'attr3', 'attr4', 'attr5']
		attributes = attribute_keys.map(function(k) {
		        return _data[k][pointNumber];
		});
		return attributes
	}
