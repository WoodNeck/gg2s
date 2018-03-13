//variable user_url & current_season is defined in gg2stats.py

//Search
var searchWrapper = document.querySelector('.search-wrapper'),
	searchInput = document.querySelector('.search-input');

document.addEventListener('click', function (e) {
  if (~e.target.className.indexOf('search')) {
	searchWrapper.classList.add('focused');
	searchInput.focus();
  } else if (~e.target.className.indexOf('log-page')) {
	jQuery("#logs").load('/?id=' + user_url + ' #content', function(){});
  } else {
	searchWrapper.classList.remove('focused');
  }
});

//Selector
$(window).on('load', function () {
	goToFromHash('onload');
});
function changeMenu (menu)
{
	jQuery("#main-content").load('/' + menu + '?id=' + user_url + ' #content', function(){
		if (menu == 'overall') {
			jQuery("#activity-logs").load('/log?id=' + user_url + ' #log-content', function(){
				if ($(".log-next").attr("id")) {
					$("#log-right").addClass("active");
				}
			});
			jQuery("#reply-replies").load('/reply?id=' + user_url + ' #reply-content', function(){
				if ($(".reply-next").attr("id")) {
					$("#reply-right").addClass("active");
				}
			});
		}
	});
	
	var menus = [];
	menus.push(document.getElementById('menu_overall'))
	menus.push(document.getElementById('menu_match'))
	menus.push(document.getElementById('menu_stat'))
	menus.push(document.getElementById('menu_profilebackpack'))
	menus.push(document.getElementById('menu_profileloadout'))
	
	for (var i = 0; i < 5; i += 1)
	{
		menus[i].classList.remove('selected');
	}	
	
	var sel_menu = document.getElementById('menu_' + menu);
	sel_menu.classList.add('selected');
}

//Activity Change
function changeActivity(dir) {
	var cursor = $(".log-next").attr("id");
	if (dir == 0){
		var button = $("#log-left");
	}
	else if (dir == 1){
		var button = $("#log-right");
	}
	if (button.hasClass("active")){
		$("#log-left").removeClass("active");
		$("#log-right").removeClass("active");
		var logContent = $("#activity-logs");
		logContent[0].innerHTML = '<i class="ion ion-refresh proxy"></i>'
		logContent.load('/log?id=' + user_url + '&cursor=' + cursor + '&dir=' + dir + ' #log-content', setTimeout(function(){
			checkNextLog(dir);
		}, 1500));
	}
}
//Check whether there're more logs
function checkNextLog(dir) {
	if (dir == 1) {
		var nextCursor = $(".log-next").attr("id");
		if (nextCursor) {
			//Has next content
			$("#log-left").addClass("active");
			$("#log-right").addClass("active");
		} else {
			//There're no next content
			$("#log-left").addClass("active");
		}
	} else if (dir == 0) {
		var hasLeft = $(".log-left").attr("id");
		if (hasLeft == '1') {
			//Has next content
			$("#log-left").addClass("active");
			$("#log-right").addClass("active");
		} else {
			//There're no next content
			$("#log-right").addClass("active");
		}
	}
}

//Reply Change
function changeReply(dir) {
	var cursor = $(".reply-next").attr("id");
	if (dir == 0){
		var button = $("#reply-left");
	}
	else if (dir == 1){
		var button = $("#reply-right");
	}
	if (button.hasClass("active")){
		$("#reply-left").removeClass("active");
		$("#reply-right").removeClass("active");
		var replyContent = $("#reply-replies");
		replyContent[0].innerHTML = '<i class="ion ion-refresh proxy"></i>'
		replyContent.load('/reply?id=' + user_url + '&cursor=' + cursor + '&dir=' + dir + ' #reply-content', setTimeout(function(){
			checkNextReply(dir);
		}, 1500));
	}
}
//Check whether there're more replies
function checkNextReply(dir) {
	if (dir == 1) {
		var nextCursor = $(".reply-next").attr("id");
		if (nextCursor) {
			//Has next content
			$("#reply-left").addClass("active");
			$("#reply-right").addClass("active");
		} else {
			//There're no next content
			$("#reply-left").addClass("active");
		}
	} else if (dir == 0) {
		var hasLeft = $(".reply-left").attr("id");
		if (hasLeft == '1') {
			//Has next content
			$("#reply-left").addClass("active");
			$("#reply-right").addClass("active");
		} else {
			//There're no next content
			$("#reply-right").addClass("active");
		}
	}
}

//Submit Reply
function submitReply() {
	var newreply = $(".newreply-content").val();
	var submitButton = $("#reply-submit");
	
	if (newreply != '') {
		$("#reply-left").removeClass("active");
		$("#reply-right").removeClass("active");
		submitButton.removeClass("ready");
		$(".newreply-content").val("");
		var jqxhr = $.post("/newreply", {id: user_url, content: newreply}, setTimeout(function(){
			jQuery("#reply-replies").load('/reply?id=' + user_url + ' #reply-content', function(){
				if ($(".reply-next").attr("id")) {
					$("#reply-right").addClass("active");
				}
			});
		}, 1500));
	} else {
		alert('Reply form is empty!');
	}
}
function checkReplyReady() {
	var submitButton = $("#reply-submit");
	var newreply = $(".newreply-content").val();
	var replyCounter = $("#newreply-counter");
	replyCounter.html(newreply.length + '/200');
	if (newreply != '') {
		submitButton.addClass("ready");
	} else {
		submitButton.removeClass("ready");
	}
}

//Stat Selection
function changeSeason() {
	if(event.keyCode == '37'){
		selectorClickLeft();
	}
	if(event.keyCode == '39'){
		selectorClickRight();
	}
}
function selectorClickLeft() {
	var arrowLeft = $(".stat-wrapper .arrow-left");
	var arrowRight = $(".stat-wrapper .arrow-right");
	if (!arrowLeft.hasClass('dead'))
	{
		var currentTitle = $(".seasonselected");
		currentTitle.addClass("seasonright");
		currentTitle.removeClass("seasonselected");
		var currentContent = $(".contentselected");
		currentContent.addClass("contentright");
		currentContent.removeClass("contentselected");
		
		var currentId = currentTitle.attr('id').replace('title', '');
		var nextId = parseInt(currentId) - 1;
		
		var nextTitle = $("#title" + nextId.toString());
		nextTitle.addClass("seasonselected");
		nextTitle.removeClass("seasonleft");
		var nextContent = $("#content" + nextId.toString());
		nextContent.addClass("contentselected");
		nextContent.removeClass("contentleft");

		arrowRight.removeClass("dead");
		if (nextId == -1)
			arrowLeft.addClass("dead");
	}
}
function selectorClickRight() {
	var arrowLeft = $(".stat-wrapper .arrow-left");
	var arrowRight = $(".stat-wrapper .arrow-right");
	if (!arrowRight.hasClass('dead'))
	{
		var currentTitle = $(".seasonselected");
		currentTitle.addClass("seasonleft");
		currentTitle.removeClass("seasonselected");
		var currentContent = $(".contentselected");
		currentContent.addClass("contentleft");
		currentContent.removeClass("contentselected");

		var currentId = currentTitle.attr('id').replace('title', '');
		var nextId = parseInt(currentId) + 1;

		var nextTitle = $("#title" + nextId.toString());
		nextTitle.addClass("seasonselected");
		nextTitle.removeClass("seasonright");
		var nextContent = $("#content" + nextId.toString());
		nextContent.addClass("contentselected");
		nextContent.removeClass("contentright");

		arrowLeft.removeClass("dead");
		if (nextId == current_season)
			arrowRight.addClass("dead");
	}
}

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