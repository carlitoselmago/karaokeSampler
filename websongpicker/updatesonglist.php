<?php
header('Access-Control-Allow-Origin:*');
header('Access-Control-Allow-Headers:Content-Type');
//header('Content-Type: application/json; Charset=UTF-8;');

//var_dump($_POST);
$data = json_decode(file_get_contents('php://input'), true);
var_dump($data);

//if (count($data)>0){
  var_dump(file_put_contents("songs.json",json_encode($data)));
//}

//echo $data["operacion"];
?>
