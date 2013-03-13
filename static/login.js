// Author: Hua Liang[Stupid ET]

$(document).ready(function () {

    var submit_btn = $("#submit");
    var password = $("#password");
    var username = $("#username");
    var username_status = $("#username-status");
    var password_status = $("#password-status");

    submit_btn.click(function () {

	if (username.val() == "") {
	    username_status.css("display", "inline").css("color", "red").html("请输入用户名！");
	    return false;
	}
	else {
	    username_status.css("display", "none");
	}


	if (password.val() == "") {
	    password_status.css("display", "inline").css("color", "red").html("请输入密码！");
	    return false;
	}
	else {
	    password_status.css("display", "none");
	}

	return true;
    });
});
