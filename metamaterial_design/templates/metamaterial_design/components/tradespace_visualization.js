{
	N = data.constr2.length
	constr1_th=0.9
	constr2_th=0.9

	//graph settings
	var x_range = [-0.8, 0.4]
		y_range = [-0.1, 1]
	var button_layer_1_height = 1.2
	 	button_layer_2_height = 1.05
		button_offset_1 = 0.22
		button_offset_2 = 0.18

	// marker setting
	var normal_color = '#585858';
		bright_color = '#00FFFF';
		dull_color = '#e6e6e6';
	var orig_color = normal_color; //dummy variable to store color
	var colors = Array.apply(null, new Array(N)).map(function(){return normal_color});

	// Hover info
	var hover_text = data.constr1.map(function(x,i){
		return '<br>Feasibility: ' + x.toFixed(1) + '<br>Stability: ' +  data.constr2[i].toFixed(1)
	});

	function filter_points(x, th){
		if (x > th) {
			return normal_color
		} else {
			return dull_color
		}
	}
	var big_size= "6";
		small_size = "6";
	var sizes = Array.apply(null, new Array(N)).map(function(){return small_size;})
	
	// Plotly graphs
	var tradespace = {
		x: data.obj1,
		y: data.obj2,
		text: hover_text,
		colorscale: 'Hot',
		mode: 'markers',
		type: 'scatter',
		marker:{size:sizes, color: colors, opacity:1},
		hovertemplate: 'Stiffness: %{x:.2f}' +
					   '<br>Target Ratio: %{y:.2f}' +
					   '%{text}' + 
					   '<extra></extra>',
		showlegend: false,
	  };

	var pareto = {
		x: data.obj1.filter((x,i) =>data.is_pareto[i]),
		y: data.obj2.filter((x,i) =>data.is_pareto[i]),
		mode: 'lines',
		showlegend: false,
		line: {"shape": 'vh', "dash": "dashdot"},
	}

	// Filter buttons 
	var updatemenus=[
		{
			buttons: [
				{
					args: ['marker.opacity', 1 ],
					label:'None',
					method:'restyle'
				},
				{
					args: ['marker.opacity', [data.constr1]],
					label: 'Feasibility',
					method: 'restyle'
				},
				{
					args: ['marker.opacity', [data.constr2]],
					label:'Stability',
					method:'restyle'
				}
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
					args: ['marker.color', [colors]],
					label:'None',
					method:'restyle'
				},
				{
					args: ['marker.color', [ data.constr1.map( x => filter_points(x, constr1_th)) ]],
					label: 'Feasibility>'+constr1_th,
					method: 'restyle'
				},
				{
					args: ['marker.color', [ data.constr2.map(  x => filter_points(x, constr2_th)) ]],
					label:'Stability>'+constr2_th,
					method:'restyle'
				},
				{
					args: ['marker.color', [ data.constr2.map(  (x,i) => filter_points( (x>constr2_th && data.constr1[i]> constr1_th) ? 1 : -1,  0)) ]],
					label:'Both',
					method:'restyle'
				}
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

	var annotations = [
		{
		  	text: 'Colorscale by Constraint:',
		  	x: 0,
		  	y: button_layer_1_height,
		  	xref: 'paper',
		  	yref: 'paper',
		  	align: 'left',
		  	showarrow: false,
		  	font: {size: 14},
		},
		{
		  	text: 'Filter by Constraint:',
		  	x: 0,
		  	y: button_layer_2_height,
		  	xref: 'paper',
		  	yref: 'paper',
		  	align: 'left',
		  	showarrow: false,
		  	font: {size: 14},
		},
	]

	var tsViz_layout = {
		hovermode:'closest',
		updatemenus: updatemenus,
		annotations: annotations,
		xaxis: {
		   title: "Stiffness",
		   // range: x_range,
		   showgrid: true
		},
		yaxis: {
		   title: "Target Ratio",
		   // range: y_range,
		   showgrid: true
		},
		margin: {
		   t: 10,
		   r:10,
		   pad: 4
		},
	};

	//div
	Plotly.newPlot(tsViz, [pareto, tradespace], tsViz_layout, {displayModeBar: true, displaylogo: false});
	dragLayer = document.getElementsByClassName('nsewdrag')[0]

	// Hover events
	tsViz.on('plotly_hover', function(data){
		dragLayer.style.cursor = 'pointer'
		
		pt_number = data.points[0].pointNumber;
		
		_colors = data.points[0].data.marker.color;
		orig_color = _colors[pt_number]
		_colors[pt_number] = bright_color;
		
		_sizes = data.points[0].data.marker.size;
		_sizes[pt_number] = big_size;

		Plotly.restyle(tsViz, 'marker.color', [_colors], 'marker.size', [_sizes]);
	})
	.on('plotly_unhover', function(data){
		dragLayer.style.cursor = ''
		
		pt_number = data.points[0].pointNumber;
		
		_colors = data.points[0].data.marker.color;
		_colors[pt_number] = orig_color;
		
		_sizes = data.points[0].data.marker.size;
		_sizes[pt_number] = small_size;
		Plotly.restyle(tsViz, 'marker.color', [_colors], 'marker.size', [_sizes]);
	});

}