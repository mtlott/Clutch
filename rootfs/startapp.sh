#!/usr/bin/with-contenv sh

cd /watch
if [ "${CLUTCH_DEBUG:-0}" -eq 1 ]; then
  exec /usr/bin/xterm >> /config/log/clutch.debug.log
else
  exec /usr/bin/tail -f /dev/null
fi