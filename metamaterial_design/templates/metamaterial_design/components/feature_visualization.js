{
	let featViz_data = [];

	var inticks = [];
	for (let i = 0; i < num_ticks; i++) {
		var value = -0.3+i*0.05
		value = value.toFixed(2)
		inticks.push({ 
			value: value,
			label: value,
			method: 'restyle', 
			args: ['line.color', 'green']
		});
	}

	const slider_template = {
		pad: {l:0, t: 0},
		len: 0.15,
		steps: inticks,
		active: 6,
		x:-0.2,
		y:1,
		transition:{
			duration:50,
			easing: 'linear'
		},
		currentvalue: {
			font: {color: 'black'},
			prefix: '			  ',
			xanchor: "middle",
			offset: -15
		},
		tickcolor: 'white',
		font: {
			color: 'white'
		},
	}

	let featViz_layout = {
		grid: {rows: num_features, columns: num_ticks, pattern: 'independent'},
		showlegend:false,
		sliders: []
	};

	config = {
		displayModeBar: false,
		staticPlot: true,
		displaylogo: false
	};

	Plotly.newPlot(featViz, update_data(featViz_data), update_layouts(featViz_layout), config);

	function update_layouts(_layout){
		// Add axis properties
		for (var i = 0; i < num_features; i++) {
			for (var j = 0; j < num_ticks; j++){
				var id = i*num_features+j+1;
				eval("_layout.xaxis"+ id + "={ticks:'', showticklabels:false, showgrid: false};");
				eval("_layout.yaxis"+ id + "={ticks:'', showticklabels:false, showgrid: false};");
			}
		}

		// Add sliders
		for (var i = 0; i < num_features; i++) {
			slider = Object.assign({}, slider_template);
			slider.y = 1-i/num_features
			_layout.sliders.push(slider)
		}

		return _layout
	};

	function update_data(_data){
		// Add subplot data
		for (var i = 0; i < num_features; i++) {
			for (var j = 0; j < num_ticks; j++){
				var id = i*num_features+j+1;
				image = JSON.parse(data.img[id-1])
				image = image.map( x => subtract_arr_from_1(x) )
				var design = {
					z: image,
					type: 'heatmap',
					hoverinfo:'skip',
					colorscale:'Greys',
					showscale: false,
					xaxis: 'x'+id,
					yaxis: 'y'+id,
				};
				_data[id-1] = design
			}
		}
		return _data
	}

}