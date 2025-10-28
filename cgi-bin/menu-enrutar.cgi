#!/bin/bash

source /usr/local/JSBach/conf/variables.conf

/bin/cat << EOM

<html>
<head>
<meta http-equiv=Content-Type content="text/html; charset=windows-1252">
<meta content="MSHTML 6.00.2900.3660" name=GENERATOR> 

<style type="text/css">
<!--
.estado {
	font-size: 18px;
	font-style: normal;
	color: #e9ab17;
	font-weight: bold;
	font-family: Georgia, "Times New Roman", Times, serif;
}
.cabecera {
	font-family: Verdana, Arial, Helvetica, sans-serif;
	color: #2A5B45;
}
.Estilo1 {color: #FF00FF}
.Estilo2 {color: #000000}
-->
</style>
</head>
<body>
<h4><a href="/cgi-bin/enrutar.cgi?command=iniciar&" target="body">enrutar iniciar</a></h4>
<h4><a href="/cgi-bin/enrutar.cgi?command=parar&" target="body">enrutar parar</a></h4>
<h4><a href="/cgi-bin/enrutar.cgi?command=estado&" target="body">enrutar estado</a></h4>
</body>
</html>

EOM