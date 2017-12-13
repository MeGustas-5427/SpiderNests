$(document).ready(function() {
    $("#login_button").click(function() {
        $.ajax({
            url: "./apis/Login?password=" + $("#password").val(),
            type: 'GET',
            dataType: 'json',
            timeout: 1000,
            cache: false,
            success: function(result) {
                if (result["errcode"] != 0) {
                    $("#warnning").show();
                    $("#error_info").text(result["msg"]);
                }else{
                    localStorage["token"] = result["token"];
                    $(location).attr('href', './admin/');
                }
            }
        })
    });
    $(document).keyup(function(event) {
        if (event.keyCode == 13) {
            $("#login_button").trigger("click");
        }
    });

    if (localStorage["token"] != "") {
        $(location).attr('href', './admin/');
    }
});
