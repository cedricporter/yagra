// Author: Hua Liang[Stupid ET]

$(document).ready(function () {

    // check username
    var check_button = $("#checkbutton");
    var username = $("#setusername");
    var username_status = $("#username-status");

    // prevent input invalid character
    username.bind('keypress', function (event) {
	var regex = new RegExp("^[a-z0-9]+$");
	var key = String.fromCharCode(!event.charCode ? event.which : event.charCode);
	if (!regex.test(key)) {
	    event.preventDefault();
	    return false;
	}
    });

    check_button.click(function () {
	username_status.css("display", "inline").html("<br>检查中...");
	$.ajax({
	    url: '/ajax-validate',
	    data: 'action=check_username&username=' + username.val(),
	    dataType: 'json',
	    type: 'post',
	    success: function (j) {
		username_status.removeClass("sayyes sayno");
		if (j.status == "OK") {
		    username_status.addClass("sayyes");
		}
		else {
		    username_status.addClass("sayno");
		}
		username_status.html("<br>" + j.msg);
	    }
	});
    });


});
