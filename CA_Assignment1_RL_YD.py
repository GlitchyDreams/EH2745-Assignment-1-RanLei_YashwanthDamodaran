"""
Computer Applications in Power Systems EH2745 : Assignment 1

Network Creation and Topology Identification

Go through the README file for easier understanding. Thank you for using!

@author1: Ran Lei
@author2: Yashwanth Damodaran
"""

#importing the required modules and specific packages
import sys
import pandapower as pp
import pandapower.networks
import pandapower.topology
import pandapower.plotting
import pandapower.converter
import pandapower.estimation
import pandapower.plotting 
import xml.etree.ElementTree as ET
import pandapower.plotting.to_html as html_output
from PyQt5.QtWidgets import QApplication,QCheckBox, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QFileDialog, QMessageBox, QButtonGroup
from PyQt5.QtGui import QPixmap
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import webbrowser


#This parts creates a PyQt5 GUI with a background image and buttons to import EQ and SSH files and to run the model

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Assignment 1")

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # Load Background Image
        pixmap = QPixmap('Background.png')
        self.bg_label = QLabel(self)
        self.bg_label.setPixmap(pixmap)
        layout.addWidget(self.bg_label)

        # Insert File Buttons
        self.button_EQ = QPushButton("Import EQ File", self)
        self.button_EQ.clicked.connect(self.EQ_file)
        layout.addWidget(self.button_EQ)

        self.button_SSH = QPushButton("Import SSH File", self)
        self.button_SSH.clicked.connect(self.SSH_file)
        layout.addWidget(self.button_SSH)

        # Run Button
        self.button_Run = QPushButton("Run", self)
        self.button_Run.clicked.connect(self.run_model)
        layout.addWidget(self.button_Run)

    def EQ_file(self):
        EQ_file, _ = QFileDialog.getOpenFileName(self, 'Open EQ File')
        self.EQ_file_XML = EQ_file
        self.Message_EQ = "Successfully added EQ File"

    def SSH_file(self):
        SSH_file, _ = QFileDialog.getOpenFileName(self, 'Open SSH File')
        self.SSH_file_XML = SSH_file
        self.Message_SSH = "Successfully added SSH File"

