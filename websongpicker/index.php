<!doctype html>
<html lang="es">

<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">

  <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js"></script>
  <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
<link href="https://fonts.googleapis.com/css?family=Source+Code+Pro:300,400,700,900&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="css/style.css" />
  <script src="js/script.js"></script>
</head>

<body>
  <?php
  if (!isset($_GET)){
  if (isset($_COOKIE["singer"])){

  //  var_dump($_COOKIE["singer"]);
    $minutes= (intval($_COOKIE["singer"])-time())/60;
    $min= intval($minutes);
    $secs=  (intval($_COOKIE["singer"])-time())-($min*60)
  ?>
    <div class="vert stop">
      <h2>Podrás añadir otra canción en <?php echo intval($minutes); ?> minutos <br><?php echo $secs;?> segundos</h2>
    </div>
  <?php
  return die();
}
  }
;?>
  <article class="container-fluid">
    <div class="">
      <div class="">
      <!--  <h1>XTREME KARAOKE</h1>-->
        <div class="choose">
          <input type="text" id="searchbar" class="form-control" placeholder="Buscar canción">
          <div id="songlist">
          </div>
          <button type="button" id="next" class="btn btn-large btn-primary">Siguiente</button>
        </div>

        <div class="yourname bottom">
          <form>
            <div class="form-group">
              <input type="text" class="form-control" id="nombre" placeholder="Tu nombre">
            </div>
            <button type="submit" id="submit" class="btn btn-large btn-primary">Enviar</button>
          </form>
        </div>

        <div id="OK" class="center">
          <div class="vert">
          <h3>Canción añadida</h3>
          <div class="custom"></div>
          </div>
        </div>
        <div id="KO" class="center">
            <div class="vert">
          <h3></h3>
            </div>
        </div>
      </div>
    </div>
  </article>
  <div id="dummy" style="display:none"></div>
</body>

</html>
