#! /bin/bash
cp balena.service /lib/systemd/system/
cp start_hss_container.service /lib/systemd/system/
chmod +x updatefeature/run_update.py
chmod +x updatefeature/run_update_in_shell.sh
chmod +x updatefeature/watch_updatefile.sh
cp updatefeature/updatefeature.service /lib/systemd/system/
systemctl daemon-reload
systemctl enable balena.service
systemctl start balena.service
systemctl enable start_hss_container.service
systemctl start start_hss_container.service
systemctl enable updatefeature.service
systemctl start updatefeature.service