{
	var radius_menu = [];
	for (var i = 0; i < n_radii; i++) {
		let key = (' ' + Object.keys(radii)[i]).slice(1)
		let value = radii[key]
		radius_menu.push({
			title: key,
			action: function(d, j) {
				addEdge.call(this, d)
				changeRadius.call(this, d, width_radius_ratio*value, value)
			}
		});
	}

	// set the dimensions and margins of the graph
	var margin = {top: 10, right: 20, bottom: 30, left: 100},
	  	width = 350 - margin.left - margin.right,
	  	height = 250 - margin.top - margin.bottom;

	// append the svg object to the body of the page
	var svg = d3.select("#desCreat")
	.append("svg")
	  .attr("width", width + margin.left + margin.right)
	  .attr("height", height + margin.top + margin.bottom)
	.append("g")
	  .attr("transform",
			"translate(" + margin.left + "," + margin.top + ")");

	createForceNetwork( nodes, edges );

	function createForceNetwork(nodes, edges) {

		//create a network from an edgelist
		var force = d3.layout.force().nodes(nodes).links(edges)
		// .size([500,500])
		// .charge(-300)
		.on("tick", updateNetwork);

		var edgeEnter = svg.selectAll("g.edge")
	  	.data(edges)
	  	.enter()
	  	.append("g")
	  	.attr("class", "edge")
	  	.attr("id", function (d) {return d.id});

	  	edgeEnter
	  	.append("line")
	  	.attr("class", "highlight")
	  	.attr("x1", function (d) {return width*d.source.x})
		.attr("y1", function (d) {return height*d.source.y})
		.attr("x2", function (d) {return width*d.target.x})
		.attr("y2", function (d) {return height*d.target.y})
	  	.style("stroke-width", "14px")
	  	.style("stroke", "#66CCCC")
	  	.style("opacity", 0)
	  	.on("mouseover", edgeOver)
	  	.on("mouseout", edgeOut)
	  	.on("contextmenu", d3.contextMenu(radius_menu) )
	  	.on("click", addEdge)
	  	.on("dblclick", deleteEdge);

	  	edgeEnter
	  	.append("line")
	  	.attr("class", "link")
	  	.classed("hide", true)
	  	.attr("x1", function (d) {return width*d.source.x})
		.attr("y1", function (d) {return height*d.source.y})
		.attr("x2", function (d) {return width*d.target.x})
		.attr("y2", function (d) {return height*d.target.y})
		.attr("radius", default_radius)
	  	.style("stroke-width", (default_width)+'px')
	  	.style("stroke", "black")
	  	.style("opacity", 0.5)
	  	.style("pointer-events", "none")

		var nodeEnter = svg.selectAll("g.node")
		.data(nodes)
		.enter()
		.append("g")
		.attr("class", "node")
		.attr("id", function(d) { return d.id; })
		.attr("cx", function(d) { return width*d.x; })
		.attr("cy", function(d) { return height*d.y; })
		.attr("transform", function(d) { 
			return "translate(" + width*d.x + "," + height*d.y+ ")";
		})

		nodeEnter.append("circle")
		.attr("r", 10)
		.style("fill", "grey")
		.style("stroke", "black")
		.style("stroke-width", "1px")

		nodeEnter.append("text")
		.style("text-anchor", "middle")
		.attr("y", 3)
		.style("stroke-width", "2px")
		.style("stroke-opacity", 0.75)
		.style("stroke", "white")
		.style("font-size", "10px")
		.text(function (d) {return d.id+1})
		.style("pointer-events", "none")

		nodeEnter.append("text")
		.style("text-anchor", "middle")
		.attr("y", 3)
		.style("font-size", "10px")
		.text(function (d) {return d.id+1})
		.style("pointer-events", "none")

		force.start();
	}

	function deleteEdge(d) {
		d3.select(this.nextSibling).classed('hide', true);
	}

	function changeRadius(d, width, radius) {
		d3.select(this.nextSibling).style('stroke-width', (width)+'px');
		d3.select(this.nextSibling).attr('radius', radius);
	}

	function addEdge(d) {
		d3.select(this.nextSibling).classed('hide', false)
		changeRadius.call(this, d, default_width, default_radius)
	}

	function edgeOver(d) {
		d3.select(this).style("opacity", 0.75);
	}

	function edgeOut() {
		d3.selectAll("line.highlight").style("opacity", 0);
	}

	function updateNetwork() {}

	document.getElementById("clearAll").addEventListener("click", onclickClear, false);
	function onclickClear(){
		d3.selectAll("line.link").classed('hide', true);
	}

	var div1 = document.getElementById("all_radii")
	if (div1 != undefined ) {
		div1.addEventListener("change", onchangeChangeAllRadii, false);
	}
	function onchangeChangeAllRadii(){
		if (div1 != undefined ) {
			// Update all links
			d3.selectAll("line.highlight").each(function(d){
				changeRadius.call(this, d, width_radius_ratio*div1.value, div1.value)
			});
		}
	}

	var div2 = document.getElementById("default_radius")
	if (div2 != undefined ) {
		div2.addEventListener("change", onchangeDefaultThickness, false);
	}
	function onchangeDefaultThickness(){
		if (div2 != undefined ) {
			//change the default thickness parameter
			default_radius = div2.value
			default_width = width_radius_ratio*default_radius
		}
	}
}