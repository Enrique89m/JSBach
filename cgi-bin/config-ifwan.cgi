#!/bin/bash

source /usr/local/JSBach/conf/variables.conf

echo "Content-type: text/html"
echo ""

# --- Obtener parámetros GET ---
modo=$(echo "$QUERY_STRING" | sed -n 's/.*MODO=\([^&]*\).*/\1/p')
ifwan=$(echo "$QUERY_STRING" | sed -n 's/.*IFWAN=\([^&]*\).*/\1/p')
ipaddr=$(echo "$QUERY_STRING" | sed -n 's/.*IP=\([^&]*\).*/\1/p')
mask=$(echo "$QUERY_STRING" | sed -n 's/.*MASC=\([^&]*\).*/\1/p')
gateway=$(echo "$QUERY_STRING" | sed -n 's/.*PE=\([^&]*\).*/\1/p')
dns=$(echo "$QUERY_STRING" | sed -n 's/.*S_DNS=\([^&]*\).*/\1/p')
ssid=$(echo "$QUERY_STRING" | sed -n 's/.*SSID=\([^&]*\).*/\1/p')
password=$(echo "$QUERY_STRING" | sed -n 's/.*PASSWORD=\([^&]*\).*/\1/p')
action=$(echo "$QUERY_STRING" | sed -n 's/.*ACTION=\([^&]*\).*/\1/p')

# --- Determinar radio marcado ---
checked_dhcp=""
checked_manual=""
[ "$modo" = "dhcp" ] && checked_dhcp="checked"
[ "$modo" = "manual" ] && checked_manual="checked"

# --- FUNC: convertir CIDR a máscara ---
cidr_to_mask() {
    local cidr=$1
    if [[ "$cidr" =~ ^[0-9]+$ ]] && [ "$cidr" -ge 0 ] && [ "$cidr" -le 32 ]; then
        local mask=""
        local full_octets=$((cidr/8))
        local remaining_bits=$((cidr%8))

        for ((i=0;i<4;i++)); do
            if [ $i -lt $full_octets ]; then
                mask+="255"
            elif [ $i -eq $full_octets ]; then
                mask+=$(( 256 - 2**(8-remaining_bits) ))
            else
                mask+="0"
            fi
            [ $i -lt 3 ] && mask+="."
        done
        echo "$mask"
    else
        echo "$cidr"
    fi
}

# --- Mostrar en input visible ---
mask_visible=$(cidr_to_mask "$mask")

# --- Listar interfaces ---
interfaces=$(ip -o link show | awk -F': ' '{print $2}')

# --- Detectar si interfaz seleccionada es wifi ---
is_wifi=0
if [ -n "$ifwan" ]; then
    if iw dev "$ifwan" info >/dev/null 2>&1; then
        is_wifi=1
    fi
fi

# --- Escanear SSID si es wifi ---
ssid_options=""
if [ "$is_wifi" -eq 1 ]; then
    ip link set "$ifwan" up >/dev/null 2>&1
    scan_output=$(timeout 8s sudo /sbin/iwlist "$ifwan" scan 2>/dev/null | grep 'ESSID' | sed 's/.*ESSID:"\(.*\)"/\1/')
    unique_ssids=$(echo "$scan_output" | sort -u)
    while IFS= read -r s; do
        [ -z "$s" ] && continue
        esc=$(printf '%s' "$s" | sed -e 's/&/\&amp;/g' -e 's/"/\&quot;/g' -e "s/'/&#39;/g" -e 's/</\&lt;/g' -e 's/>/\&gt;/g')
        if [ "$s" = "$ssid" ]; then
            ssid_options+="<option value=\"$esc\" selected>$esc</option>"
        else
            ssid_options+="<option value=\"$esc\">$esc</option>"
        fi
    done <<< "$unique_ssids"
fi

# --- Generar opciones de interfaz ---
select_options=""
for iface in $interfaces; do
    [ "$iface" = "lo" ] && continue
    esciface=$(printf '%s' "$iface" | sed -e 's/&/\&amp;/g' -e 's/"/\&quot;/g' -e "s/'/&#39;/g" -e 's/</\&lt;/g' -e 's/>/\&gt;/g')
    if [ "$iface" = "$ifwan" ]; then
        select_options+="<option value=\"$esciface\" selected>$esciface</option>"
    else
        select_options+="<option value=\"$esciface\">$esciface</option>"
    fi
done

