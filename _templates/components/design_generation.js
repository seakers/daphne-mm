// This script includes design components for feature space exploration. Particularly, On the right pancel, sliders represent features.
// On the left panel, there is a design visualization panel. 
// By changing slider values, one can change the feature values of the design shown on the left panel. 
// New feature values are added to the features of the existing design. The new generated design with the changed features is shown on the left panel.

(async function() {

	var inticks = [];
	for (let i = 0; i < num_ticks; i++) {
		var value = eta_slider_step_values[i]
		inticks.push({ 
			value: value,
			label: value,
			name: '',
			method: 'skip', 
			args: []
		});
	}

	// Check for formatting https://plotly.com/javascript/reference/layout/sliders/
	const slider_template = {
		pad: {l:50, r: -50},
		len: 0.75,
		steps: inticks,
		active: 0,
		x:0.12,
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
			suffix: '                                                         ',
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
		visible: false,
		ticks:""
	};

	const annotation_template = {
		x: -0.18,
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

	var desGen_layout = {
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
	let values = selected_features.filter((x,i) =>feature_ind[i])
	update_automated_suggestions_table(feature_names,values,values)

	Plotly.newPlot(desGen, [design], update_layouts(desGen_layout), config);

	function update_layouts(_layout){
		// Add sliders
		n_sliders = 1
		slider_names = ['Overall Change']
		for (let i = 0; i < n_sliders; i++) {
			slider = deepCopyFunction(slider_template);
			slider.y = Number((1-i/n_sliders-0.05).toFixed(2));
			//Create update upon slider event
			var slider_update = {};
			_layout.sliders.push(slider);
		}

		// Add feature annotations
		for (let i = 0; i < n_sliders; i++) {
			annotation = deepCopyFunction(annotation_template)
			annotation.y = Number((1-i/n_sliders-10).toFixed(2));
			annotation.text = slider_names[i]+':'
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

	//;isten to reset all button
	document.getElementById("resetEta").addEventListener("click", onclickResetEta, false);
	async function onclickResetEta(){
		// All 10 features
		selected_features = await get_selected_features(selected_curve, selected_point, 'all')
		//Select five features
		let values = selected_features.filter((x,i) =>feature_ind[i])

		// Update sliders
		let update = {'sliders[0].active': 0}
		eta = 0
		Plotly.relayout(desGen, update)
		// find default/selected features
		// Show new features
		update_automated_suggestions_table(feature_names, values, values)
		// Retrieve current image data
		plot_design(selected_curve, selected_point, 'selected')
	}

	var isSliderChange = false
	// Do not evaluate drag or scrolling
	document.addEventListener('mouseup', () => {

	    if (isSliderChange) {
	    	// Retrieve current image data and its features
			image = get_image(selected_curve, selected_point)
			attributes = get_attributes(selected_curve, selected_point)

			ref_point = target_objectives.concat([1.])
			//Select five features
			let values = selected_features.filter((x,i)=>feature_ind[i])
			// find new features
			new_features = design_generator.feature_suggestions(image, attributes, eta, eta_n_steps, ref_point)

			// Do other stuff
			new_features = new_features.then(arr => {
				
				recontr_image = design_generator.decode(arr)
				recontr_image.then(image => {
					design_generator.clean_and_print(image)
				})

				//Convert into JS variable
				arr = arr.squeeze().dataSync()
				arr.map(x=>{return around(x,2)})

				// Store the features being generated
				// z_selected.push([...selected_features])
				z_generated.push([...arr])

				//Select 5 features
				let new_values = arr.filter((x,i)=>feature_ind[i])

				// Show new features
				update_automated_suggestions_table(feature_names, values, new_values)
			})

			isSliderChange=false
	    }

	})

		// Do things in slider change
	desGen.on("plotly_sliderchange", function (e) {
		
		eta = Number(e.step.value)

		isSliderChange = true
		
	})

})();