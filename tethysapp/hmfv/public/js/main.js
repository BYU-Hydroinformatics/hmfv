//get cookie
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

//find if method is csrf safe
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

//add csrf token to appropriate ajax requests
$(function() {
    crossDomain: false,
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
            }
        }
    });
});

function ajax_update_database_with_file(ajax_url, ajax_data,div_id) {
    //backslash at end of url is required
    if (ajax_url.substr(-1) !== "/") {
        ajax_url = ajax_url.concat("/");
    }
    //update database
    var xhr = jQuery.ajax({
        url: ajax_url,
        type: "POST",
        data: ajax_data,
        dataType: "json",
        processData: false, // Don't process the files
        contentType: false // Set content type to false as jQuery will tell the server its a query string request
    });
    xhr.done(function(data) {
        if("success" in data){
            addSuccessMessage(data['success'],div_id);
        }else{
            appendErrorMessage(data['error'],div_id);
        }
    })
    .fail(function(xhr, status, error) {
        appendErrorMessage(xhr.responseText,div_id);
        console.log(xhr.responseText);

    });
    return xhr;
}

function addSuccessMessage(message, div_id) {
    var div_id_string = '#message';
    if (typeof div_id != 'undefined') {
        div_id_string = '#'+div_id;
    }
    $(div_id_string).html(
      '<span class="glyphicon glyphicon-ok-circle" aria-hidden="true"></span>' +
      '<span class="sr-only">Sucess:</span> ' + message
    ).removeClass('hidden')
    .removeClass('alert-danger')
    .removeClass('alert-info')
    .removeClass('alert-warning')
    .addClass('alert')
    .addClass('alert-success');
}

function appendErrorMessage(message, div_id, message_div_id) {
    var div_id_string = '';
    if (typeof div_id != 'undefined') {
        div_id_string = 'id = "'+div_id+'"';
    }
    var message_div_id_string = '#message';
    if (typeof message_div_id != 'undefined') {
        message_div_id_string = '#'+message_div_id;
    }
    $('#'+div_id).remove();
    $(message_div_id_string).append(
      '<div '+ div_id_string +' class="alert alert-danger alert-dissmissible" role="alert">' +
      '<button type="button" class="close" data-dismiss="alert" aria-label="Close">' +
      '<span aria-hidden="true">&times;</span></button>' +
      '<span class="glyphicon glyphicon-fire" aria-hidden="true"></span>' +
      '<span class="sr-only">Error:</span> ' + message + '</div>'
    )
    .removeClass('hidden');
}


function appendSuccessMessage(message, div_id) {
    var div_id_string = '';
    if (typeof div_id != 'undefined') {
        div_id_string = 'id = "'+div_id+'"';
    }
    $('#message').append(
      '<div '+ div_id_string +' class="alert alert-success" role="alert">' +
      '<br><span class="glyphicon glyphicon-ok-circle" aria-hidden="true"></span>' +
      '<span class="sr-only">Sucess:</span> ' + message + '</div>'
    )
    .removeClass('hidden');
}

//add error message to #message div
function addErrorMessage(error, div_id) {
    var div_id_string = '#message';
    if (typeof div_id != 'undefined') {
        div_id_string = '#'+div_id;
    }
    $(div_id_string).html(
      '<span class="glyphicon glyphicon-exclamation-sign" aria-hidden="true"></span>' +
      '<span class="sr-only">Error:</span> ' + error
    )
    .removeClass('hidden')
    .removeClass('alert-success')
    .removeClass('alert-info')
    .removeClass('alert-warning')
    .addClass('alert')
    .addClass('alert-danger');

}

