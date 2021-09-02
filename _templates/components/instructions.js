{
	// Instructions handling
	var instr = document.getElementById("instructions");
	instr.style.display = "none"
	var show_btn = document.getElementById("showInstructions");
	show_btn.addEventListener("click", onclickShow, false);
	function onclickShow(){
		if (show_btn.innerHTML === "Show") {
			instr.style.display = "block"
			show_btn.innerHTML = "Hide" 
		} else {
			instr.style.display = "none"
			show_btn.innerHTML = "Show" 
		}
	}
}