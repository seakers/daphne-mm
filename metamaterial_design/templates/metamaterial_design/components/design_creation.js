{
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
	  	.data(edges, function (d) {return d.id})
	  	.enter()
	  	.append("g")
	  	.attr("class", "edge");

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
	  	.style("stroke-width", "12px")
	  	.style("stroke", "black")
	  	.style("opacity", 0.5)
	  	.style("pointer-events", "none");
		
		
		var nodeEnter = svg.selectAll("g.node")
		.data(nodes)
		.enter()
		.append("g")
		.attr("class", "node")
		.attr("cx", function(d) { return width*d.x; })
		.attr("cy", function(d) { return height*d.y; })
		.attr("transform", function(d) { 
			return "translate(" + width*d.x + "," + height*(1-d.y)+ ")";
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
		
		function deleteEdge(d) {
			d3.select(this.nextSibling).classed('hide', true);
		}

		function addEdge(d) {
			d3.select(this.nextSibling).classed('hide', false);
		}

		function edgeOver(d) {
			d3.select(this).style("opacity", 0.75);
		}

		function edgeOut() {
			d3.selectAll("line.highlight").style("opacity", 0);
		}

		function updateNetwork() {}
	}
}