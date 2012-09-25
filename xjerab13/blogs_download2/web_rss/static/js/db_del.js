$(document).ready(init);

function init() {
    $("i.del").click(del);
    $("input[name^=f_enable]").change(chckbox_change);    
     $("input[name^=f_backup]").change(chckbox_change);    
   

}

function del() {
    var row = $(this).parent().parent();
    var id = row.find("td:first").text();
    row.remove();
    //send("DELETE", null, id);
    
    $.ajax({
        type : "DELETE",
        url : "/api/db/" + id,
        data : null,
        success : function(data) {
            alert("delete ok");

        }
    });
    return false;
    
    
    
}

function chckbox_change(){
   var row = $(this).parent().parent();
   var id = row.find("td:first").text().replace(/^\s+|\s+$/g, '');
   var type = $(this).attr("name");
   
   var change = $(this).is(':checked')
   var datastring = "action=";
   if (change){
       datastring +="enable"
   }else {
       datastring += "disable"
   }
   datastring += "&f_type=" + type;

    $.ajax({
        type : "PUT",
        url : "/api/ctrl/" + id,
        data : datastring,
        success : function(data) {
            alert("change ok");

        }
    });
    return false;
    
}

