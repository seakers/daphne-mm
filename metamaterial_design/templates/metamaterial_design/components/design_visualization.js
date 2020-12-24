{	
	let i = 0
	image = JSON.parse(data.img[i])
	image = image.map( x => subtract_arr_from_1(x) )

	var design = {
		z: image,
		type: 'heatmap',
		hoverinfo:'skip',
		colorscale:'Greys',
		showscale: false,
		ticks:""
	};

	var desViz_layout = {
		xaxis: {
			ticks:"",
			showticklabels:false,
			showgrid: false
		},
		yaxis: {
			ticks:"",
			showticklabels:false,
			showgrid: false
		},
		margin: {
			t: 25,
			r: 5,
			pad: 10
		},
		annotations: [{
			xref: 'paper',
			yref: 'paper',
			x: 0.95,
			xanchor: 'right',
			y: -0.25,
			yanchor: 'bottom',
			text: 	'Design #' + i + 
					'<br>Stiffness: ' + data.obj1[i].toFixed(1) + '  Target Ratio: ' + data.obj1[i].toFixed(1) +
					'<br>Feasibility: ' + data.constr1[i].toFixed(1) + '  Stability: ' +  data.constr2[i].toFixed(1),
			showarrow: false,
			font: {
			  color: "black",
			  size: 16
			},
			align: 'left',
		  }]
	};

	//div
	config = {
	    displayModeBar: false,
	    staticPlot: true
	}
	Plotly.newPlot(desViz, [design], desViz_layout, config);
}