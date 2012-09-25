
var data = new Object();



$(document).ready(init);

function init() {
 
    $("#f_submit_btn").click(update);
    loadState();
    
   

}

function loadState(){
    data.id = $("#f_id").val();
    data.name = $("#f_name").val();
    data.type = $("#f_ftype").val();
    data.url = $("#f_url").val();
    var minutes = $("#f_utime_m").val();
    var hours = $("#f_utime_h").val();
    data.update_time = (hours*60 + minutes)*60;
    data.login = $("#f_login").val();
    data.password = $("#f_passwd").val();
    data.checked = $("#f_enable").is(':checked'); 
}

function update(){
    var id = $("#f_id").val();
    var datas = '';
    datas += ($("#f_name").val() != data.name ? "&name="+$("#f_name").val() : '' );
    datas += ($("#f_ftype").val() != data.type ? "&type="+$("#f_ftype").val() : '' );
    datas += ($("#f_url").val() != data.url ? "&url="+$("#f_url").val() : '' );
    
    var minutes = parseInt($("#f_utime_m").val());
    //alert(minutes);
    var hours = parseInt($("#f_utime_h").val());
    //alert(hours);
    var update_time = (hours*60 + minutes)*60;
    //alert(update_time);
    datas += (update_time != data.update_time ? "&utime="+update_time : '' );
    datas += ($("#f_login").val() != data.login ? "&login="+$("#f_login").val() : '' );
    datas += ($("#f_passwd").val() != data.password ? "&passwd="+$("#f_passwd").val() : '' );
    datas += ($("#f_enable").is(':checked') != data.checked ? "&enable="+ ($("#f_enable").is(':checked') ? "1" : "0") : '' );
    if (datas == ''){
        return false;
    }
    datas = "fid=" + $("#f_id").val() + datas;
    //alert(datas);
    $.ajax({
        type : "PUT",
        url : "/api/db/" + id,
        data : datas,
        success : function(data) {
            alert("Feed settings has been successfully updated.");
            return false;
        }
    });
    loadState();
    return false;
    

}