{
	constr1_th=0.9
	constr2_th=0.9

	//graph settings
	// var xrange = [-0.05, 0.46]
	// 	yrange = [0, 0.85]
	var button_layer_1_height = 1.2
	 	button_layer_2_height = 1.05
		button_offset_1 = 0.25
		button_offset_2 = 0.22

	function filter_points(x, th){
		if (x > th) {
			return 1 // Opacity of selected points
		} else {
			return 0.01
		}
	}

	// Plotly graphs
	var tradespace = {
		x: data.obj1,
		y: data.obj2,
		text: get_hover_text(data, is_response=false),
		colorscale: 'Hot',
		mode: 'markers',
		type: 'scatter',
		name: 'Existing designs',
		marker:{size:sizes, color: colors, symbol:symbols, opacity:1},
		hovertemplate: '{{Constants.objectives.0}}: %{x:.2f}' +
					   '<br>{{Constants.objectives.1}}: %{y:.2f}' +
					   '%{text}' + 
					   '<extra></extra>',
		showlegend: true,
	  };

	var tradespace_response = {
		x: response_data.obj1,
		y: response_data.obj2,
		text: get_hover_text(response_data, is_response=true),
		colorscale: 'Hot',
		mode: 'markers',
		type: 'scatter',
		name: 'New designs',
		marker:{size:big_size, color: 'red', symbol:response_symbol, opacity:1},
		hovertemplate: '{{Constants.objectives.0}}: %{x:.2f}' +
					   '<br>{{Constants.objectives.1}}: %{y:.2f}' +
					   '%{text}' + 
					   '<extra></extra>',
		showlegend: true,
	}

	var pareto = {
		x: data.obj1.filter((x,i) =>data.is_pareto[i]),
		y: data.obj2.filter((x,i) =>data.is_pareto[i]),
		mode: 'lines',
		name: 'Best of existing designs (Pareto*)',
		showlegend: true,
		line: {"shape": 'vh', "dash": "dashdot", "color":'blue'},
	}

	var pareto_invsible = {
		x: data.obj1.filter((x,i) =>data.is_pareto[i]),
		y: data.obj2.filter((x,i) =>data.is_pareto[i]),
		mode: 'lines',
		name: 'Best of existing designs',
		showlegend: false,
		visible: false,
		line: {"shape": 'vh', "dash": "dashdot", "color":'blue'},
	}

	_pareto_response_data = pareto_response_data(data, response_data)
	var pareto_response = {
		x: _pareto_response_data.obj1,
		y: _pareto_response_data.obj2,
		name: 'Best of existing + new designs (new Pareto*)',
		mode: 'lines',
		showlegend: true,
		line: {"shape": 'vh', "dash": "dashdot", "color":'red'},
		fill: 'tonexty',
	}

	var ref_point = {
		x: [],
		y: [],
		mode: 'markers',
		type: 'scatter',
		name: 'Target',
		marker:{size:big_size, color:'red', symbol:"circle-open-dot", opacity:1},
		visible: true,
		hoverinfo: 'skip',
		showlegend: true,
	}

	var generated_point = {
		x: [],
		y: [],
		mode: 'markers',
		type: 'scatter',
		name: 'Recently generated',
		marker:{size:big_size, color:'lime', symbol:'triangle-up', opacity:1},
		visible: true,
		hoverinfo: 'skip',
		showlegend: false,
	}

	// Filter buttons 
	var updatemenus=[
		{
			buttons: [
				{
					args: [{'marker.opacity': 1}, [0]],
					label:'All',
					method:'restyle'
				},
				{
					args: [{'marker.opacity': [ data.constr1.map( x => filter_points(x, constr1_th))] }, [0] ],
					label: 'Feasible',
					method: 'restyle'
				},
			],
			direction: 'left',
			// pad: {'r': 10, 't': 10},
			showactive: true,
			type: 'buttons',
			x: button_offset_1,
			xanchor: 'left',
			y: button_layer_1_height+0.02,
			yanchor: 'top'
		},
		{
				buttons: [
					{
						args: [{'marker.opacity': 1}, [1]],
						label:'All',
						method:'restyle'
					},
					{
						args: [{'marker.opacity': 1 }, [1] ],
						label: 'Feasible',
						method: 'restyle'
					},
				],
				direction: 'left',
				// pad: {'r': 10, 't': 10},
				showactive: true,
				type: 'buttons',
				x: button_offset_2,
				xanchor: 'left',
				y: button_layer_2_height+0.02,
				yanchor: 'top'
		}
	]

	if (Object.keys(response_data).length > 0) {
		updatemenus[1].buttons[1].args = [{'marker.opacity': [ response_data.constr1.map( x => filter_points(x, constr1_th))] }, [1] ];
	}

	var annotations = [
		{
		  	text: '   Show Existing Designs: ',
		  	x: 0,
		  	y: button_layer_1_height,
		  	xref: 'paper',
		  	yref: 'paper',
		  	align: 'left',
		  	showarrow: false,
		  	font: {size: 14},
		},
		{
		  	text: '   Show New Designs:  ',
		  	x: 0,
		  	y: button_layer_2_height,
		  	xref: 'paper',
		  	yref: 'paper',
		  	align: 'left',
		  	showarrow: false,
		  	font: {size: 14},
		}
	]

	var tsViz_layout = {
		hovermode:'closest',
		updatemenus: updatemenus,
		annotations: annotations,
		xaxis: {
		   title: goals[0] + " " + "{{Constants.objectives.0}}" + "<br> <span style='font-size: 12px;'>*Only feasible metamaterials are part of Pareto front </span>",
		   dtick: 0.05,
		   showgrid: true
		},
		yaxis: {
		   title: goals[1] + " " +"{{Constants.objectives.1}}",
		   dtick: 0.05,
		   showgrid: true
		},
		margin: {
		   t:10,
		   r:10,
		   pad: 4
		},
		showlegend: true,
		legend: {
		   x: 1.1,
		   xanchor: 'right',
		   yanchor: 'top',
		   y: 1.2
		}
	};

	// Plot config of tradespace plot
	tsViz_config = tsViz_config || {displayModeBar: true, displaylogo: false, modeBarButtonsToRemove: ['toImage', 'select2d', 'lasso2d']}

	//div
	Plotly.newPlot(tsViz, [tradespace, tradespace_response, pareto_invsible, pareto_response, pareto, ref_point, generated_point], tsViz_layout, tsViz_config)
	// .then(attach);

	function attach() {
	 	var xaxis = tsViz._fullLayout.xaxis;
	  	var yaxis = tsViz._fullLayout.yaxis;
	  	var margin = tsViz._fullLayout.margin;
	  	var offsets = tsViz.getBoundingClientRect();

	  	//Calculate linear function to convert x coord
	  	var xy1 = tsViz.layout.xaxis.range[0];
	  	var xy2 = tsViz.layout.xaxis.range[1];
	  	var xx1 = offsets.left + margin.l;
	  	var xx2 = offsets.left + tsViz.offsetWidth - margin.l - margin.r;
	  	var mx = (xy2 - xy1) / (xx2 - xx1);
	  	var cx = -(mx * xx1) + xy1;
	  
	  	//Calculate linear function to convert y coord
	  	var yy1 = tsViz.layout.yaxis.range[0];
	  	var yy2 = tsViz.layout.yaxis.range[1];
	  	var yx1 = offsets.top + tsViz.offsetHeight - margin.b;
	  	var yx2 = offsets.top + margin.t + margin.b;

	  	var my = (yy2 -yy1) / (yx2 - yx1);
	  	var cy = -(my * yx1) + yy1;
	  
		tsViz.addEventListener('click', function(evt) {
	        var xInDataCoord = clamp( mx*evt.x + cx, xy1, xy2);
	        var yInDataCoord = clamp( my*evt.y + cy, yy1, yy2);
	        var update = {'x': [[xInDataCoord]], 'y': [[yInDataCoord]]}
	        if (activeTabId === "generator-tab") {
	    		Plotly.update(tsViz, update, {}, [5]);
	    		ref_point = [xInDataCoord, yInDataCoord]
	        }
	   });
	}
	dragLayer = document.getElementsByClassName('nsewdrag')[0]
	setTimeout(function(){ ifTargetSelect=false; }, 10000);

	// Hover events
	tsViz.on('plotly_hover', function(d){
		dragLayer.style.cursor = 'pointer'
		
		pt_number = d.points[0].pointNumber;
		curveNumber = d.points[0].curveNumber;
		
		if (curveNumber === 0) {
			_colors = d.points[0].data.marker.color;
			_colors[pt_number] = bright_color;
			
			var update = {
				'marker.color': [_colors]
			}
			Plotly.update(tsViz, update, {}, [curveNumber]);
		}
	})
	.on('plotly_unhover', function(d){
		dragLayer.style.cursor = ''
		
		pt_number = d.points[0].pointNumber;
		curveNumber = d.points[0].curveNumber;
		
		if (curveNumber === 0 || curveNumber === 1) {
			_colors = d.points[0].data.marker.color;
			_colors[pt_number] = normal_color;
			if (selected_curve === 0) {
				_colors[selected_point] = select_color;
			}
			
			var update = {
				'marker.color': [_colors]
			}
			Plotly.update(tsViz, update, {}, [curveNumber]);
		}
	});

	// Onclick events
	tsViz.on('plotly_click', function(d){

		// Collect identity of the selected point
		pointNumber = d.points[0].pointNumber; // New design id
		curveNumber = d.points[0].curveNumber;

		change_selected_design(curveNumber, pointNumber)

		if ("{{ Constants.name_in_url }}" === "main" ||  "{{ Constants.name_in_url }}" === "automation_expt"){
			//Reset the feature exploration tabs
			document.getElementById("resetAll").click();
			document.getElementById("resetEta").click();
		}

		// Update design plot
		plot_design(curveNumber, pointNumber, 'selected')

	});
}