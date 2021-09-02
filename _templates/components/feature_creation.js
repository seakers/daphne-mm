// This script includes design components for feature space exploration. Particularly, On the right pancel, sliders represent default_features.
// On the left panel, there is a design visualization panel. 
// By changing slider values, one can change the feature values of the design shown on the left panel. 
// New feature values replace the default_features of the existing design. The new generated design with the changed default_features is shown on the left panel.
(async function() {

	var inticks = [];
	for (let i = 0; i < num_ticks; i++) {
		var value = features_sliders_step_values[i]
		inticks.push({ 
			value: value.toFixed(2),
			label: value.toFixed(2),
			name: '',
			method: "skip", 
			args: []
		});
	}

	// Check for formatting https://plotly.com/javascript/reference/layout/sliders/
	const slider_template = {
		pad: {l:50, r: -50},
		len: 0.71,
		steps: inticks,
		active: 5,
		x:0.1,
		y:1,
		xref: 'paper',
		xanchor: 'left',
      	yref: 'paper',
      	yanchor: 'top',
		transition:{
			duration:50,
			easing: 'linear'
		},
		currentvalue: {
			font: {color: 'black', size: 14},
			suffix: '                                                     ',
			xanchor: "right",
			offset: -15
		},
		tickcolor: 'white',
		font: {
			color: 'white'
		},
	}

	var design = {
		z: [],
		type: 'heatmap',
		hoverinfo:'skip',
		colorscale:'Greys',
		showscale: false,
		ticks:""
	};

	const annotation_template = {
		x: -0.2,
		y: 1,
		text: '',
		font: {size:14},
		showarrow: false,
		xref: 'paper',
		xanchor: 'left',
      	yref: 'paper',
      	yanchor: 'top',
      	align:"right"
	}

	var featCreat_layout = {
		width: 450,
		autoszie: true,
		xaxis: {
			ticks:"",
			showticklabels:false,
			showgrid: false,
			zeroline:false
		},
		yaxis: {
			ticks:"",
			showticklabels:false,
			showgrid: false,
			zeroline:false

		},
		margin: {
			t: 25,
			r: 0,
			pad: 10
		},
		annotations: [],
		sliders: []
	};

	config = {
		displayModeBar: false,
		staticPlot: true,
		displaylogo: false
	};

	selected_features = await get_selected_features(selected_curve, selected_point)
	current_slider_values = selected_features.filter((x,i) =>feature_ind[i])
	Plotly.newPlot(featCreat, [design], update_layouts(featCreat_layout), config);

	function update_layouts(_layout){
		// Add sliders
		for (let i = 0; i < num_features; i++) {
			slider = deepCopyFunction(slider_template);
			slider.y = Number((1-i/num_features).toFixed(2));
			slider.name = i
			slider.active = features_sliders_step_values.findIndex( (e) => e > current_slider_values[i] )
			_layout.sliders.push(slider);
		}

		// Add feature annotations
		for (let i = 0; i < num_features; i++) {
			annotation = deepCopyFunction(annotation_template)
			annotation.y = Number((1-i/num_features-0.09).toFixed(2));
			annotation.text = feature_names[i]+':'
			_layout.annotations.push(annotation);
		}

		// Add text on slider scale
		low_annot = deepCopyFunction(annotation_template)
		low_annot.x = 0.27; low_annot.y = 1.05;
		low_annot.text = '<em>Low</em>'
		_layout.annotations.push(low_annot);

		mid_annot = deepCopyFunction(annotation_template)
		mid_annot.x = 0.57; mid_annot.y = 1.05;
		mid_annot.text = '<em>Mid</em>'
		_layout.annotations.push(mid_annot);

		high_annot = deepCopyFunction(annotation_template)
		high_annot.x = 0.85; high_annot.y = 1.05;
		high_annot.text = '<em>High</em>'
		_layout.annotations.push(high_annot);

		return _layout
	};

	// Listen to generate design & test button
	// document.getElementById("testDesign").addEventListener("click", onclickGenerateDesign, false);
	// function onclickGenerateDesign(){
	// 	let sliders = document.getElementsByClassName("slider-group");
	// 	z = [];
	// 	for (let i = 0; i < sliders.length; i++) {
	// 		z.push(features_sliders_step_values[sliders[i].__data__.active])
	// 	}
	// 	send_data = {
	// 		'x': '',
	// 		'z': z,
	// 		'points_checked': points_checked,
	// 	}
	// 	liveSend(send_data)
	// }

	//Listen to reset all button
	document.getElementById("resetAll").addEventListener("click", onclickReset, false);
	async function onclickReset(){
		// All 10 features
		selected_features = await get_selected_features(selected_curve, selected_point, 'all')
		//Select five features
		let values = selected_features.filter((x,i) =>feature_ind[i])
		// Update sliders
		let update = {}
		for (let i = 0; i < num_features; i++) {
			update['sliders['+i+'].active'] = features_sliders_step_values.findIndex( (e) => e > values[i] )
		}
		current_slider_values = values
		Plotly.relayout(featCreat, update)

		// Retrieve current image data
		plot_design(selected_curve, selected_point, 'selected')
	}

	var isSliderChange = false
	// Do not evaluate drag or scrolling
	document.addEventListener('mouseup', () => {

	    if (isSliderChange) {
	      	// Store the features being generated
			// z_selected.push([...selected_features])
			z_generated.push([...new_features])
			// do other things needed
			recontr_image = design_generator.decode(new_features) 
			recontr_image.then(image => {
					design_generator.clean_and_print(image)
					// image.squeeze().array().then(x=> {
					// 	update_design_visualization(x, '')
					// 	original = get_image(selected_curve, selected_point)
					// 	image.squeeze().sub(original).mean().print()
					// })
			})
	      	isSliderChange = false
	    }
	})

	// Do things in slider change
	featCreat.on("plotly_sliderchange", function (e) {

		// Retrieve current slider data
		current_slider_values[e.slider.name] = Number(e.step.value)
		new_features = replace(selected_features, feature_ind, current_slider_values)

		isSliderChange = true

	})

})();