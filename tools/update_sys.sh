#!/bin/bash
if [ $1 == "-c" ]
then
	echo "==========================Clean .log files==========================="
	rm *.backup.log*
	rm *.log*
	rm *.backup.jou*
	rm vivado_pid*
	sudo sh -c "/usr/bin/echo 1 > /proc/sys/vm/drop_caches"
	sudo sh -c "/usr/bin/echo 2 > /proc/sys/vm/drop_caches"
	sudo sh -c "/usr/bin/echo 3 > /proc/sys/vm/drop_caches"
	echo "==========================Free Memory ================================"
	free +/- buff/cache
	free -m
elif [ $1 == "swap" ]
then
	sudo swapoff -a
	echo "Resize the swap to 8GB"
	#if = input file
	#of = output file
	#bs = block size
	#count = multiplier of blocks
	sudo dd if=/dev/zero of=/home/dcs/myswap count=8 bs=1G
	sudo chmod 600 /home/dcs/myswap
	sudo mkswap /home/dcs/myswap
	sudo swapon /home/dcs/myswap
	sudo sysctl vm.swappiness=70
	echo "System swappiness=$swappiness"
	#sudo nano /etc/sysctl.conf
	#To verify swap's size
	#nano /etc/fstab
	#Append the following line:
	#/swapfile1 none swap sw 0 0
	# or in my case : /run/media/dcs/data2/myswap   swap    swap    sw  0   0
	#swapon /run/media/dcs/data2/myswap
	#sudo swapoff /swapfile1 #Disable swap	
	#sleep 10	
	swapon --summary
	free -h
	echo "==========================Free Swap Memory==========================="
	swappiness="$(cat /proc/sys/vm/swappiness)"
	echo "System swappiness=$swappiness"
	sudo sysctl vm.swappiness=70
	Nswappiness="$(cat /proc/sys/vm/swappiness)"
	echo "New System swappiness=$Nswappiness"
	free -m	#Check space
	sudo sysctl -w vm.overcommit_memory=1
	sudo swapon -a #Enable swap
	grep -i --color swap /proc/meminfo

else
	echo "==========================Clean .log files==========================="
	rm *.backup.log*
	rm *.backup.jou*
	rm vivado_pid*
	echo "======================Delete temporary DB files======================="
	sudo rm -f /var/lib/rpm/__*
	sudo rm /var/lib/rpm/.rpm.lock
	sudo rm /var/lib/rpm/.dbenv.lock
	sudo rm -rf ~/.config/google-chrome/Singleton*
	sudo logrotate -f /etc/logrotate.conf
	sudo rm -rf /tmp/*
	sudo rm -rf /tmp/.x2go-dcs/*
	sudo rm -rf /var/crash/*
	sudo rm -rf /var/tmp/*
	sudo yum clean metadata
	sudo yum clean packages
	sudo yum autoremove
	echo "=====================rebuild RPM database ========================="
	sudo rpm --rebuilddb -v -v
	echo "=======================Update yum database==========================="
	sudo yum makecache
	echo "==============================Clean yum=============================="
	sudo rm -fr /var/cache/yum/*
	sudo yum clean all
	echo "Update yum"
	sudo yum update -y --exclude google-chrome-stable

	echo "==================Clean Up Remaining Dependencies:======================"
	sudo yum autoremove
	echo "=======================Current Kernel========================="
	uname -snr
	echo "=======================Removing Old Kernels========================="
	rpm -q kernel
	sudo package-cleanup --oldkernels --count=1
	echo "==============================Update Conda==========================="
	conda clean -a -y
	#conda config --set channel_priority strict
	conda config --set channel_priority flexible
	conda update conda -y
	conda update --all -y
	conda update -n base -c defaults conda

fi
