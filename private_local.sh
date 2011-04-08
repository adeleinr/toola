echo -n "Copying private files ..."
scp settings_local.py webme@184.106.152.183:/web/webme/releases/current/webme/
scp private_remote.sh webme@184.106.152.183:/web/webme/releases/current/webme/
scp -r data/*.json webme@184.106.152.183:/web/webme/releases/current/webme/data
scp -r media_rsc/uploads webme@184.106.152.183:/web/webme/releases/current/webme/media_rsc/
