# Preliminary tests
The testing and validation of the MOPS-Hub includes strict assessments of its hardware components. This scripts involved in this repo aims to ensure the reliability,
functionality, and performance of the MOPS-Hub crate across various scenarios. 
An Arduino-based setup was built to test the modules under controlled conditions.

![MOPS-Hub Readout](https://gitlab.cern.ch/mopshub/mopshub_testing/-/raw/master/preliminary_tests/figures/mopshub_irradiation_test_setup_cic.png?ref_type=heads)

## List of scripts 
### Test Files
1. **test_can_interface_card.py**: Runs automated tests on the CAN Interface Card (CIC) to ensure correct operation. Data is collected continuously over an extended period using the Arduino-based setup.
2. **test_power_card.py**: Runs automated tests to validate the PP3-power card’s performance and functionality.
- Data is collected continuously over an extended period using the Arduino-based setup. 
- The script control over the connected power supply during operation.
3. **test_power_supply.py** : Controls the supply power during operation [Used during the Proton Campaign].

### Analysis Files
1. **analyze_cic_v2_results.py**: Processes and analyzes data from CAN Interface Card (CIC) tests including:
	- Total Ionizing Dose (TID).
	- Neutron Fluence.
	- Magnetic Field.
2. **analyze_cic_configurations_test.py**: to analyze the data of the VCAN voltages on the CAN Interface Card (CIC) under different Configurations.
3. **analyze_powersupply_results.py**: Analyzes the performance of the power supply to reflect current and voltage behavior of the connected DUT (Device Under Test).
4. **analyze_powercard_results.py**: Processes and analyzes data from PP3-power card tests including: 
	- Total Ionizing Dose (TID).
	- Neutron Fluence.
	- Magnetic Field.
5. **analyze_magnetic_field_results.py**: Creat a magnetic field map for the Lab setup.<br>

**Note**: Data from each test is saved in the directory: `$PROJ_HOME/preliminary_tests/output_dir/`

# Documentation
- Construction of MOPS-Hub document: [AT2-IP-EP-0021](https://edms.cern.ch/document/2600650/1).
- QA/QC of MOPS-Hub document: [AT2-IP-QA-0053](https://edms.cern.ch/document/2600650/1).

# Contributing and Contact Information:
We welcome contributions from the community please contact : 
- Felix Nitz : `fnitz@uni-wuppertal.de`.
- Ahmed Qamesh `ahmed.qamesh@cern.ch`.
