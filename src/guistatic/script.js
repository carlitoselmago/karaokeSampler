$( document ).ready(function() {
 	loadKarSongs();
 	loadSamplers();

 	$('#songlist').on('click', '.song', function(){
    	var songName=$(this).text();
    	var fileName=songName+".kar";
    	$("#selsong").text(songName);
    	$("#selsong").attr("filename",fileName);
	});

	$('#samplerlist').on('click', '.sampler', function(){
    	var samplerName=$(this).text();
    	var style=$(this).attr("style");
    	$("#selsampler").text( samplerName);
    	$("#selsampler").attr("samplerName",samplerName);
    	$("#selsampler").attr("style",style);
	});

	//controls
	$('#controls').on('click', '#loadsong', function(){
		var filename=$("#selsong").attr("filename");
		var samplerName=$("#selsampler").attr("samplerName");
		var arrayJson= JSON.stringify({"filename":filename,"samplerName":samplerName});
		$.ajax({
		    type: 'POST',
		    url: 'loadsong',
		    data: arrayJson, // or JSON.stringify ({name: 'jonas'}),
		    success: function(data) { alert('data: ' + data); },
		    contentType: "application/json",
		    dataType: 'json'
		});
	});
});


function loadKarSongs(){
	   $.getJSON( "getkarsongs", function( data ) {
  var items = [];
  $.each( data, function( key, val ) {
    items.push( "<li class='song' id='" + key + "'>" + val + "</li>" );
  });
 
  $( "<ul/>", {
    "class": "my-new-list",
    html: items.join( "" )
  }).appendTo( "#songlist" );
});
}

function loadSamplers(){
	$.getJSON( "getsamplers", function( data ) {
  	var items = [];
  	$.each( data, function( key, val ) {
  		
  		var vals=val.toString().split(",");
  		//samplerImage=data[1];
  		var image=vals[1].replace("\\", "/");
    	items.push( "<div id='" + vals[0] + "' class='sampler' style='background-image:url("+image+")'>" + vals[0] + "</div>" );
  	});
 	
  	$("#samplerlist").append(items.join( "" ));
 });
 

}
