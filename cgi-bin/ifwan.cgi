#!/bin/bash

source /usr/local/JSBach/conf/variables.conf

echo "Content-type: text/html; charset=utf-8"
echo ""

/bin/cat << EOM
<html>
<head>
  <meta charset="utf-8">
  <title>Hola mundo CGI</title>
</head>
<body>
EOM

command=$(echo "$QUERY_STRING" | sed -n 's/^.*command=\([^&]*\).*$/\1/p')

echo "Configuració WAN <br>"

echo "$($DIR/$NOMBRE_EQUIPO/$DIR_SCRIPTS/client_srv_cli ifwan $command) <br>"


/bin/cat << EOM
</body>
</html>
EOM
