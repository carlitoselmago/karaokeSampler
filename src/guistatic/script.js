$( document ).ready(function() {


	window.selecteSongPath=""
	//DELETE THIS
	window.selecteSongPath="KARsongs/LATINAS/Bella y bestia son.kar";
	//DELETE THIS

 	loadKarSongs();
 	loadSamplers();
 	loadSingers();
 	//setInterval(loadSingers, 10000);
 	
 	$( function() {
   	 	$( ".sortable" ).sortable();
   		 $( ".sortable" ).disableSelection();
  	} );

 	$('#songlist').on('click', '.song', function(){
    	var songName=$(this).text();
    	var songPath=unescape($(this).attr("path"));
    	var fileName=songName+".kar";
    	$("#selsong").text(songName);
    	window.selecteSongPath=songPath;
    	//$("#selsong").attr("path",songPath);
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
		var songpath=window.selecteSongPath;//$("#selsong").attr("path");
		
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

	$('#controls').on('click', '#pause', function(){
		$.ajax({
			url: 'pausesong',
			success: function(data) { 
				setTimeout(function(){
					//loadSamplers();
					$("#status").text("PAUSED");
				 }, 2000);
				

			}
		});
	});

	$('#controlssingers').on('click', '#nextSinger', function(){
		var url='http://htmlfiesta.com/karaoke/deletesinger.php';
		$.ajax({
			    url:url,
			    method:"GET",
			    data:{"singerid":$(".singer").first().attr("singerid")},
			    success: function(data) { 

			    	$("#customtext").val($(".singer").first().attr("singer"));
			    	$(".song#"+$(".singer").first().attr("songid")).trigger("click");

			    	//delete
			    	$(".singer").first().remove();
			    }
			});
		
	});

	$('#controlssingers').on('click', '#updatesingers', function(){
			loadSingers();
	});
	$('#controlssingers').on('click', '#sendsongs', function(){
		var songlist=[];
		$( "#songlist li" ).each(function( index ) {
			songlist.push({"songid":$(this).attr("id"),"title":$(this).text()});
		});
		var url='http://htmlfiesta.com/karaoke/updatesonglist.php';
		$.ajax(url, {
		    data : JSON.stringify(songlist),
		    contentType : 'application/json',
		    type : 'POST',
		    success: function (data) {
		    	console.log(data);
        		alert("Updated songs"); 
        	}
		});

		console.log(songlist);
	});

	$('#singerlist').on('click', '.deletesinger', function(){
		var singerid=$(this).closest(".singer").attr("singerid");
		var url='http://htmlfiesta.com/karaoke/deletesinger.php';
		$.ajax({
			    url:url,
			    method:"GET",
			    data:{"singerid":singerid},
			    success: function(data) { 
			    	//delete
			    	$(".singer[singerid="+singerid+"]").remove();
			    }
			});
	});



	$('#controls').on('click', '#play', function(){
		playSong();
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

function playSong(){
	if ($("#status").text()=="ready!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"){
			$("#status").text("playing");
			$.ajax({
			    url: 'playsong',
			    allways: function(data) { 
			    	if (data=="recorded"){
			    			$("#customtext").val("");
			    			loadSamplers();
			    			
			    	}
			    }
			});
		} else {
			alert("song must be loaded first");
		}
}

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
		    		$("#status").text("ready!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!");
		    		if ($("#autoplay").is(':checked') ){
		    			playSong();
		    		}
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

    items.push( "<li class='song' id='" + key + "' path='"+escape(val[1])+"'>" + val[0] + "</li>" );
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

function loadSingers(){
	var url="http://htmlfiesta.com/karaoke/listsingers.php";
	$.getJSON( url, function( data ) {
	  //var items = [];
	  $("#singerlist").html("");
	  $.each( data, function( key, val ) {
	  	 var songname=$(".song#"+val["songid"]).text();
	   $("#singerlist").append('<div singerid="'+val["singerid"]+'" songid="'+val["songid"]+'" singer="'+val["name"]+'" class="singer">'+val["name"]+' - '+songname+'<span class="deletesinger">X</span></div>');
	  });
   });
 
 
}
