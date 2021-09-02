
{
	var max_ranks = 5;

	// Add the link to instructions
	const scoreboard_div = document.getElementById("ScoreboardTable");

   	var scoreboard = Object.values(data['scoreboard'])
   	scoreboard = scoreboard.sort((a, b) => (a.rank > b.rank) ? 1 : -1)

   	//set header of table
	let table = `
		<table class="table table-bordered table-hover table-sm" id = "myTable">
		  <thead class="thead-light">
		    <tr>
		    	<th scope="col"> Rank </th>
		      <th scope="col"> Name </th>
		      <th scope="col"> Score* </th>
		    </tr>
		  </thead>
		  <tfoot><tr><td colspan="3"> *Score is equal to the distance to utopia point ([1,0]) averaged over your Pareto points </td></tr></tfoot>
		  <tbody>
		`;
		//create//append rows
		for(i = 0; i < Math.min(scoreboard.length,max_ranks); i++){
			row = scoreboard[i]
			// td_color = CellColor(change,i,3)
		    table = table +
		    `<tr>
		      <td scope="row"> ${row.rank} </td>
		      <td>${row.name}</td>
		      <td>${row.score}</td>
		    </tr>`
		}
		//close off table
		table = table +
		  `</tbody>
		  </table>`;
	
	scoreboard_div.innerHTML = table;

}