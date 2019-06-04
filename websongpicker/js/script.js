$(document).ready(function() {

  $('#searchbar').on('input', function() {
    $(".song").removeClass("hidden");
    var input=$("#searchbar").val().toUpperCase();
    if (input.length>2){
      $(".song").each(function(){
        if (!$(this).text().toUpperCase().includes(input)){
          $(this).addClass("hidden");
        }
      });
    }
  });

  $.getJSON("songs.json", function(data) {
    var items = [];
    $.each(data, function(key, val) {
      console.log(val);
      $("#songlist").append('<div class="song" songid="' + val["songid"] + '">' + val["title"] + '</div>')
      //  items.push( "<li id='" + key + "'>" + val + "</li>" );
    });

  });

  $("#next").on("click", function(e) {
    if ($(".song.selected").length==0){
      alert("No has seleccionado ninguna canción");
      return false;
    } else {
    $(".choose").hide();
    $(".yourname").show();
  }
  });

  $("#songlist").on("click", ".song", function(e) {
    $(".song").removeClass("selected");
    $(this).addClass("selected");
  });


  function saveSinger(songid, name) {
    $("#dummy").load("savesinger.php?songid=" + songid + "&name=" + encodeURI(name), function(response, status, xhr) {
      console.log(response);
        if (response == "1") {
          return true;
        } else {
          return false;
        }

    });
  }


  $('form').on('submit', function(e) { //use on if jQuery 1.7+
    e.preventDefault(); //prevent form from submitting
      if ($("#nombre").val()==""){
        alert("No te has puesto nombre a ti mismo");
        return false;
    }
    if ($(".song.selected").length==0){
      alert("No has seleccionado ninguna canción");
      return false;
    }
    $(".yourname").hide();
    $("body").addClass("fuego");
    var song = $(".song.selected").attr("songid");
    var name = $("#nombre").val();
    //alert(name);
    console.log(song);
    console.log(name);

    //save to file
    saveSinger(song, name)
    if (1==1) {
      //OK message
      $(".choose").hide();
      $("#OK").show();

      $("#OK .custom").html("<h3>" + $(".song[songid=" + song + "]").text() + "</h3><p>" + name + "</p>");
    } else {
      alert("Ha habido un error al grabar tu canción.");
    }
  });

});