# --- Página HTML ---
cat <<EOM
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Configuración IFWAN</title>
  <style>
    input[readonly], input:disabled, select:disabled {
      background-color: #eee;
      color: #666;
    }
    label {
      display: inline-block;
      width: 180px;
    }
  </style>
  <script>
    function toggleFields() {
      const dhcp = document.getElementById('modo_dhcp').checked;
      const ip = document.getElementById('ip');
      const maskVisible = document.getElementById('maskVisible');
      const gateway = document.getElementById('gateway');
      const dns = document.getElementById('dns');

      if (dhcp) {
        ip.value = "";
        maskVisible.value = "";
        gateway.value = "";
        dns.value = "";
        ip.readOnly = true;
        maskVisible.readOnly = true;
        gateway.readOnly = true;
        dns.readOnly = true;
      } else {
        ip.readOnly = false;
        maskVisible.readOnly = false;
        gateway.readOnly = false;
        dns.readOnly = false;
      }

      const actionField = document.getElementById('actionField');
      if (actionField) actionField.value = "";
    }

    function toggleWifi() {
  const actionField = document.getElementById('actionField');
  if (actionField) actionField.value = "scan";
  document.getElementById('configForm').action = "/$DIR_CGI/config-ifwan.cgi"; // 👈 vuelve a esta misma página
  document.getElementById('configForm').submit();
}


    // =========================
    // MÁSCARA -> CIDR
    // =========================
    function maskToCIDR(maskStr) {
      if (!maskStr) return "";
      if (/^[0-9]+$/.test(maskStr)) return maskStr;
      const parts = maskStr.split('.');
      if (parts.length !== 4) return maskStr;
      let bits = 0;
      for (let p of parts) {
        const num = parseInt(p, 10);
        if (isNaN(num) || num < 0 || num > 255) return maskStr;
        bits += num.toString(2).split('1').length - 1;
      }
      return bits.toString();
    }

    function updateMaskCIDR() {
      const maskInput = document.getElementById('maskVisible');
      if (!maskInput) return;
      const cidr = maskToCIDR(maskInput.value.trim());
      if (cidr) {
        maskInput.setAttribute('title', '/' + cidr);
      } else {
        maskInput.removeAttribute('title');
      }
    }

    function doSave() {
      const actionField = document.getElementById('actionField');
      if (actionField) actionField.value = "save";

      // Pasar valor convertido al input oculto
      const maskVisible = document.getElementById('maskVisible');
      const maskHidden = document.getElementById('maskHidden');
      if (maskVisible && maskHidden) {
        maskHidden.value = maskToCIDR(maskVisible.value.trim());
      }

      return true;
    }
  </script>
</head>
<body onload="toggleFields()">
  <h1>Configuración WAN</h1>

  <form action="/$DIR_CGI/guardar-ifwan.cgi" method="get" id="configForm">
    <input type="hidden" name="ACTION" id="actionField" value="">
  <label>
    <input type="radio" name="MODO" value="dhcp" id="modo_dhcp" $checked_dhcp onclick="toggleFields()"> DHCP
  </label><br>
  <label>
    <input type="radio" name="MODO" value="manual" id="modo_manual" $checked_manual onclick="toggleFields()"> Manual
  </label><br><br>

  <label for="ifwan">Seleccionar interfaz:</label>
  <select name="IFWAN" id="ifwan" onchange="toggleWifi()">
    $select_options
  </select>
  <br><br>

  <label for="ip">IP:</label>
  <input type="text" name="IP" id="ip" value="$ipaddr"><br>

  <label for="maskVisible">Máscara:</label>
  <input type="text" id="maskVisible" value="$mask_visible" oninput="updateMaskCIDR()">
  <input type="hidden" name="MASC" id="maskHidden" value="$mask"><br>

  <label for="gateway">Puerta de enlace:</label>
  <input type="text" name="PE" id="gateway" value="$gateway"><br>

  <label for="dns">Servidor DNS:</label>
  <input type="text" name="S_DNS" id="dns" value="$dns"><br><br>
EOM

# --- Campos wifi si aplica ---
if [ "$is_wifi" -eq 1 ]; then
    cat <<EOM
    <div id="wifiFields">
  <label for="ssid">SSID:</label>
  <select name="SSID" id="ssid">
    $ssid_options
  </select><br>

  <label for="password">Contraseña:</label>
  <input type="password" name="PASSWORD" id="password" value="$password"><br><br>
</div>
EOM
fi

# --- Resto del HTML ---
cat <<EOM
    <input type="submit" value="Guardar" onclick="return doSave();">
  </form>

  <hr>
EOM

if [ "$action" = "save" ]; then
cat <<EOM
  <h2>Valores seleccionados:</h2>
  <p><b>MODO:</b> $modo</p>
  <p><b>IFWAN:</b> $ifwan</p>
  <p><b>IP:</b> $ipaddr</p>
  <p><b>MÁSCARA:</b> $mask</p>
  <p><b>PUERTA DE ENLACE:</b> $gateway</p>
  <p><b>SERVIDOR DNS:</b> $dns</p>
EOM

if [ "$is_wifi" -eq 1 ]; then
cat <<EOM
  <p><b>SSID:</b> $ssid</p>
  <p><b>CONTRASEÑA:</b> $password</p>
EOM
fi
fi

cat <<EOM
</body>
</html>
EOM
