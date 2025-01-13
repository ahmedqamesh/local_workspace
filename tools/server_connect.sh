if [ $1 == "vivado" ]
then
	VIVADO_FILE=/mnt/storage/sw/Xilinx/Vivado/2020.2/settings64.sh
	if test -f "$VIVADO_FILE"; then
	    echo "$VIVADO_FILE exists."
	else 	
	    echo "Mounting fstab"
	    sudo mount -a
	fi
	echo "Connecting to $1 2020.2"
	source $VIVADO_FILE
	vivado
fi
if [ $1 == "hdl" ]
then
	HDL_FILE=/eda/tsmc65_setup.sh
	if test -f "$HDL_FILE"; then
	    echo "$HDL_FILE exists."
	else 	
	    echo "Mounting fstab"
	    sudo mount -a
	fi
	echo "Connecting to $1"
	source /eda/tsmc65_setup.sh
	hds
fi
if [ $1 == "sdk" ]
then
	VIVADO_FILE=/mnt/storage/sw/Xilinx/SDK/2018.3/settings64.sh
	if test -f "$VIVADO_FILE"; then
	    echo "$VIVADO_FILE exists."
	else 	
	    echo "Mounting fstab"
	    sudo mount -a
	fi
	echo "Connecting to $1 2018.3"
	source $VIVADO_FILE
	xsdk

fi
if [ $1 == "tcl" ]
then
	VIVADO_FILE=/mnt/storage/sw/Xilinx/Vivado/2020.2/settings64.sh
	if test -f "$VIVADO_FILE"; then
	    echo "$VIVADO_FILE exists."
	else 	
	    echo "Mounting fstab"
	    sudo mount -a
	fi
	echo "Connecting to $1 2020.2"
	source $VIVADO_FILE
	vivado -mode $1

fi




