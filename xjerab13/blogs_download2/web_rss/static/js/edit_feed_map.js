$(document).ready(init);

function init() {
    $(".func_type").change(onchange);
    $("#f_submit_btn").click(createxml);

}

function onchange() {
    $(this).nextAll().remove();
    var value = $(this).val();
    var str = $(this).attr("id");
    var qqs = str.split("_");
    var id = "";
    var atrid = "";
    var prefix = qqs[0];
    //alert(qqs.length)
    if(qqs.length == 4){
        id = qqs[qqs.length-1];
    }else if(qqs.length == 5){
        id = qqs[qqs.length-2];
        atrid = "_" + qqs[qqs.length-1];
    }
    //alert(id);
    //alert(atrid);
    var data;

    if(value == "buildin") {
        data = $("<select>").attr({
            "class" : "input-large",
            "id" : prefix + "_func_name_"+id + atrid
        }).append(
        $("<option>").attr("value", "getItemFromFeedItem").text("getItemFromFeedItem"), 
        $("<option>").attr("value", "getIsoDateTime").text("getIsoDateTime")).after(
            $("<strong>").text("(").after(" ").before(" "), 
            $("<input>").attr({
                "type" : "text",
                "class" : "input-large",
                "list" : "feed_data",
                "id" : prefix + "_args_" + id + atrid
        }).after(" "), $("<strong>").text(")").after(" "));

    } else if(value == "static") {
        data = $("<input>").attr({
            "type" : "text",
            "class" : "input-medium",
            "id" : prefix + "_args_" + id + atrid
        });
    } else if(value == "userfunc") {
        data = $("<textarea>").attr({
            "class" : "span8",
            "rows" : "10",
            "id" : prefix + "_func_content_" + id + atrid
        });
    }
    $(this).after(data).after(" ");

}

function createxml() {
    var optionTexts = [];
    $('form[id^="f_tagform_"]').each(function() {
        optionTexts.push($(this).attr("id"))
    });
    var root_tag = $("#f_xml_root").val();
    var cont_tag = $("#f_xml_cont").val();

   
    var funcs = new XMLWriter("UTF-8");
    funcs.formatting = "indented";
    funcs.indentChar = ' ';
    funcs.indentation = 4;

    funcs.writeStartDocument();
    funcs.writeStartElement("root");
    funcs.writeStartElement("update_feed");
    funcs.writeCDATA($("#f_update_func").val());
    funcs.writeEndElement();
    funcs.writeStartElement("func");

    for(idc in optionTexts) {
        var id = $("#" + optionTexts[idc] + " > input.form_tag_id").val()
        var enabled = $("#f_check_enabled_" + id).is(':checked');
        if (!enabled){
            continue;
        }
        var tagname = $("#tag_name_" + id).val();
        var xpath = $("#tag_xpath_" + id).val();
        var text_func_type = $("#text_func_type_" + id).val();

        //scheme.writeStartElement(tagname);
        //scheme.writeEndElement();
        funcs.writeStartElement("item");
        funcs.writeAttributeString("for", xpath);
        if(text_func_type != undefined) {
            var text_args = $("#text_args_" + id).val();
            text_args = (text_args == undefined ? "" : text_args);
            funcs.writeStartElement("text");
            funcs.writeAttributeString("functype", text_func_type);
            funcs.writeAttributeString("args", text_args);

            if(text_func_type == "buildin") {
                var text = $("#text_func_name_" + id).val();
                funcs.writeString((text == undefined ? " " : text));
            } else if(text_func_type == "static") {

            } else if(text_func_type == "userfunc") {
                var text = $("#text_func_content_" + id).val();
                
                if(text.length > 0){
                    
                funcs.writeCDATA(text);
                }

            }
            funcs.writeEndElement();
        }

        var attrs = [];
        $("#" + optionTexts[idc] + " .form_attr_id").each(function() {
            attrs.push($(this).val())
        });
        for(a in attrs) {
            var atrid = attrs[a];
            var atr_name = $("#attr_name_" + id + "_" + atrid).val();
            //alert(atr_name);
            var atr_func_type = $("#attr_func_type_" + id + "_" + atrid).val();
            var atr_func_name = $("#attr_func_name_" + id + "_" + atrid).val();
            atr_func_name = (atr_func_name == undefined ? " " : atr_func_name );
            var atr_args = $("#attr_args_" + id + "_" + atrid).val();
            atr_args = (atr_args == undefined ? "" : atr_args);

            funcs.writeStartElement("attr");
            
            funcs.writeAttributeString("name", atr_name);
            funcs.writeAttributeString("functype", atr_func_type);
            funcs.writeAttributeString("args", atr_args);
            
            if(atr_func_type == "buildin") {
                funcs.writeString($("#attr_func_name_" + id + "_" + atrid).val());
            } else if(atr_func_type == "static") {

            } else if(atr_func_type == "userfunc") {
                funcs.writeCDATA($("#attr_func_content_" + id + "_" + atrid).val());
            }

            funcs.writeEndElement();
        }

        funcs.writeEndElement();
    }
    funcs.writeEndElement();
    funcs.writeEndElement();
    funcs.writeEndDocument();
    //scheme.writeEndElement();
    //scheme.writeEndElement();
    //scheme.writeEndDocument();
    //alert(scheme.flush());
    $("#qq").empty();
    
    var feed_id = $("#feed_db_id").val();
    var tstbwndls = $("#f_testdownload").is(':checked');
    var tst = (tstbwndls == true) ? "1" : "0"
    //alert(tstbwndls);
    $.ajax({
        type : "POST",
        url : "/db/savefeed/" + feed_id + "/meco",
        data : "data="+encodeURIComponent(funcs.flush())+"&testdownload=" + tstbwndls, 
        success : function(data) {
            $("#qq").html(data);
        }
    });
    return false;
}