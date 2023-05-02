echo "---------------------------------"
echo "Setting up Can Interface"
echo "---------------------------------"
echo "Set down Interfaces"
sudo ip link set down $1
echo "---------------------------------"
echo "Configure Interfaces"
sudo ip link set $1 type can bitrate $2 phase-seg1 $3 phase-seg2 $4 sjw $5 sample-point $6
echo "---------------------------------"
echo "Bring up Interfaces"
sudo ip link set up $1
echo "---------------------------------"
