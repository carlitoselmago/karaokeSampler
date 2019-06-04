<?php
header('Access-Control-Allow-Origin:*');
header('Access-Control-Allow-Headers:Content-Type');
if (isset($_GET["singerid"])){
  $singerFile='singers/'.$_GET["singerid"].'.txt';
  if (file_exists($singerFile)){
    unlink($singerFile);
    echo "1";
    return;
  }
}
echo "0";
return;
?>
