var linkRequest;
var aRequest;
 
$(document).ready(function(){
    $("input[type*=submit]").click(getAnalyze);
  
});

function getAnalyze(){
    
    if(linkRequest !=undefined){
      linkRequest.abort();
    }
    if(aRequest !=undefined){
      aRequest.abort();
    }
        
    var parseurl = $("input[name*=url]").val();
    linkRequest = $.getJSON('analyzeUrl?url='+parseurl+"&rtype=lnk", parseLinkLinks); 
    aRequest = $.getJSON('analyzeUrl?url='+parseurl+"&rtype=a", parseALinks);
    $("#output_block").css("visibility","visible");
    $("table").css("visibility","hidden");
    $("table").find("tr").remove();
    $(".main_loader").css("display","block");
    return false;
}
   
function parseLinkLinks(data){
    storeData(data,"t_lnk","1");
    
}

function parseALinks(data){
    storeData(data,"t_a","2");
    }


function storeData(data, container, loader){
    var value = $('#r'+loader+' > h2').text();
    if (data.length == 0){ 
        value = value.replace(/searching/g,"not found");

    } else 
    {
    value = value.replace(/searching/g,"found");
    for (row in data){
         $('#'+container+ ' > tbody:last').append(
         $('<tr>').append($('<td>').text(data[row].text),
                          $('<td>').text(data[row].type),
                          $('<td>').text(data[row].url),
                          $('<td>').append(
                              $("<button>").attr("type","submit").attr("class","btn").text("add").click(sendfeed)
                          )
                      )
                  );
    }
    $('#'+container).css("visibility","visible");
    }
    $('#l'+loader).css("display","none");
    $('#r'+loader+' > h2').text(value);   
}

function sendfeed(){
  $(this).off('click').attr("disabled","true");
  
  var name = $(this).parent().parent().find("td").eq(0).html();
  var type = $(this).parent().parent().find("td").eq(1).html();
  var url = $(this).parent().parent().find("td").eq(2).html();
  var datastring = "name="+name+"&type="+type+"&url="+url;
  //alert(datastring);
    
$.ajax({
  type: "POST",
  url: "/api/rest",
  data: datastring
}).done(function( msg ) {
  var parent = $("button[disabled*=disabled]").parent();
  $("button[disabled*=disabled]").remove();
  parent.append($("<i>").attr("class","icon-check"));
});
}
