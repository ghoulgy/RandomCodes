#!/bin/bash
if [[ -n $(find ~/Samples/Analysis -type d -name $(date +'%d%m')) ]]; then
  echo "[+] Dir already exists!\n[+] Redirect to ~/Samples/Analysis/$(date +'%d%m')"
  cd ~/Samples/Analysis/$(date +'%d%m')
else
  echo "[+] Dir not found! Dir created ~/Samples/Analysis/$(date +'%d%m') :D"
  mkdir ~/Samples/Analysis/$(date +'%d%m')
fi
