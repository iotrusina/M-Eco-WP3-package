var linkRequest;
var aRequest;

$(document).ready(function() {
    $("#analyze_submit_btn").click(getAnalyze);
    $("#f_close_btn").click(function() {
        $(".float_container").css("display", "none");
        $("button[disabled*=disabled]").removeAttr("disabled");
        return false;
    });
    $("#f_submit_btn").click(sendfeed);
});
function getAnalyze() {

    if(linkRequest != undefined) {
        linkRequest.abort();
    }
    if(aRequest != undefined) {
        aRequest.abort();
    }

    var parseurl = $("input[name*=url]").val();
    linkRequest = $.getJSON('analyzeUrl?url=' + parseurl + "&rtype=lnk", parseLinkLinks);
    aRequest = $.getJSON('analyzeUrl?url=' + parseurl + "&rtype=a", parseALinks);
    $("#output_block").css("visibility", "visible");
    $("table").css("visibility", "hidden");
    $("table > tbody").find("tr").remove();
    $(".main_loader").css("display", "block");
    return false;
}

function parseLinkLinks(data) {
    storeData(data, "t_lnk", "1");

}

function parseALinks(data) {
    storeData(data, "t_a", "2");
}

function storeData(data, container, loader) {
    var value = $('#r' + loader + ' > h2').text();
    if(data.length == 0) {
        value = value.replace(/searching/g, "not found");

    } else {
        value = value.replace(/searching/g, "found");
        for(row in data) {
            $('#' + container + ' > tbody:last').append($('<tr>').append($('<td>').text(data[row].text), $('<td>').text(data[row].type), $('<td>').text(data[row].url), $('<td>').append($("<button>").attr("type", "submit").attr("class", "btn").text("add").click(show_form))));
        }
        $('#' + container).css("visibility", "visible");
    }
    $('#l' + loader).css("display", "none");
    $('#r' + loader + ' > h2').text(value);
}

function show_form() {
    var name = $(this).parent().parent().find("td").eq(0).html();
    var type = $(this).parent().parent().find("td").eq(1).html();
    var url = $(this).parent().parent().find("td").eq(2).html();
    $(this).attr("disabled", "true");
    $("#f_name").attr("value", name);
    $("#f_ftype").attr("value", type);
    $("#f_url").attr("value", url);
    $("#f_utime_h").attr("value", "1");
    $("#f_utime_m").attr("value", "00");
    $("#f_login").val('');
    $("#f_passwd").val('');
    $(".float_container").css("display", "block");

    return false;
}

function sendfeed() {

    var name = $("#f_name").val();
    var type = $("#f_ftype").val();
    var url = $("#f_url").val();
    var update_time = $("#f_utime_h").val()*60 + $("#f_utime_m").val()*1;
    var login = $("#f_login").val();
    var password = $("#f_passwd").val();
    //var enable = $("#f_enable").is(':checked');
     
    var datastring = "name=" + name + "&type=" + type + "&url=" + url+ "&utime=" +update_time*60;
    
    if(login != '' && password != ''){
        datastring += "&login=" +login+ "&passwd=" +password;
    }
    /*
    if(enable){
        datastring += "&enable=" +"1";
    }else{
        datastring += "&enable=" +"0";
    }*/
    
    //alert(datastring);
    //return false;
   
    $.ajax({
        type : "POST",
        url : "/api/db",
        data : datastring
    }).done(function(msg) {
        var parent = $("button[disabled*=disabled]").parent();
        $("button[disabled*=disabled]").remove();
        parent.append($("<i>").attr("class", "icon-check"));
        $(".float_container").css("display", "none");
    });
    
     return false;
}