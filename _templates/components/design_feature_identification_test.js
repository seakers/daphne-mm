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
	for (let i = 0; i < n_dfi_tests; i++) {
		// Add the image
		var img0 = document.getElementById("dfi_test"+i.toFixed(0))
		image = JSON.parse(images_dfi_test[i])
		image = image.map( x => subtract_arr_from_1(x) )
		design = deepCopyFunction(design_template)
		design.z = image
		Plotly.plot(img0, [design], layout, config)
	}
}