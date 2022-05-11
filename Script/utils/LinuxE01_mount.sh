#! /bin/bash
# Mount Linux partition in E01 file

sudo mkdir /mnt/ewf/
sudo mkdir /mnt/ewf_mount/
ewfinfo $1 #/mnt/ewf/ewf1
sudo ewfmount $1 /mnt/ewf

i=0
while IFS= read -r line
do
	myarray[ $i ]=$(echo $line | awk '{printf  "%d",$3}')
	echo "$i: $line"
	(( i++ ))
done <<< $(sudo mmls /mnt/ewf/ewf1 | grep "Linux")

echo "Which slot you want to mount? "
read num

# sudo losetup -f # Look for free loop device
DEV_LOOP_NUM=$(sudo losetup -f | sed 's/\/dev\/loop//g')
echo "[+] DEV_LOOP_NUM = $DEV_LOOP_NUM"
FINAL_OFFSET=$(expr ${myarray[$num]} "*" 512) 
echo "[+] FINAL_OFFSET = $FINAL_OFFSET"

losetup_COMMAND="sudo losetup --read-only --offset $FINAL_OFFSET /dev/loop$DEV_LOOP_NUM /mnt/ewf/ewf1"
echo "[+] $losetup_COMMAND"
$losetup_COMMAND # Execute command

MOUNT_RO="sudo mount -o ro,noload,noexec /dev/loop$DEV_LOOP_NUM /mnt/ewf_mount/"
echo "[+] $MOUNT_RO"
$MOUNT_RO # Execute command
