#!/bin/bash
# shot.sh in.svg out.png width height [background]
printf '<html><body style="margin:0;background:%s"><img src="%s" style="width:%spx;height:%spx;display:block"></body></html>' "${5:-#e2d5b7}" "$(realpath "$1")" "$3" "$4" > _shot.html
google-chrome --headless=new --disable-gpu --hide-scrollbars --screenshot="$2" --window-size="$3,$4" "file://$PWD/_shot.html" >/dev/null 2>&1
