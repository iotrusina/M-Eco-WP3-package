$(document).ready(init);

function init() {
    setTimeout(get_update,5000);
    //alert(new Date(456156168470.120));
}

function get_update() {
    $.ajax({
        dataType : "json",
        type : "get",
        url : "/api/ctrl",
        data : null
    }).done(update_table);

}

function update_table(data) {
    $("table > tbody tr").remove();
    for(a in data) {
        $("table > tbody:last").append(
            $("<tr>").append(
                $("<td>").text(data[a].name),
                 $("<td>").text(data[a].url),
                 $("<td>").text(data[a].status), 
                 $("<td>").text(data[a].next_update), 
                 $("<td>").text(data[a].last_update)
                 )
           )

    }
    setTimeout(get_update,5000);

}

function ISODateString(time) {
    var d = new Date(time);
    function pad(n) {
        return n < 10 ? '0' + n : n
    }

    return d.getUTCFullYear() + '-' + pad(d.getUTCMonth() + 1) + '-' + pad(d.getUTCDate()) + ' ' + pad(d.getUTCHours()) + ':' + pad(d.getUTCMinutes()) + ':' + pad(d.getUTCSeconds()) + 'Z'
}