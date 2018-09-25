sudo inotifywait -q -m -e close_write /var/lib/balena/volumes/framectrdata/_data/update.command |
while read -r filename event; do
  sudo python3 run_update_command.py
done