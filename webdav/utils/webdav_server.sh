#!/usr/bin/env bash
rm -rf /run/ui-ssh-webdav.socket
/usr/local/uissh/webdav/webdav --config /usr/local/uissh/webdav/config.yaml &
sleep 3
chown www-data.www-data /run/ui-ssh-webdav.socket