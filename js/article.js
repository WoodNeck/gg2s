//게시글 삭제버튼
function deletePrompt(){
	if (confirm("You really want to delete this article?")){
		var deleteForm = document.getElementById('delete-form');
		deleteForm.submit();
	} else {
		// DO NOTHING
	}
}

function deleteReplyPrompt(reply_index){
	if (confirm("You really want to delete this reply?")){
		var deleteForm = document.getElementById('reply-delete-form-' + reply_index.toString());
		deleteForm.submit();
	} else {
		// DO NOTHING
	}
}

//댓글 공간 생성
function makeReplyForm(index, article, target, user_id, totalReplyCounter){
	for (var i = 0; i < totalReplyCounter; i += 1) {
		replyWrapper = document.getElementById('reply-new-' + i.toString());
		replyWrapper.innerHTML = '';
	}
	
	var innerHTML = '';
	innerHTML += '<form method="POST" action="/newboardreply">';
	innerHTML += '<input type="hidden" name="article" value="' + article + '" />';
	innerHTML += '<input type="hidden" name="target" value="' + target + '" />';
	innerHTML += '<input type="hidden" name="targetuser" value="' + user_id + '" />';
	innerHTML += '<input type="hidden" name="type" value="new" />';
	innerHTML += '<div class="reply-newform-wrapper">';
	innerHTML += '<div class="reply-newtext-wrapper">';
	innerHTML += '<textarea id="reply-newreply-content" name="reply-newreply-content" placeholder="Leave a comment..." resize="none" wrap="hard"></textarea>';
	innerHTML += '</div>'; //reply-newtext-wrapper
	innerHTML += '<div class="reply-newsubmit-wrapper">';
	innerHTML += '<input type="submit" id="reply-newreply-submit" value="SUBMIT" />';
	innerHTML += '</div>'; //reply-newsubmit-wrapper
	innerHTML += '</div>'; //reply-newform-wrapper
	innerHTML += '</form>';
	
	targetWrapper = document.getElementById('reply-new-' + index.toString());
	targetWrapper.innerHTML = innerHTML;
}

//이미 삭제된 댓글에 대해 삭제버튼 없애기
function hideDeleteForm(){
			var replies = document.getElementsByClassName('reply-content');
			[].forEach.call(replies, function (reply) {
				if (reply.innerHTML.substring(0, 24) == '<div id="reply-deleted">'){
					reply.innerHTML = '<div id="reply-deleted">';
				}
			});
}