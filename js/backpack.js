//Backpack Selection
function changeBackpackPage(page) {
	if (page > 0) {
		var currentBackpackPage = $(".backpack-visible");
		currentBackpackPage.addClass("backpack-invisible");
		currentBackpackPage.removeClass("backpack-visible");
		var currentSelector = $("#selector-" + currentBackpackPage.attr('id').replace('backpack-', ''));
		currentSelector.removeClass("selected");
		
		var newBackpackPage = $("#backpack-" + page.toString());
		newBackpackPage.addClass("backpack-visible");
		newBackpackPage.removeClass("backpack-invisible");
		var newSelector = $("#selector-" + page.toString());
		newSelector.addClass("selected");
	}
}