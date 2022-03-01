if [ $1 == "vivado" ]
then
	echo "Mounting fstab"
	sudo mount -a
	echo "Connecting to $1 2020.1"
	source /mnt/storage/sw/Xilinx/Vivado/2020.1/settings64.sh
	vivado
fi
if [ $1 == "hdl" ]
then
	echo "Connecting to $1"
	source /eda/tsmc65_setup.sh
	hds
fi
