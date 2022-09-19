#!/usr/bin/env bash
rm -rf /run/ui-ssh-webdav.socket
/usr/local/uissh/webdav/webdav --config /usr/local/uissh/webdav/config.yaml
chown www-data.www-data /run/ui-ssh-webdav.socket