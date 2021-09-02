{
	var config = {
			displayModeBar: false,
			staticPlot: true,
			displaylogo: false
	};

	var layout = {
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
			t: 0,
			r: 0,
			l: 50,
			b: 0
		},
	};

	let design_template = {
			z: [],
			type: 'heatmap',
			hoverinfo:'skip',
			colorscale:'Greys',
			showscale: false,
	};

	// Add image plots to div
	for (let i = 0; i < n_di_tests; i++) {
		// Add first image
		var img0 = document.getElementById("di_test"+(i+1).toFixed(0)+"_0")
		image = JSON.parse(images_di_test[i])
		image = image.map( x => subtract_arr_from_1(x) )
		design = deepCopyFunction(design_template)
		design.z = image
		Plotly.plot(img0, [design], layout, config)
	}
}