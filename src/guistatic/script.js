$( document ).ready(function() {
 	loadKarSongs();
 	loadSamplers();

 	$('#songlist').on('click', '.song', function(){
    	var songName=$(this).text();
    	var songPath=$(this).attr("path");
    	var fileName=songName+".kar";
    	$("#selsong").text(songName);
    	$("#selsong").attr("path",songPath);
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

		if ($("#customtext").val()==""){
			alert("You must fill custom text for singer");
		} else {
			waitForSongLoaded();
		var customtext=$("#customtext").val();
		$("#status").text("LOADING...");
		var filename=$("#selsong").attr("filename");
		var songpath=$("#selsong").attr("path");
		var samplerName=$("#selsampler").attr("samplerName");
		var arrayJson= JSON.stringify({"filename":filename,"songpath":songpath,"samplerName":samplerName,"customtext":customtext});
		$.ajax({
		    type: 'POST',
		    url: 'loadsong',
		    data: arrayJson, // or JSON.stringify ({name: 'jonas'}),
		    success: function(data) { 
		    	if (data=="OK"){
		    		$("#status").text("iddle");
		    	}
		    },
		    contentType: "application/json",
		   
		});
		}

		
	});

	$('#controls').on('click', '#play', function(){
		if ($("#status").text()=="ready"){
			$("#status").text("playing");
			$.ajax({
			    url: 'playsong',
			    success: function(data) { 
			    	if (data=="recorded"){
			    			
			    			loadSamplers();
			    			$("#customtext").val("");
			    	}
			    }
			});
		} else {
			alert("song must be loaded first");
		}
	});

	$('#controls').on('click', '#stop', function(){
		$.ajax({
			    url: 'stopsong',
			    success: function(data) { 
			    	setTimeout(function(){
			    		loadSamplers();
			    		$("#status").text("iddle");
			    	 }, 2000);
			    	

			    }
			});
	});
	//END CONTROLS





});

function waitForSongLoaded(){
	var songLoaded=false;
	var watcher=setInterval(function(){
		if (songLoaded){
			//song is ready
			clearInterval( watcher );

		} else {
			//keep watching
			$.ajax({
		    url: 'songloaded',
		    success: function(data) { 
		    	if (data=="loaded"){
		    		songLoaded=true;
		    		$("#status").text("ready");
		    	}
		    }
		});
		}
	}, 3000);
}

function loadKarSongs(){
	   $.getJSON( "getkarsongs", function( data ) {
  var items = [];

  $.each( data, function( key, val ) {

    items.push( "<li class='song' id='" + key + "' path='"+val[1]+"'>" + val[0] + "</li>" );
  });
 
  $( "<ul/>", {
    "class": "my-new-list",
    html: items.join( "" )
  }).appendTo( "#songlist" );
});
}

function loadSamplers(){
	$("#samplerlist").html("");
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
