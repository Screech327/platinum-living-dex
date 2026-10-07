#!/bin/sh
# Stamp asset URLs with a version so browsers fetch fresh files after each deploy.
v=$(date +%Y%m%d%H%M%S)
sed -i -E "s#(styles\.css|data\.js|app\.js)(\?v=[0-9]+)?\"#\1?v=$v\"#g" "$(dirname "$0")/../index.html"
echo "assets stamped v=$v"
