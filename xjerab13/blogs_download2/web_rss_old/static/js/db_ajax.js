$(document).ready(init);

function init() {
    $("i.del").click(del);
    $("i.edit").click(edit);

}

function del() {
    var row = $(this).parent().parent();
    var id = row.find("td:first").text();
    row.remove();
    send("DELETE", null, id);
}

function edit() {
    alert("not implemented yet :(");
}

function send(method, data, id) {

    $.ajax({
        type : method,
        url : "/api/rest/" + id,
        data : data,
        success : function(data) {
            //alert("ok");

        }
    });
    return false;

}