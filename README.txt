Assignment-1 Overview:
  This application is a user-friendly graphical interface for simulating and analyzing power grids using pandapower. It allows users to import grid data, run simulations, visualize the results and predict Topology in specific cases. This guide is intended for first-time users to help them navigate and utilize the application effectively.

Authors:
1. Ran Lei
2. Yashwanth Damodaran

Requirements:
•	Python 3.x
•	PyQt5: For the GUI.
•	pandapower: For power grid simulations.
•	xml.etree.ElementTree: For parsing XML files.

Installation:
1.	Ensure Python 3.x is installed on your system.
2.	Install necessary libraries using pip:
	pip install PyQt5 
	pip install pandapower
 
Usage:
1.	Starting the Application: Run the script to open the GUI.
2.	Importing Files:
•	Use the 'Import EQ File' and 'Import SSH File' buttons to upload your grid data files.
•	EQ and SSH files should be in XML format.
3.	Running the Simulation:
•	Select the simulation mode via the Mode Selection dialog.
•	Options include 'Construct Full AC Grid' or 'Create Substation Topology'.
4.	Viewing Results:
•	Upon completion, the simulation results are displayed in a graphical format.
•	An HTML file with detailed results is generated, which can be opened for in-depth analysis.
•	In case of PP_Brussels, Topology if created and predicted and is displayed in a Red box for easier identification.

Features:
•	File Import: Import EQ (Equipment) and SSH (State Estimation) files.
•	Mode Selection: Choose between full grid construction or substation topology.
•	Graphical Visualization: Visualize the power grid using pandapower’s plotting capabilities.
•	HTML Output: Generates an HTML file for detailed analysis of the simulation results.

Note:
This application is developed for educational and simulation purposes. It requires a basic understanding of power grid systems and pandapower.

Support:
For any queries or support, please contact the developer at yda@kth.se or rlei@kth.se
