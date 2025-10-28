#!/bin/bash

source /usr/local/JSBach/conf/variables.conf

# Cabecera HTTP obligatoria
echo "Content-type: text/html"
echo ""

# Bloque HTML con EOF
/bin/cat <<EOM
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Hola Mundo CGI</title>
</head>
<body>
EOM

modo=$(echo "$QUERY_STRING" | sed -n 's/.*MODO=\([^&]*\).*/\1/p')
ifwan=$(echo "$QUERY_STRING" | sed -n 's/.*IFWAN=\([^&]*\).*/\1/p')
ip=$(echo "$QUERY_STRING" | sed -n 's/.*IP=\([^&]*\).*/\1/p')
masc=$(echo "$QUERY_STRING" | sed -n 's/.*MASC=\([^&]*\).*/\1/p')
pe=$(echo "$QUERY_STRING" | sed -n 's/.*PE=\([^&]*\).*/\1/p')
dns=$(echo "$QUERY_STRING" | sed -n 's/.*S_DNS=\([^&]*\).*/\1/p')
ssid=$(echo "$QUERY_STRING" | sed -n 's/.*SSID=\([^&]*\).*/\1/p')
password=$(echo "$QUERY_STRING" | sed -n 's/.*PASSWORD=\([^&]*\).*/\1/p')


# --- Ruta absoluta de tu script ---
SCRIPT_PATH="$DIR/$NOMBRE_EQUIPO/$DIR_SCRIPTS/client_srv_cli"

# Si es wifi y hay SSID, añadimos SSID y PASSWORD
if [ -n "$ssid" ]; then
    CMD="$SCRIPT_PATH ifwan configurar $modo $ifwan $ip $masc $pe $dns \"$ssid\" \"$password\""
else
    CMD="$SCRIPT_PATH ifwan configurar $modo $ifwan $ip $masc $pe $dns"
fi


# --- Ejecutar comando ---
# IMPORTANTE: asegúrate de que www-data tenga permisos para ejecutarlo (sudoers si es necesario)
eval $CMD >/tmp/ifwan_out.txt 2>&1

# --- Mostrar página de resultado ---
cat <<EOM
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Guardar configuración IFWAN</title>
</head>
<body>
  <h1>Configuración aplicada</h1>
  <p><b>MODO:</b> $modo</p>
  <p><b>IFWAN:</b> $ifwan</p>
  <p><b>IP:</b> $ip</p>
  <p><b>MÁSCARA:</b> $masc</p>
  <p><b>PUERTA DE ENLACE:</b> $pe</p>
  <p><b>SERVIDOR DNS:</b> $dns</p>
EOM

if [ -n "$ssid" ]; then
cat <<EOM
  <p><b>SSID:</b> $ssid</p>
  <p><b>CONTRASEÑA:</b> $password</p>
EOM
fi

# --- Mostrar salida del comando ---
if [ -f /tmp/ifwan_out.txt ]; then
    echo "<hr><h3>Salida del script:</h3><pre>"
    cat /tmp/ifwan_out.txt | sed 's/&/\&amp;/g;s/</\&lt;/g;s/>/\&gt;/g'
    echo "</pre>"
fi

cat <<EOM
  <hr>
  <a href="/$DIR_CGI/config-ifwan.cgi">Volver a configuración</a>
</body>
</html>
EOM