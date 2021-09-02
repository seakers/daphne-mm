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
			l: 0,
			b: 0
		},
		grid: {rows: 1, columns: num_ticks, pattern: 'independent'},
	};

	let feature_template = {
			z: [],
			type: 'heatmap',
			hoverinfo:'skip',
			colorscale:'Greys',
			showscale: false,
	};

	// Add image plots to div
	layout = update_layouts(layout)
	for (let i = 0; i < n_fi_tests; i++) {
		// Add first image
		var img0 = document.getElementById("fi_test"+(i+1).toFixed(0)+"_0")
		images = images_fi_test[i]
		data = update_data(images)
		Plotly.plot(img0, data, layout, config)
	}

	function update_layouts(_layout){
		// Add axis properties
		for (let j = 2; j <= num_ticks; j++){
			eval("_layout.xaxis"+ j + "={ticks:'', showticklabels:false, showgrid: false};");
			eval("_layout.yaxis"+ j + "={ticks:'', showticklabels:false, showgrid: false};");
		}
		return _layout
	};

	function update_data(_feature_images){
		_data = []
		// Add subplot data
		for (let j = 1; j <= num_ticks; j++){
			image = JSON.parse(_feature_images[j-1])
			image = image.map( x => subtract_arr_from_1(x) )
			if (j === 1){
					id=''
				}
			else {
				id=j
			}
			let design = {
				z: image,
				type: 'heatmap',
				hoverinfo:'skip',
				colorscale:'Greys',
				showscale: false,
				xaxis: 'x'+id,
				yaxis: 'y'+id,
			};
			_data[j-1] = design
		}
		return _data
	}
}