#!/bin/bash
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

echo "$(/usr/local/JSBach/scripts/client_srv_cli ifwan $command) <br>"


/bin/cat << EOM
</body>
</html>
EOM
