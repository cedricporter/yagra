// Author: Hua Liang[Stupid ET]

$(document).ready(function () {
    $(".gravatar").click(function () {
	var new_image_id = this.id.match(/\d+/);
	$.ajax({
	    url: '/user/set_avatar',
	    data: 'new_image_id=' + new_image_id,
	    dataType: 'json',
	    type: 'post',
	    success: function (j) {
		if (j.status == 'OK') {
		    window.location.reload();
		}
		else {
		    alert('选择图片出错了！');
		}
	    }
	});
    });
});