#This is the main part of the code
    def run_model(self):
        
        # Display a dialog box for mode selection
        mode_msg = QMessageBox()
        mode_msg.setIcon(QMessageBox.Question)
        mode_msg.setText("Please select the mode you want to run. Please Note that the currently topology identification works only for PP_Brussels")
        mode_msg.setWindowTitle("Mode Selection")

        # Center-align the message text
        mode_msg.setStyleSheet("QLabel{min-width: 200px;}")

        # Create a button group to ensure only one checkbox is selectable
        button_group = QButtonGroup(mode_msg)

        # Add checkboxes for mode options
        construct_grid_checkbox = QCheckBox("Construct Full AC Grid", mode_msg)
        create_topology_checkbox = QCheckBox("Create Substation Topology", mode_msg)

        # Add checkboxes to the button group
        button_group.addButton(construct_grid_checkbox)
        button_group.addButton(create_topology_checkbox)

        mode_msg.layout().addWidget(construct_grid_checkbox)
        mode_msg.layout().addWidget(create_topology_checkbox)

        # Display the dialog box
        mode_response = mode_msg.exec_()

        # Process the selected mode
        selected_mode = None
        if mode_response == QMessageBox.Ok:
            if button_group.checkedButton() == construct_grid_checkbox:
                selected_mode = 1
            elif button_group.checkedButton() == create_topology_checkbox:
                selected_mode = 2

        # Show disclaimer based on the selected mode
        if selected_mode == 1:
            disclaimer_msg = QMessageBox()
            disclaimer_msg.setIcon(QMessageBox.Information)
            disclaimer_msg.setText("Currently, the Construct Full AC Grid option is selected.")
            disclaimer_msg.setWindowTitle("Disclaimer")
            disclaimer_msg.exec_()
        elif selected_mode == 2:
            disclaimer_msg = QMessageBox()
            disclaimer_msg.setIcon(QMessageBox.Information)
            disclaimer_msg.setText("Currently, the Create Substation Topology option is selected only for PP_Brussels.")
            disclaimer_msg.setWindowTitle("Disclaimer")
            disclaimer_msg.exec_()
        #This is the XML Parsing and data collection part

        tree_EQ = ET.parse(self.EQ_file_XML)
        tree_SSH = ET.parse(self.SSH_file_XML)

        root_EQ = tree_EQ.getroot()
        root_SSH = tree_SSH.getroot()

        # root_EQ = ET.parse('20171002T0930Z_BE_EQ_4.xml')
        # root_SSH = ET.parse('20171002T0930Z_1D_BE_SSH_4.xml')

        cim = "{http://iec.ch/TC57/2013/CIM-schema-cim16#}"
        md = "{http://iec.ch/TC57/61970-552/ModelDescription/1#}"
        entsoe = "{http://entsoe.eu/CIM/SchemaExtension/3/1#}"
        rdf = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}"

        # The required dictionaries are created to store data
        ac_line_segments_dict = {}
        base_voltage_dict = {}
        bay_dict = {}
        busbar_section_dict = {}
        common_switch_dict = {}
        connectivity_node_dict = {}
        current_limit_dict = {}
        curve_data_dict = {}
        equivalent_branch_dict = {}
        energy_consumer_dict = {}
        external_network_injection_dict = {}
        generating_unit_dict = {}
        geographical_region_dict = {}
        line_dict = {}
        linear_shunt_compensator_dict = {}
        operational_limit_set_dict = {}
        petersen_coil_dict = {}
        phase_tap_changer_asymmetrical_dict = {}
        power_transformer_dict = {}
        power_transformer_end_dict = {}
        ratio_tap_changer_dict = {}
        regulating_control_dict = {}
        series_compensator_dict = {}
        substation_dict = {}
        synchronous_machine_dict = {}
        tap_changer_control_dict = {}
        terminal_dict = {}
        voltage_level_dict = {}

        for substation_xml in root_EQ.iter(cim+"Substation"):
            substation_id = substation_xml.get(rdf+"ID")
            substation_dict[substation_id] = {
                'ID': substation_id,
                'name': substation_xml.find(cim+"IdentifiedObject.name").text,
                'region': substation_xml.find(cim+"Substation.Region").get(rdf+"resource")
            }

        #find the elements related to the substation "PP Brussels"
        substation_name_to_find = 'PP_Brussels'
        substation_id_to_find = None
        matching_elements = []
        matching_voltage_levels = []

        if selected_mode == 1:
                # Mode 1: Append all element IDs and matching voltage levels
                for element_xml in root_EQ.iter():
                    element_id = element_xml.get(rdf + 'ID')
                    matching_elements.append(element_id)

                # Copy matching_elements to matching_voltage_levels
                matching_voltage_levels = matching_elements.copy()

        elif selected_mode == 2:
            # Mode 2: Append elements related to the selected substation
            for substation_id, substation_data in substation_dict.items():
                if substation_data['name'] == substation_name_to_find:
                    for element_xml in root_EQ.iter():
                        equipment_container = element_xml.find(cim + 'Equipment.EquipmentContainer')
            
                        if equipment_container is not None and equipment_container.get(rdf + 'resource') == '#' + substation_id:
                            element_id = element_xml.get(rdf + 'ID')
                            matching_elements.append(element_id)
            
            
            for substation_id, substation_data in substation_dict.items():
                if substation_data['name'] == substation_name_to_find:
                    substation_id_to_find = substation_id
                    break
            
            # If the Substation ID is found, search for matching VoltageLevel elements
            if substation_id_to_find:
                for voltage_level_xml in root_EQ.iter(cim + 'VoltageLevel'):
                    substation_resource = voltage_level_xml.find(cim + 'VoltageLevel.Substation').get(rdf + 'resource')
            
                    if substation_resource is not None and substation_resource == '#' + substation_id_to_find:
                        voltage_level_id = voltage_level_xml.get(rdf + 'ID')
                        matching_voltage_levels.append(voltage_level_id)

        for ac_segment_xml in root_EQ.iter(cim + 'ACLineSegment'):
            equipment_container_ACl= ac_segment_xml.find(cim + 'Equipment.EquipmentContainer').get(rdf + 'resource').replace("#", "")
            if equipment_container_ACl in matching_voltage_levels:
                ac_id = ac_segment_xml.get(rdf + 'ID')
                ac_line_segments_dict[ac_id] = {
                    'ID': ac_id,
                    'name': ac_segment_xml.find(cim + 'IdentifiedObject.name').text,
                    'equipment_container': ac_segment_xml.find(cim + 'Equipment.EquipmentContainer').get(rdf + 'resource'),
                    'r': ac_segment_xml.find(cim + 'ACLineSegment.r').text,
                    'x': ac_segment_xml.find(cim + 'ACLineSegment.x').text,
                    'bch': ac_segment_xml.find(cim + 'ACLineSegment.bch').text,
                    'length': ac_segment_xml.find(cim + 'Conductor.length').text,
                    'gch': ac_segment_xml.find(cim + 'ACLineSegment.gch').text,
                    'base_voltage': ac_segment_xml.find(cim + 'ConductingEquipment.BaseVoltage').get(rdf + 'resource'),
                    'r0': ac_segment_xml.find(cim + "ACLineSegment.r0").text,
                    'x0': ac_segment_xml.find(cim + "ACLineSegment.x0").text,
                    'b0ch': ac_segment_xml.find(cim + "ACLineSegment.b0ch").text,
                    'g0ch': ac_segment_xml.find(cim + "ACLineSegment.g0ch").text
                }   
            # print(ac_line_segments)

        for base_voltage_xml in root_EQ.iter(cim + "BaseVoltage"):
            base_voltage_id = base_voltage_xml.get(rdf + "ID")
            base_voltage_dict[base_voltage_id] = {
                'ID': base_voltage_id,
                'nominal_voltage': base_voltage_xml.find(cim + "BaseVoltage.nominalVoltage").text
            }
        # print(base_voltage_dict)

        for bay_xml in root_EQ.iter(cim + 'Bay'):
            bay_id = bay_xml.get(rdf + 'ID')
            bay_dict[bay_id] = {
                'ID': bay_id,
                'name': bay_xml.find(cim + 'IdentifiedObject.name').text,
                'description': bay_xml.find(cim + 'IdentifiedObject.description').text,
                'voltage_level': bay_xml.find(cim + 'Bay.VoltageLevel').get(rdf + 'resource'),
                'mRID': bay_xml.find(cim + 'IdentifiedObject.mRID').text,
            }
        #print(bay_dict)

        def extract_switch_data(root, element_type):
            element_dict = {}
            cim_element_tag = cim + element_type
            for element_xml in root.iter(cim_element_tag):
                element_voltage=element_xml.find(cim + 'Equipment.EquipmentContainer').get(rdf + 'resource').replace("#", "")
                if element_voltage in matching_voltage_levels:
                    element_id = element_xml.get(rdf + 'ID')
                    element_dict[element_id] = {
                        'ID': element_id,
                        'name': element_xml.find(cim + 'IdentifiedObject.name').text,
                        'equipment_container': element_xml.find(cim + 'Equipment.EquipmentContainer').get(rdf + 'resource'),
                        'status': " ",
                        'type': element_type  # Additional key for CIM element type
                    }
            # Update status in the element_dict using SSH data
            for element_xml in root_SSH.iter(cim_element_tag):
                element_id = element_xml.get(rdf + 'about').replace("#", "")
                if element_id in element_dict:
                    element_dict[element_id]['status'] = element_xml.find(cim + "Switch.open").text

            return element_dict

        breaker_dict = extract_switch_data(root_EQ, 'Breaker')
        common_switch_dict.update(breaker_dict)

        disconnector_dict = extract_switch_data(root_EQ, 'Disconnector')
        common_switch_dict.update(disconnector_dict)

        load_break_switch_dict = extract_switch_data(root_EQ, 'LoadBreakSwitch')
        common_switch_dict.update(load_break_switch_dict)

        switch_dict = extract_switch_data(root_EQ, 'Switch')
        common_switch_dict.update(switch_dict)

        # Print the merged common_switch_dict
        #print(common_switch_dict)
              

        element_types = ['BusbarSection', 'DCBusbar']  # Add more types if needed when including DC network
        for busbar_section_xml in root_EQ.iter(cim + 'BusbarSection'):
            busbar_section_id = busbar_section_xml.get(rdf + 'ID')
            busbar_section_dict[busbar_section_id] = {
                'ID': busbar_section_id,
                'name': busbar_section_xml.find(cim + 'IdentifiedObject.name').text,
                'equipment_container': busbar_section_xml.find(cim + 'Equipment.EquipmentContainer').get(rdf + 'resource')
            }
        # print(busbar_section_dict)
        for connectivity_node_xml in root_EQ.iter(cim + 'ConnectivityNode'):
            connectivity_node_container_id = connectivity_node_xml.find(cim + "ConnectivityNode.ConnectivityNodeContainer").get(rdf + "resource").replace("#", "")
            if connectivity_node_container_id in matching_voltage_levels:
                
                connectivity_node_id = connectivity_node_xml.get(rdf + 'ID')
                connectivity_node_dict[connectivity_node_id] = {
                        'ID': connectivity_node_id,
                        'name': connectivity_node_xml.find(cim + 'IdentifiedObject.name').text,
                        'connectivity_node_container': connectivity_node_xml.find(cim + "ConnectivityNode.ConnectivityNodeContainer").get(rdf + "resource")
                }
        for equivalent_branch_xml in root_EQ.iter(cim + 'EquivalentBranch'):
            equipment_container_eq= equivalent_branch_xml.find(cim + 'Equipment.EquipmentContainer').get(rdf + 'resource').replace("#", "")
            if equipment_container_eq in matching_voltage_levels:
                equivalent_branch_id = equivalent_branch_xml.get(rdf + 'ID')
                equivalent_branch_dict[equivalent_branch_id] = {
                    'ID': equivalent_branch_id,
                    'name': equivalent_branch_xml.find(cim + 'IdentifiedObject.name').text,
                    'equivalent_network': equivalent_branch_xml.find(cim + 'EquivalentEquipment.EquivalentNetwork').get(rdf + 'resource'),
                    'base_voltage': equivalent_branch_xml.find(cim + 'ConductingEquipment.BaseVoltage').get(rdf + 'resource'),
                    'r': float(equivalent_branch_xml.find(cim + 'EquivalentBranch.r').text),
                    'x': float(equivalent_branch_xml.find(cim + 'EquivalentBranch.x').text),
                    'equipment_container': equivalent_branch_xml.find(cim + 'Equipment.EquipmentContainer').get(rdf + 'resource'),
                    'description': equivalent_branch_xml.find(cim + 'IdentifiedObject.description').text
                }

        for energy_consumer_xml in root_EQ.iter(cim + 'EnergyConsumer'):
            equipment_container_ec= energy_consumer_xml.find(cim + 'Equipment.EquipmentContainer').get(rdf + 'resource').replace("#", "")
            if equipment_container_ec in matching_voltage_levels:
                energy_consumer_id = energy_consumer_xml.get(rdf + 'ID')
                energy_consumer_dict[energy_consumer_id] = {
                    'ID': energy_consumer_id,
                    'name': energy_consumer_xml.find(cim + 'IdentifiedObject.name').text,
                    'equipment_container': energy_consumer_xml.find(cim + 'Equipment.EquipmentContainer').get(rdf + 'resource'),
                    'active_power': "",
                    'reactive_power': ""
                }
            
        for energy_consumer_xml in root_SSH.iter(cim + "EnergyConsumer"):
            energy_consumer_id = energy_consumer_xml.get(rdf + 'about').replace("#", "")
            if energy_consumer_id in energy_consumer_dict:
                energy_consumer_dict[energy_consumer_id]['active_power'] = energy_consumer_xml.find(cim + "EnergyConsumer.p").text
                energy_consumer_dict[energy_consumer_id]['reactive_power'] = energy_consumer_xml.find(cim + "EnergyConsumer.q").text
        #print(energy_consumer_dict)

        for external_network_injection_xml in root_EQ.iter(cim + 'ExternalNetworkInjection'):
            equipment_container_XG = external_network_injection_xml.find(cim + 'Equipment.EquipmentContainer').get(rdf + 'resource').replace("#","")
            if equipment_container_XG in matching_voltage_levels:
                external_network_injection_id = external_network_injection_xml.get(rdf + 'ID')
                external_network_injection_dict[external_network_injection_id] = {
                    'ID': external_network_injection_id,
                    'name': external_network_injection_xml.find(cim + 'IdentifiedObject.name').text,
                    'equipment_container': external_network_injection_xml.find(cim + 'Equipment.EquipmentContainer').get(rdf + 'resource'),
                    'ik_second': external_network_injection_xml.find(cim + 'ExternalNetworkInjection.ikSecond').text,
                    'max_initial_sym_shc_current': external_network_injection_xml.find(cim + 'ExternalNetworkInjection.maxInitialSymShCCurrent').text,
                    'max_r0_to_x0_ratio': external_network_injection_xml.find(cim + 'ExternalNetworkInjection.maxR0ToX0Ratio').text,
                    'max_r1_to_x1_ratio': external_network_injection_xml.find(cim + 'ExternalNetworkInjection.maxR1ToX1Ratio').text,
                    'max_z0_to_z1_ratio': external_network_injection_xml.find(cim + 'ExternalNetworkInjection.maxZ0ToZ1Ratio').text,
                    'min_initial_sym_shc_current': external_network_injection_xml.find(cim + 'ExternalNetworkInjection.minInitialSymShCCurrent').text,
                    'min_r0_to_x0_ratio': external_network_injection_xml.find(cim + 'ExternalNetworkInjection.minR0ToX0Ratio').text,
                    'min_r1_to_x1_ratio': external_network_injection_xml.find(cim + 'ExternalNetworkInjection.minR1ToX1Ratio').text,
                    'min_z0_to_z1_ratio': external_network_injection_xml.find(cim + 'ExternalNetworkInjection.minZ0ToZ1Ratio').text,
                    'voltage_factor': external_network_injection_xml.find(cim + 'ExternalNetworkInjection.voltageFactor').text,
                    'governor_scd': external_network_injection_xml.find(cim + 'ExternalNetworkInjection.governorSCD').text,
                    'max_p': external_network_injection_xml.find(cim + 'ExternalNetworkInjection.maxP').text,
                    'min_p': external_network_injection_xml.find(cim + 'ExternalNetworkInjection.minP').text,
                    'max_q': external_network_injection_xml.find(cim + 'ExternalNetworkInjection.maxQ').text,
                    'min_q': external_network_injection_xml.find(cim + 'ExternalNetworkInjection.minQ').text,
                    'base_voltage': external_network_injection_xml.find(cim + 'ConductingEquipment.BaseVoltage').get(rdf + 'resource'),
                    'regulating_control': external_network_injection_xml.find(cim + 'RegulatingCondEq.RegulatingControl').get(rdf + 'resource'),
                    'description': external_network_injection_xml.find(cim + 'IdentifiedObject.description').text,
                    'short_name': external_network_injection_xml.find(entsoe + 'IdentifiedObject.shortName').text,
                    'energy_ident_code_eic': external_network_injection_xml.find(entsoe + 'IdentifiedObject.energyIdentCodeEic').text,
                    'aggregate': external_network_injection_xml.find(cim + 'Equipment.aggregate').text
                }
        def extract_generating_unit_data(generating_unit_xml):
            generating_unit_id = generating_unit_xml.get(rdf + 'ID')
            return {
                'ID': generating_unit_id,
                'name': generating_unit_xml.find(cim + 'IdentifiedObject.name').text,
                'initial_p': generating_unit_xml.find(cim + "GeneratingUnit.initialP").text,
                'nominal_p': generating_unit_xml.find(cim + "GeneratingUnit.nominalP").text,
                'max_operating_p': generating_unit_xml.find(cim + 'GeneratingUnit.maxOperatingP').text,
                'min_operating_p': generating_unit_xml.find(cim + 'GeneratingUnit.minOperatingP').text,
                'equipment_container': generating_unit_xml.find(cim + 'Equipment.EquipmentContainer').get(rdf + 'resource')
            }

        # Define the relevant CIM element tags for generating units
        generating_unit_tags = [
            cim + 'GeneratingUnit',
            cim + 'HydroGeneratingUnit',
            cim + 'NuclearGeneratingUnit',
            cim + 'SolarGeneratingUnit',
            cim + 'ThermalGeneratingUnit',
            cim + 'WindGeneratingUnit'
        ]

        for tag in generating_unit_tags:
            for generating_unit_xml in root_EQ.iter(tag):
                generating_unit_data = extract_generating_unit_data(generating_unit_xml)
                generating_unit_dict[generating_unit_data['ID']] = generating_unit_data
        # print(generating_unit_dict)

        if selected_mode == 1:
            for geographical_region_xml in root_EQ.iter(cim + 'GeographicalRegion'):
                geographical_region_id = geographical_region_xml.get(rdf + 'ID')
                geographical_region_dict[geographical_region_id] = {
                    'ID': geographical_region_id,
                    'name': geographical_region_xml.find(cim + 'IdentifiedObject.name').text
                }
                # print(geographical_region_dict)
            for line_xml in root_EQ.iter(cim + 'Line'):
                line_id = line_xml.get(rdf + 'ID')
                line_dict[line_id] = {
                    'ID': line_id,
                    'name': line_xml.find(cim + 'IdentifiedObject.name').text,
                    'region': line_xml.find(cim + 'Line.Region').get(rdf + 'resource')
                }
            # print(line_dict)
            for phase_tap_changer_asymmetrical_xml in root_EQ.iter(cim + 'PhaseTapChangerAsymmetrical'):
                phase_tap_changer_asymmetrical_id = phase_tap_changer_asymmetrical_xml.get(rdf + 'ID')
                phase_tap_changer_asymmetrical_dict[phase_tap_changer_asymmetrical_id] = {
                    'ID': phase_tap_changer_asymmetrical_id,
                    'name': phase_tap_changer_asymmetrical_xml.find(cim + 'IdentifiedObject.name').text,
                    'neutral_u': phase_tap_changer_asymmetrical_xml.find(cim + 'TapChanger.neutralU').text,
                    'low_step': phase_tap_changer_asymmetrical_xml.find(cim + 'TapChanger.lowStep').text,
                    'high_step': phase_tap_changer_asymmetrical_xml.find(cim + 'TapChanger.highStep').text,
                    'neutral_step': phase_tap_changer_asymmetrical_xml.find(cim + 'TapChanger.neutralStep').text,
                    'normal_step': phase_tap_changer_asymmetrical_xml.find(cim + 'TapChanger.normalStep').text,
                    'voltage_step_increment': phase_tap_changer_asymmetrical_xml.find(cim + 'PhaseTapChangerNonLinear.voltageStepIncrement').text,
                    'x_min': phase_tap_changer_asymmetrical_xml.find(cim + 'PhaseTapChangerNonLinear.xMin').text,
                    'x_max': phase_tap_changer_asymmetrical_xml.find(cim + 'PhaseTapChangerNonLinear.xMax').text,
                    'winding_connection_angle': phase_tap_changer_asymmetrical_xml.find(cim + 'PhaseTapChangerAsymmetrical.windingConnectionAngle').text,
                    'transformer_end': phase_tap_changer_asymmetrical_xml.find(cim + 'PhaseTapChanger.TransformerEnd').get(rdf + 'resource'),
                    'tap_changer_control': phase_tap_changer_asymmetrical_xml.find(cim + 'TapChanger.TapChangerControl').get(rdf + 'resource')
                }
            for current_limit_xml in root_EQ.iter(cim + "CurrentLimit"):
                current_limit_id = current_limit_xml.get(rdf + "ID")
                current_limit_dict[current_limit_id] = {
                    'ID': current_limit_id,
                    'name': current_limit_xml.find(cim + "IdentifiedObject.name").text,
                    'value': current_limit_xml.find(cim + "CurrentLimit.value").text,
                    'operational_limit_set': current_limit_xml.find(cim + "OperationalLimit.OperationalLimitSet").get(rdf + "resource"),
                    'operational_limit_type': current_limit_xml.find(cim + "OperationalLimit.OperationalLimitType").get(rdf + "resource")
                }
            # print(current_limit_dict)
            for regulating_control_xml in root_EQ.iter(cim+'RegulatingControl'):
                regulating_control_id = regulating_control_xml.get(rdf+'ID')
                regulating_control_dict[regulating_control_id] = {
                    'ID': regulating_control_id,
                    'name': regulating_control_xml.find(cim+'IdentifiedObject.name').text,
                    'mode': regulating_control_xml.find(cim+'RegulatingControl.mode').get(rdf+'resource'),
                    'terminal': regulating_control_xml.find(cim+'RegulatingControl.Terminal').get(rdf+'resource'),
                    'target_value': ""  # Initialize the target_value attribute
                }

            for regulating_control_xml in root_SSH.iter(cim+'RegulatingControl'):
                regulating_control_id = regulating_control_xml.get(rdf + 'about').replace("#", "")
                if regulating_control_id in  regulating_control_dict:
                    regulating_control_dict[regulating_control_id]['target_value'] = regulating_control_xml.find(cim+'RegulatingControl.targetValue').text

        for linear_shunt_compensator_xml in root_EQ.iter(cim + 'LinearShuntCompensator'):
            equipment_container_LSC = linear_shunt_compensator_xml.find(cim + 'Equipment.EquipmentContainer').get(rdf + 'resource').replace("#","")
            if equipment_container_LSC in matching_voltage_levels:
                linear_shunt_compensator_id = linear_shunt_compensator_xml.get(rdf + 'ID')
                linear_shunt_compensator_dict[linear_shunt_compensator_id] = {
                    'ID': linear_shunt_compensator_id,
                    'name': linear_shunt_compensator_xml.find(cim + 'IdentifiedObject.name').text,
                    'b_per_section': linear_shunt_compensator_xml.find(cim + 'LinearShuntCompensator.bPerSection').text,
                    'g_per_section': linear_shunt_compensator_xml.find(cim + 'LinearShuntCompensator.gPerSection').text,
                    'b0_per_section': linear_shunt_compensator_xml.find(cim + 'LinearShuntCompensator.b0PerSection').text,
                    'g0_per_section': linear_shunt_compensator_xml.find(cim + 'LinearShuntCompensator.g0PerSection').text,
                    'nom_u': linear_shunt_compensator_xml.find(cim + 'ShuntCompensator.nomU').text,
                    'regulating_control': linear_shunt_compensator_xml.find(cim + 'RegulatingCondEq.RegulatingControl').get(rdf + 'resource'),
                    'equipment_container': linear_shunt_compensator_xml.find(cim + 'Equipment.EquipmentContainer').get(rdf + 'resource'),
                    'q_mvar_sh': ''
                }

        for petersen_coil_xml in root_EQ.iter(cim + 'PetersenCoil'):
            equipment_container_PC = petersen_coil_xml.find(cim + 'Equipment.EquipmentContainer').get(rdf + 'resource').replace("#","")
            if equipment_container_PC in matching_voltage_levels:
                petersen_coil_id = petersen_coil_xml.get(rdf + 'ID')
                petersen_coil_dict[petersen_coil_id] = {
                    'ID': petersen_coil_id,
                    'name': petersen_coil_xml.find(cim + 'IdentifiedObject.name').text,
                    'equipment_container': petersen_coil_xml.find(cim + 'Equipment.EquipmentContainer').get(rdf + 'resource'),
                    'x_ground_nominal': petersen_coil_xml.find(cim + 'PetersenCoil.xGroundNominal').text,
                    'x_ground_max': petersen_coil_xml.find(cim + 'PetersenCoil.xGroundMax').text,
                    'x_ground_min': petersen_coil_xml.find(cim + 'PetersenCoil.xGroundMin').text,
                    'position_current': petersen_coil_xml.find(cim + 'PetersenCoil.positionCurrent').text,
                    'offset_current': petersen_coil_xml.find(cim + 'PetersenCoil.offsetCurrent').text,
                    'nominal_u': petersen_coil_xml.find(cim + 'PetersenCoil.nominalU').text,
                    'mode': petersen_coil_xml.find(cim + 'PetersenCoil.mode').get(rdf + 'resource')
                }

        matching_transformers=[]
        for power_transformer_xml in root_EQ.iter(cim+'PowerTransformer'):
            power_transformer_id = power_transformer_xml.get(rdf+'ID')
            if power_transformer_id in matching_elements: 
                matching_transformers.append(power_transformer_id)
                power_transformer_dict[power_transformer_id] = {
                    'ID': power_transformer_id,
                    'name': power_transformer_xml.find(cim+'IdentifiedObject.name').text,
                    'equipment_container': power_transformer_xml.find(cim+'Equipment.EquipmentContainer').get(rdf+'resource')
                }

        for power_transformer_end_xml in root_EQ.iter(cim+'PowerTransformerEnd'):
            power_tranfo=power_transformer_end_xml.find(cim+'PowerTransformerEnd.PowerTransformer').get(rdf+'resource').replace("#", "")
            if power_tranfo in matching_transformers:
                power_transformer_end_id = power_transformer_end_xml.get(rdf+'ID')
                power_transformer_end_dict[power_transformer_end_id] = {
                    'ID': power_transformer_end_id,
                    'name': power_transformer_end_xml.find(cim+'IdentifiedObject.name').text,
                    'r': power_transformer_end_xml.find(cim+'PowerTransformerEnd.r').text,
                    'x': power_transformer_end_xml.find(cim+'PowerTransformerEnd.x').text,
                    'b': power_transformer_end_xml.find(cim+'PowerTransformerEnd.b').text,
                    'g': power_transformer_end_xml.find(cim+'PowerTransformerEnd.g').text,
                    'r0': power_transformer_end_xml.find(cim+'PowerTransformerEnd.r0').text,
                    'x0': power_transformer_end_xml.find(cim+'PowerTransformerEnd.x0').text,
                    'b0': power_transformer_end_xml.find(cim+'PowerTransformerEnd.b0').text,
                    'g0': power_transformer_end_xml.find(cim+'PowerTransformerEnd.g0').text,
                    'rground': power_transformer_end_xml.find(cim+'TransformerEnd.rground').text,
                    'xground': power_transformer_end_xml.find(cim+'TransformerEnd.xground').text,
                    'rated_s': power_transformer_end_xml.find(cim+'PowerTransformerEnd.ratedS').text,
                    'rated_u': power_transformer_end_xml.find(cim+'PowerTransformerEnd.ratedU').text,
                    'phase_angle_clock': power_transformer_end_xml.find(cim+'PowerTransformerEnd.phaseAngleClock').text,
                    'connection_kind': power_transformer_end_xml.find(cim+'PowerTransformerEnd.connectionKind').get(rdf+'resource'),
                    'base_voltage': power_transformer_end_xml.find(cim+'TransformerEnd.BaseVoltage').get(rdf+'resource'),
                    'power_transformer': power_transformer_end_xml.find(cim+'PowerTransformerEnd.PowerTransformer').get(rdf+'resource'),
                    'terminal': power_transformer_end_xml.find(cim+'TransformerEnd.Terminal').get(rdf+'resource')
                }

        for ratio_tap_changer_xml in root_EQ.iter(cim+'RatioTapChanger'):
            ratio_tap_changer_id = ratio_tap_changer_xml.get(rdf+'ID')
            ratio_tap_changer_dict[ratio_tap_changer_id] = {
                'ID': ratio_tap_changer_id,
                'name': ratio_tap_changer_xml.find(cim+'IdentifiedObject.name').text,
                'transformer_end': ratio_tap_changer_xml.find(cim+'RatioTapChanger.TransformerEnd').get(rdf+'resource'),
                'step': ""
            }
            
        for ratio_tap_changer_xml in root_SSH.iter(cim+'RatioTapChanger'):
            ratio_tap_changer_id = ratio_tap_changer_xml.get(rdf + 'about').replace("#", "")
            if ratio_tap_changer_id in ratio_tap_changer_dict:
                ratio_tap_changer_dict[ratio_tap_changer_id]['step'] = ratio_tap_changer_xml.find(cim+'TapChanger.step').text        
            
        for series_compensator_xml in root_EQ.iter(cim + 'SeriesCompensator'):
            equipment_container_sc= series_compensator_xml.find(cim + 'Equipment.EquipmentContainer').get(rdf + 'resource').replace("#", "")
            if equipment_container_sc in matching_voltage_levels:
                series_compensator_id = series_compensator_xml.get(rdf + 'ID')
                series_compensator_dict[series_compensator_id] = {
                    'ID': series_compensator_id,
                    'name': series_compensator_xml.find(cim + 'IdentifiedObject.name').text,
                    'equipment_container': series_compensator_xml.find(cim + 'Equipment.EquipmentContainer').get(rdf + 'resource'),
                    'base_voltage': series_compensator_xml.find(cim + 'ConductingEquipment.BaseVoltage').get(rdf + 'resource'),
                    'r': float(series_compensator_xml.find(cim + 'SeriesCompensator.r').text),
                    'x': float(series_compensator_xml.find(cim + 'SeriesCompensator.x').text),
                    'varistor_present': series_compensator_xml.find(cim + 'SeriesCompensator.varistorPresent').text,
                    'varistor_rated_current': float(series_compensator_xml.find(cim + 'SeriesCompensator.varistorRatedCurrent').text),
                    'varistor_voltage_threshold': float(series_compensator_xml.find(cim + 'SeriesCompensator.varistorVoltageThreshold').text),
                    'r0': float(series_compensator_xml.find(cim + 'SeriesCompensator.r0').text),
                    'x0': float(series_compensator_xml.find(cim + 'SeriesCompensator.x0').text),
                    'description': series_compensator_xml.find(cim + 'IdentifiedObject.description').text,
                    'mRID': series_compensator_xml.find(cim + 'IdentifiedObject.mRID').text,
                }

        for synchronous_machine_xml in root_EQ.iter(cim+'SynchronousMachine'):
            equipment_container_SM = synchronous_machine_xml.find(cim+'Equipment.EquipmentContainer').get(rdf+'resource').replace("#","")
            if equipment_container_SM in matching_voltage_levels:
                synchronous_machine_id = synchronous_machine_xml.get(rdf+'ID')
                synchronous_machine_dict[synchronous_machine_id] = {
                    'ID': synchronous_machine_id,
                    'name': synchronous_machine_xml.find(cim+'IdentifiedObject.name').text,
                    'equipment_container': synchronous_machine_xml.find(cim+'Equipment.EquipmentContainer').get(rdf+'resource'),
                    'regulating_control': synchronous_machine_xml.find(cim+'RegulatingCondEq.RegulatingControl').get(rdf+'resource'),
                    'generating_unit': synchronous_machine_xml.find(cim+'RotatingMachine.GeneratingUnit').get(rdf+'resource'),
                    'active_power': "",
                    'reactive_power': ""  # Initialize the active_power and reactive_power attributes
                }

        for synchronous_machine_xml in root_SSH.iter(cim+'SynchronousMachine'):
            synchronous_machine_id = synchronous_machine_xml.get(rdf + 'about').replace("#", "")
            if synchronous_machine_id in synchronous_machine_dict:
                synchronous_machine_dict[synchronous_machine_id]['active_power'] = synchronous_machine_xml.find(cim+'RotatingMachine.p').text
                synchronous_machine_dict[synchronous_machine_id]['reactive_power'] = synchronous_machine_xml.find(cim+'RotatingMachine.q').text
            
        for tap_changer_control_xml in root_EQ.iter(cim+"TapChangerControl"):
            tap_changer_control_id = tap_changer_control_xml.get(rdf+"ID")
            tap_changer_control_dict[tap_changer_control_id] = {
                'ID': tap_changer_control_id,
                'name': tap_changer_control_xml.find(cim+'IdentifiedObject.name').text,
                'mode': tap_changer_control_xml.find(cim+"RegulatingControl.mode").text,
                'terminal': tap_changer_control_xml.find(cim+"RegulatingControl.Terminal").get(rdf+"resource")
            }

        for voltage_level_xml in root_EQ.iter(cim+'VoltageLevel'):
            voltage_level_id = voltage_level_xml.get(rdf+'ID')
            voltage_level_dict[voltage_level_id] = {
                'ID': voltage_level_id,
                'name': voltage_level_xml.find(cim+'IdentifiedObject.name').text,
                'substation': voltage_level_xml.find(cim+'VoltageLevel.Substation').get(rdf+'resource'),
                'base_voltage': voltage_level_xml.find(cim+'VoltageLevel.BaseVoltage').get(rdf+'resource')
            }    

        for terminal_xml in root_EQ.iter(cim+'Terminal'):
            terminal_id = terminal_xml.get(rdf+'ID')
            terminal_dict[terminal_id] = {
                'ID': terminal_id,
                'name': terminal_xml.find(cim+'IdentifiedObject.name').text,
                'conducting_equipment': terminal_xml.find(cim+'Terminal.ConductingEquipment').get(rdf+'resource'),
                'connectivity_node': terminal_xml.find(cim+'Terminal.ConnectivityNode').get(rdf+'resource')
            }
        #print(terminal_dict)


        """
        This part creates nested lists for each component filled with the required data for Panda Power 
        """
        # Check for missing ConnectivityNodes and forming function to find the busbar type
        if selected_mode == 1:
            for terminal_id, terminal_data in terminal_dict.items():
                connectivity_node_id = terminal_data['connectivity_node'].replace("#", "")
                
                if connectivity_node_id not in connectivity_node_dict:
                    # If the ConnectivityNode is missing, add it
                    missing_node_name = f"MissingNode_{len(connectivity_node_dict) + 1}"
                    connectivity_node_dict[connectivity_node_id] = {
                        'ID': connectivity_node_id,
                        'name': missing_node_name,
                        'connectivity_node_container': "#"
                    }


        def find_busbar(node_ID):
            for terminal_id, terminal_data in terminal_dict.items():
                if '#' + node_ID == terminal_data['connectivity_node']:
                    for busbar_id, busbar_data in busbar_section_dict.items():
                        if terminal_data['conducting_equipment'] == '#' + busbar_data['ID']:
                            return 'b'
            return 'n'        

        #indexing all the keys present
        terminal_keys_list = ['#' + key for key in terminal_dict.keys()]
        connectivity_node_keys_list = ['#' + key for key in connectivity_node_dict.keys()]
        #print(connectivity_node_keys_list)
        #print(len(connectivity_node_keys_list))
        terminal_dic = {}
        for i in range(len(terminal_keys_list)):
            terminal_dic[terminal_keys_list[i]] = i    
        connectivity_node_dic = {}
        for i in range(len(connectivity_node_keys_list)):
            connectivity_node_dic[connectivity_node_keys_list[i]] = i
        #print(connectivity_node_dic)
        connectivity_node = [[0 for i in range(5)] for j in range(len(connectivity_node_dict))]

        for i, (node_id, node_data) in enumerate(connectivity_node_dict.items()):
            connectivity_node[i][0] = node_data['name']
            connectivity_node[i][3] = node_data['connectivity_node_container'].replace("#", "")
            connectivity_node[i][4] = node_data['ID']
            try:
                voltage_level_name = voltage_level_dict[node_data['connectivity_node_container'].replace("#", "")]['name']
                connectivity_node[i][1] = float(voltage_level_name)
                connectivity_node[i][2] = find_busbar(node_id)
            except KeyError:
                # If the connectivity_node_container is a Bay, extract voltage_level from Bay
                bay_id = node_data['connectivity_node_container'].replace("#", "")
                # Check if the bay_id exists in bay_dict
                if bay_id in bay_dict:
                    voltage_level_id_from_bay = bay_dict[bay_id]['voltage_level'].replace("#", "")
                    # Check if 'voltage_level' exists in the bay_dict entry
                    voltage_level_name_from_bay = voltage_level_dict[voltage_level_id_from_bay]['name']
                    # Set values in connectivity_node
                    connectivity_node[i][1] = float(voltage_level_name_from_bay)
                    connectivity_node[i][2] = find_busbar(node_id)
                else:
                    # Handle the case when bay_id doesn't exist in bay_dict
                    connectivity_node[i][1] = 'nan'
                    connectivity_node[i][2] = find_busbar(node_id)
            except Exception as e:
                # Handle other exceptions
                print(f"An unexpected error occurred: {e}")
                # Set values in connectivity_node for 'nan'
                connectivity_node[i][1] = 'nan'
                connectivity_node[i][2] = find_busbar(node_id)
            
        power_transformer = [[0 for i in range(10)] for j in range(len(power_transformer_dict))]

        for i, (pt_id, pt_data) in enumerate(power_transformer_dict.items()):
            power_transformer[i][0] = pt_data['name']
            power_transformer[i][7] = 'two_winding'
            power_transformer[i][8] = pt_data['ID']
            power_transformer[i][9] = pt_data['equipment_container'].replace("#", "")
            t_i = []
            vl_i = []
            cn_i = []

            for pt_end_id, pt_end_data in power_transformer_end_dict.items():
                if '#'+ pt_data['ID'] == pt_end_data['power_transformer']:
                    t_i.append(terminal_keys_list.index(pt_end_data['terminal']))
                    cn_i.append(connectivity_node_keys_list.index(terminal_dict[terminal_keys_list[t_i[-1]].replace("#", "")]['connectivity_node']))
                    vl_i.append(connectivity_node[cn_i[-1]][1])

            # print(cn_i)
            # print(vl_i)
            min_vl_ind = vl_i.index(min(vl_i))
            max_vl_ind = vl_i.index(max(vl_i))
            power_transformer[i][1] = cn_i[min_vl_ind]
            power_transformer[i][4] = vl_i[min_vl_ind]
            power_transformer[i][3] = cn_i[max_vl_ind]
            power_transformer[i][6] = vl_i[max_vl_ind]

            if len(vl_i) == 3:
                power_transformer[i][2] = cn_i[3 - (min_vl_ind + max_vl_ind)]
                power_transformer[i][5] = vl_i[3 - (min_vl_ind + max_vl_ind)]
                power_transformer[i][7] = 'three_winding'

        AC_line_segment = [[0 for i in range(6)] for j in range(len(ac_line_segments_dict))]

        for i, (ac_line_segment_id,ac_line_segment_data) in enumerate(ac_line_segments_dict.items()):
            AC_line_segment[i][0] = ac_line_segment_data['name']
            AC_line_segment[i][3] = float(ac_line_segment_data['length'])
            AC_line_segment[i][4] = ac_line_segment_data['ID']
            AC_line_segment[i][5] = ac_line_segment_data['equipment_container'].replace("#", "")
            count = 0
            for terminal_key in terminal_dict.keys():
                if '#' + ac_line_segment_data['ID'] == terminal_dict[terminal_key]['conducting_equipment']:
                    count += 1
                    if count == 1:
                        AC_line_segment[i][1] = connectivity_node_keys_list.index(terminal_dict[terminal_key]['connectivity_node'])
                    else:
                        AC_line_segment[i][2] = connectivity_node_keys_list.index(terminal_dict[terminal_key]['connectivity_node'])

        #print(AC_line_segment)
        equivalent_branches = [[0 for i in range(7)] for j in range(len(equivalent_branch_dict))]

        for i, (branch_id, branch_data) in enumerate(equivalent_branch_dict.items()):
            equivalent_branches[i][0] = branch_data['name']
            equivalent_branches[i][5] = branch_data['ID']
            equivalent_branches[i][6] = branch_data['equipment_container'].replace("#", "")
            
            count = 0
            for terminal_key in terminal_dict.keys():
                if '#' + branch_data['ID'] == terminal_dict[terminal_key]['conducting_equipment']:
                    count += 1
                    if count == 1:
                        equivalent_branches[i][1] = connectivity_node_keys_list.index(terminal_dict[terminal_key]['connectivity_node'])
                    else:
                        equivalent_branches[i][2] = connectivity_node_keys_list.index(terminal_dict[terminal_key]['connectivity_node'])            
            equivalent_branches[i][3] = float(branch_data['r'])  # Assuming 'r' is a float value
            equivalent_branches[i][4] = float(branch_data['x'])  # Assuming 'x' is a float value
         
        energy_consumer = [[0 for i in range(6)] for j in range(len(energy_consumer_dict))]

        for i, (energy_consumer_id, energy_consumer_data) in enumerate(energy_consumer_dict.items()):
            energy_consumer[i][0] = energy_consumer_data['name']
            energy_consumer[i][2] = float(energy_consumer_data['active_power'])
            energy_consumer[i][3] = float(energy_consumer_data['reactive_power'])
            energy_consumer[i][4] = energy_consumer_data['equipment_container'].replace("#", "")
            energy_consumer[i][5] = energy_consumer_data['ID']

            for terminal_key in terminal_dict.keys():
                if '#' + energy_consumer_data['ID'] == terminal_dict[terminal_key]['conducting_equipment']:
                    energy_consumer[i][1] = connectivity_node_keys_list.index(terminal_dict[terminal_key]['connectivity_node'])
        #print(energy_consumer)

        external_network_injection = [[0 for i in range(8)] for j in range(len(external_network_injection_dict))]

        for i, (external_network_injection_id, external_network_injection_data) in enumerate(external_network_injection_dict.items()):
            external_network_injection[i][0] = external_network_injection_data['name']
            external_network_injection[i][6] = external_network_injection_data['equipment_container'].replace("#", "")
            external_network_injection[i][7] = external_network_injection_data['ID']
            
            
            
            # Assuming you have 'connectivity_node' information for ExternalNetworkInjection
            for terminal_key in terminal_dict.keys():
                if '#' + external_network_injection_data['ID'] == terminal_dict[terminal_key]['conducting_equipment']:
                    external_network_injection[i][1] = connectivity_node_keys_list.index(terminal_dict[terminal_key]['connectivity_node'])
                    break
            else:
                external_network_injection[i][1] = None  # Handle the case where connectivity_node is not found

            external_network_injection[i][2] = float(external_network_injection_data.get('max_p', 0)) 
            external_network_injection[i][3] = float(external_network_injection_data.get('max_q', 0))  
            external_network_injection[i][4] = float(external_network_injection_data.get('maxR0ToX0Ratio', 0)) 
            external_network_injection[i][5] = float(external_network_injection_data.get('minR0ToX0Ratio', 0))
            
        generating_unit = [[0 for i in range(5)] for j in range(len(generating_unit_dict))]

        for i, (generating_unit_id, generating_unit_data) in enumerate(generating_unit_dict.items()):
            generating_unit[i][0] = generating_unit_data['name']
            generating_unit[i][2] = float(generating_unit_data['nominal_p'])
            generating_unit[i][3] = generating_unit_data['ID']
            generating_unit[i][4] = generating_unit_data['equipment_container'].replace("#", "")
            
            for synchronous_machine_id, synchronous_machine_data in synchronous_machine_dict.items():
                if '#' + generating_unit_data['ID'] == synchronous_machine_data['generating_unit']:
                    
                    for terminal_key, terminal_data in terminal_dict.items():
                        if '#' + synchronous_machine_data['ID'] == terminal_dict[terminal_key]['conducting_equipment']:
                            generating_unit[i][1] = connectivity_node_keys_list.index(terminal_dict[terminal_key]['connectivity_node'])
                            break

        series_compensators = [[0 for i in range(8)] for j in range(len(series_compensator_dict))]

        for i, (compensator_id, compensator_data) in enumerate(series_compensator_dict.items()):
            series_compensators[i][0] = compensator_data['name']
            series_compensators[i][6] = compensator_data['equipment_container'].replace("#", "")
            series_compensators[i][7] = compensator_data['ID']
            count = 0
            for terminal_key in terminal_dict.keys():
                if '#' + compensator_data['ID'] == terminal_dict[terminal_key]['conducting_equipment']:
                    count += 1
                    if count == 1:
                        series_compensators[i][1] = connectivity_node_keys_list.index(terminal_dict[terminal_key]['connectivity_node'])
                    else:
                        series_compensators[i][2] = connectivity_node_keys_list.index(terminal_dict[terminal_key]['connectivity_node'])
                        
            series_compensators[i][3] = float(compensator_data['r'])  # Assuming 'r' is a float value
            series_compensators[i][4] = float(compensator_data['x'])  # Assuming 'x' is a float value
            
            # Calculate the value for series_compensators[i][5] by multiplying rated current and r
            series_compensators[i][5] = float(compensator_data['varistor_rated_current']) * series_compensators[i][3]    

        switches = [[0 for i in range(7)] for j in range(len(common_switch_dict))]

        for i, (switch_id, switch_data) in enumerate(common_switch_dict.items()):
            switches[i][0] = switch_data['name']
            switches[i][4] = switch_data['type']
            switches[i][5] = switch_data['equipment_container'].replace("#", "")
            switches[i][6] = switch_data['ID']
            if switch_data['status'] == 'false':
                switches[i][3] = True
            count = 0
            for terminal_key in terminal_dict.keys():
                if '#' + switch_data['ID'] == terminal_dict[terminal_key]['conducting_equipment']:
                    count += 1
                    if count == 1:
                        switches[i][1] = connectivity_node_keys_list.index(terminal_dict[terminal_key]['connectivity_node'])
                    else:
                        switches[i][2] = connectivity_node_keys_list.index(terminal_dict[terminal_key]['connectivity_node'])

        synchronous_machine = [[0 for i in range(5)] for j in range(len(synchronous_machine_dict))]

        for i, (synchronous_machine_id, synchronous_machine_data) in enumerate(synchronous_machine_dict.items()):
            synchronous_machine[i][0] = synchronous_machine_data['name']
            synchronous_machine[i][2] = float(synchronous_machine_data['active_power'])
            synchronous_machine[i][3] = synchronous_machine_data['equipment_container'].replace("#", "")
            synchronous_machine[i][4] = synchronous_machine_data['ID']
            
            for terminal_key in terminal_dict.keys():
                if '#' + synchronous_machine_data['ID'] == terminal_dict[terminal_key]['conducting_equipment']:
                    synchronous_machine[i][1] = connectivity_node_keys_list.index(terminal_dict[terminal_key]['connectivity_node'])

        linear_shunt_compensator = [[0 for i in range(5)] for j in range(len(linear_shunt_compensator_dict))]

        for i, (linear_shunt_compensator_id, linear_shunt_compensator_data) in enumerate(linear_shunt_compensator_dict.items()):
            linear_shunt_compensator[i][0] = linear_shunt_compensator_data['name']
            linear_shunt_compensator[i][2] = linear_shunt_compensator_data['equipment_container'].replace("#", "")
            linear_shunt_compensator[i][4] = linear_shunt_compensator_data['ID']
            # reactive_power = float(voltage)**2 * float(susceptance)
            linear_shunt_compensator[i][3] = float(linear_shunt_compensator_data['nom_u'])**2 * float(linear_shunt_compensator_data['b_per_section'])
            
            for terminal_key in terminal_dict.keys():
                if '#' + linear_shunt_compensator_data['ID'] == terminal_dict[terminal_key]['conducting_equipment']:
                    linear_shunt_compensator[i][1] = connectivity_node_keys_list.index(terminal_dict[terminal_key]['connectivity_node'])

        #Panda power modelling
        net = pp.create_empty_network()

        #Busbars
        for i in range (len(connectivity_node_dict)):
            pp.create_bus (net, name=connectivity_node[i][0], vn_kv=connectivity_node[i][1], type = connectivity_node[i][2])
         
        #Lines
        for i in range (len(ac_line_segments_dict)):
            pp.create_line(net, AC_line_segment[i][1], AC_line_segment[i][2], length_km = AC_line_segment[i][3], std_type = "N2XS(FL)2Y 1x300 RM/35 64/110 kV",  name = AC_line_segment[i][0])

        #switches
        for i in range(len(common_switch_dict)):
            pp.create_switch(net, switches[i][1], switches[i][2], et="b", type = ["CB" if switches[i][4] == 'Breaker' else "DS" if switches[i][4] == 'Disconnector' else "LS"], closed=switches[i][3])


        #Transformers
        for i in range (len(power_transformer_dict)):
            if power_transformer[i][7] == 'two_winding':
                pp.create_transformer (net, power_transformer[i][3], power_transformer[i][1], name = power_transformer[i][0], std_type="25 MVA 110/20 kV")
            if power_transformer[i][7] == 'three_winding':
                pp.create.create_transformer3w (net, power_transformer[i][3], power_transformer[i][2], power_transformer[i][1], name = power_transformer[i][0], std_type="63/25/38 MVA 110/20/10 kV")

        #Load
        for i in range (len(energy_consumer_dict)):
            pp.create_load(net, energy_consumer[i][1], p_mw = energy_consumer[i][2], q_mvar = energy_consumer[i][3], name = energy_consumer[i][0])

        for i in range (len(series_compensator_dict)):
            pp.create_impedance(net, series_compensators[i][1], series_compensators[i][2], series_compensators[i][3], series_compensators[i][4], sn_mva=series_compensators[i][5])

        for i in range(len(equivalent_branch_dict)):
            pp.create_impedance(net, equivalent_branches[i][1], equivalent_branches[i][2], equivalent_branches[i][3], equivalent_branches[i][4], 100)

        #Generator 
        for i in range (len(generating_unit_dict)):
            pp.create_gen(net, generating_unit[i][1], p_mw = generating_unit[i][2], name = generating_unit[i][0])

        #for i in range (len(synchronous_machine_list)):
            #pp.create_sgen(net, synchronous_machine[i][1], p_mw = synchronous_machine[i][2], name = synchronous_machine[i][0])

        for i in range(len(linear_shunt_compensator_dict)):
            pp.create.create_shunt(net, linear_shunt_compensator[i][1], q_mvar=linear_shunt_compensator[i][3] , p_mw=0,  name=linear_shunt_compensator[i][0])    

        for i in range(len(external_network_injection_dict)):
            pandapower.create.create_ext_grid(net, external_network_injection[i][1], vm_pu=1.0, va_degree=0.0, name=external_network_injection[i][0], 
                                              in_service=True, rx_max=external_network_injection[i][4], rx_min=external_network_injection[i][5], max_p_mw=external_network_injection[i][2], max_q_mvar=external_network_injection[i][3])

        #pp.plotting.simple_plot(net)
        #pandapower.plotting.plotly.traces.create_bus_trace(net, buses=None, size=5, patch_type='Square', color='red', infofunc=None, trace_name='buses', legendgroup=None, cmap=None, cmap_vals=None, cbar_title=None, cmin=None, cmax=None, cpos=1.0, colormap_column='vm_pu')
        pp.plotting.create_generic_coordinates(net, mg=None, library='igraph', respect_switches=True, geodata_table='bus_geodata', buses=None, overwrite=True)

        if selected_mode == 1:
            pp.plotting.simple_plot(net, respect_switches=True, line_width=1.0, bus_size=1.0, ext_grid_size=1.0, trafo_size=1.0, plot_loads=True, plot_gens=True, 
                                    plot_sgens=True, load_size=1.0, gen_size=2.0, sgen_size=1.0, switch_size=1.0, switch_distance=1.0, plot_line_switches=True, scale_size=True, 
                                    bus_color=['red' if net.bus.at[i, 'type'] == 'b' else 'blue' for i in net.bus.index], line_color='grey', 
                                    dcline_color='c', trafo_color='k', ext_grid_color='y', switch_color='k', library='igraph', show_plot=True, ax=None)
            html_output(net, 'Full AC Grid.html')
            html_file_path = 'Full AC Grid.html'
            print(net)
        else:
            pp.plotting.simple_plot(net, respect_switches=True, line_width=1.0, bus_size=1.0, ext_grid_size=1.0, trafo_size=1.0, plot_loads=True, plot_gens=True, 
                                    plot_sgens=True, load_size=1.0, gen_size=2.0, sgen_size=1.0, switch_size=1.0, switch_distance=1.0, plot_line_switches=True, scale_size=True, 
                                    bus_color=['red' if net.bus.at[i, 'type'] == 'b' else 'blue' for i in net.bus.index], line_color='grey', 
                                    dcline_color='c', trafo_color='k', ext_grid_color='y', switch_color='k', library='igraph', show_plot=False, ax=None)
            html_output(net, 'PP_Brussels Topology.html')
            html_file_path = 'PP_Brussels Topology.html'
            print(net)
            if len(net.bus) == 1:
                Topology = ("Only Single Bus Topology")
            elif all(len(net.switch[(net.switch.bus == bus)]) <= 1 for bus in net.bus.index):
                Topology = ("Single Bus Topology and Sectionalized Bus Topology")
            elif any(len(net.switch[(net.switch.bus == bus)]) > 1 for bus in net.bus.index):
                Topology = ("Single Bus Topology and Main and Transfer Bus Topology")
            elif any(len(net.switch[(net.switch.bus == bus)]) > 2 for bus in net.bus.index):
                Topology = ("Single Bus Topology, Main and Transfer Bus Topology and Double Breaker Topology")
            elif any(len(net.switch[(net.switch.bus == bus)])== 2 for bus in net.bus.index):
                Topology = ("Breaker-and-a-Half Topology")

            # Add the rectangle
            rect = patches.Rectangle((-2, -2.9), 6.5, 5.1, linewidth=1, edgecolor='r', facecolor='none')
            plt.gca().add_patch(rect)
            text_x = -2 + 7 / 2
            text_y = -3 + 10.5 / 2
            plt.text(text_x, text_y, Topology , horizontalalignment='center', verticalalignment='bottom')
            plt.show()
            
            #finding all the present topologies of the grid   
            def is_single_bus_topology(net, bus_id):
                # Check if all elements connected to this bus are not connected to any other bus
                for line in net.line.itertuples():
                    if (line.from_bus == bus_id or line.to_bus == bus_id) and (line.from_bus != line.to_bus):
                        return False
                for transformer in net.trafo.itertuples():
                    if (transformer.hv_bus == bus_id or transformer.lv_bus == bus_id) and (transformer.hv_bus != transformer.lv_bus):
                        return False
                for load in net.load.itertuples():
                    if load.bus == bus_id:
                        return False
            
                for gen in net.gen.itertuples():
                    if gen.bus == bus_id:
                        return False
            
                for shunt in net.shunt.itertuples():
                    if shunt.bus == bus_id:
                        return False
                return True
            
            def find_single_bus_topologies(net):
                single_bus_systems = []
                for bus_id in net.bus.index:
                    if is_single_bus_topology(net, bus_id):
                        single_bus_systems.append(bus_id)
                return single_bus_systems
            
            # Now check for single bus topologies
            single_bus_systems = find_single_bus_topologies(net)
            if single_bus_systems:
                print("Single bus topologies found at buses:", single_bus_systems)
            else:
                print("No single bus topologies found.")
        
        # Open the HTML file in the default web browser
        webbrowser.open(html_file_path)
        # After running the model and generating plots the output is stored in HTML format
        print("Model Run Successful and the result is stored in " + html_file_path)
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Model Run Successful: HTML File opened in the default web browser")
        msg.setWindowTitle("Model Run Status")
        msg.exec_()
        
        # Show a message box asking the user if they want to open the file
        #     msg = QMessageBox()
        #     msg.setIcon(QMessageBox.Information)
        #     msg.setText("Model Run Successful. Do you want to open the HTML file?")
        #     msg.setWindowTitle("Open File")
        #     msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        #     response = msg.exec_()
    
        #     if response == QMessageBox.Yes:
        #         self.open_html_file()
    
        # def open_html_file(self):
        #     # Get the current working directory
        #     cwd = os.getcwd()
        #     html_file_path = os.path.join(cwd, 'power_system_model_test_3.html')       

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())




