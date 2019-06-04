<?php
$dir = "singers/";
chdir($dir);
$singers=array();
array_multisort(array_map('filemtime', ($files = glob("*.*"))), SORT_ASC, $files);
foreach($files as $filename)
{
  $cont=file_get_contents($filename,true);
  $cont=mb_convert_encoding($cont, 'HTML-ENTITIES', "UTF-8");
  $datas=explode("\n", $cont);

  $songid=$datas[0];
  $name=utf8_encode($datas[1]);

  array_push($singers,array("singerid"=>substr($filename, 0, -4),"songid"=>$songid,"name"=>$name));


  //print_r(json_decode(json_encode($singers)));
//	echo "<li>".substr($filename, 0, -4)."</li>";
}

//echo "Coño";
header('Access-Control-Allow-Origin:*');
header('Content-Type: application/json; Charset=UTF-8;');
echo json_encode($singers);



function file_get_contents_utf8($fn) {
     $content = file_get_contents($fn);
      return mb_convert_encoding($content, 'UTF-8',
          mb_detect_encoding($content, 'UTF-8, ISO-8859-1', true));
}
?>
