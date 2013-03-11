// Author: Hua Liang[Stupid ET]

$(document).ready(function () {

    var check_button = $("#checkbutton");
    var username = $("#setusername");
    var username_status = $("#username-status");
    var email = $("#email");

    // prevent input invalid character
    username.bind('keypress', function (event) {
	var regex = new RegExp("^[a-z0-9]+$");
	var key = String.fromCharCode(!event.charCode ? event.which : event.charCode);
	if (!regex.test(key)) {
	    event.preventDefault();
	    return false;
	}
    });


    // prevent input invalid character
    email.bind('keypress', function (event) {
	var regex = new RegExp("^[a-zA-Z0-9-_.@]+$");
	var key = String.fromCharCode(!event.charCode ? event.which : event.charCode);
	if (!regex.test(key)) {
	    event.preventDefault();
	    return false;
	}
    });


    // check username
    check_button.click(function () {
	if (username.val() == "") {
	    username_status.css("display", "inline").addClass("sayno").html("<br>用户名不能为空！");
	    return;
	}

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

    // password match
    var pass1 = $("#pass1");
    var pass2 = $("#pass2");
    var pass_status = $("#password-status");

    pass2.keyup(function () {
	if (pass1.val() != pass2.val()) {
	    pass_status.css("display", "inline").css("color", "red");
	    pass_status.html("两次密码不匹配！");
	}
	else {
	    pass_status.css("display", "none");
	}
    });

    var submit_btn = $("#submit");
    submit_btn.click(function () {

	var is_failed = false;
	// username
	$.ajax({
	    url: '/ajax-validate',
	    data: 'action=check_username&username=' + username.val(),
	    dataType: 'json',
	    type: 'post',
	    async: false,
	    success: function (j) {
		username_status.removeClass("sayyes sayno");

		if (j.status == "OK") {
		    username_status.addClass("sayyes");
		}
		else {
		    is_failed = true;
		    username_status.css("display", "inline");
		    username_status.addClass("sayno");
		}
		username_status.html("<br>" + j.msg);
	    }
	});

	if (is_failed) return false;

	// email
	var email_status = $("#email-status");
	$.ajax({
	    url: '/ajax-validate',
	    data: 'action=check_email&email=' + email.val(),
	    dataType: 'json',
	    type: 'post',
	    async: false,
	    success: function (j) {
		if (j.status != "OK") {
		    email_status.css("display", "inline").css("color", "red").html(j.msg);
		    is_failed = true;
		}
	    }
	});

	if (is_failed) return false;

	if (pass1.val() != pass2.val()) return false;

	return true;
    });
});
