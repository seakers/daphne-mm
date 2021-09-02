
// Global variables
var data = js_vars.data; // Historic data; constant
const data_key = js_vars.data_key;
var	n_data = data.obj1.length

var feature_images = js_vars.feature_images
var feature_ind = js_vars.feature_ind

var response_data = js_vars.response_data
if (response_data === undefined || Object.keys(response_data).length === 0){
	response_data = {}
} else {
	var n_response = response_data.obj1.length
}
var player_id = {{ player.id_in_subsession }}
const goals = js_vars.goals

var nodes = js_vars.nodes;
var edges = js_vars.edges;
const num_features= {{ Constants.num_features }};
const num_ticks= {{ Constants.num_ticks }};

// Slider information
const feature_names = js_vars.feature_names;
const features_sliders_step_values = Array.apply(null, Array(num_ticks)).map(function (x, i) { return (-2.5+i*5/num_ticks); })
const eta_slider_step_values = Array.apply(null, Array(num_ticks)).map(function (x, i) { return (i*0.5/num_ticks).toFixed(2); })
const eta_n_steps = 75

var current_slider_values = new Array(num_features).fill(0);
var eta = 0;

// marker setting
var normal_color = '#585858';
	bright_color = '#00FFFF';
	dull_color = '#e6e6e6';
	select_color = 'red'
var orig_color = normal_color; //dummy variable to store color
var colors = Array.apply(null, new Array(n_data)).map(function(){return normal_color});
const big_plus = "<span style=\"color: transparent;  text-shadow: 0 0 0 red; \">&#10133;</span>"
const green_triangle = "<span style=\"color: #00FF00;  text-shadow: 0 0 0 green; \"> &#9650;</span>"

var big_size = "10";
	small_size = "6";
	select_size = "14"
var sizes = Array.apply(null, new Array(n_data)).map(function(){return small_size;})

var normal_symbol = "circle";
	select_symbol = "cross-dot";
	response_symbol = 'triangle-up';
var symbols = Array.apply(null, new Array(n_data)).map(function(){return normal_symbol;})

// Tradespace plot condifg
var tsViz_config
var target_objectives = [1, 0]

// Initialize selected point on display
var selected_curve = 0
var selected_point = 50
var selected_features;

// DOM elements
var desViz = document.getElementById('desViz');
var tsViz = document.getElementById('tsViz');
var featCreat = document.getElementById('featCreat');
var activeTaskId = "design-tab";

// Information to send back to the database
var x_selected = [data.design_bitstring[selected_point]]
var z_selected = []
var z_generated = []

//Reconstructed image shown temporarily on the screen
var recontr_image = Promise.resolve([]);

//Radius and material options
const radii = js_vars.radii;
const n_radii = Object.keys(radii).length
const materials = js_vars.materials;

//Default thickness of links
var default_radius = 0.0002 //meters
var default_width = 10
var width_radius_ratio = default_width/default_radius

// Number of top scores to show
var scoreboard = Object.values(data['scoreboard'])
const max_ranks = 5;


