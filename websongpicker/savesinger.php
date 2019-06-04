<?php
if (isset($_GET["songid"])){
  $songid=$_GET["songid"];
  $name=urldecode ($_GET["name"]);
  $fecha = new DateTime();
$ts= $fecha->getTimestamp();
  $fichero="singers/".$ts.".txt";
  $content=$songid."\n".$name;
  if (  file_put_contents($fichero, $content)){
  echo "1";

  //save cookie
  $minutes=5;
  $expire= time() + (60 * 5);
  setcookie("singer",  $expire,  $expire, "/"); // unit in seconds
  } else {
    echo "0";
  }

}

 ?>
