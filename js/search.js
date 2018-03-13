document.addEventListener("keydown", function(e) {
    if (!e) { var e = window.event; }
    // Enter is pressed
    if (e.keyCode == 13) {
		submitInput();
	}
}, false);

function submitInput() {
	var searchInput = $("#search-input").val();
	searchInput = searchInput.replace(/ /g, "%20");
	$("#search-result").load('/searchresult?id=' + searchInput + ' #result-content', setTimeout(function(){}, 1500));
}