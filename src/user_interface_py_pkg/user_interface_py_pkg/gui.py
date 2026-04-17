################################
# gui.py
# Part of the user_interface_py_pkg
#
# Author: Nathan Horder (nathan.horder.700@cranfield.ac.uk)
# Part of Cranfield University MSC Robotics Group Project 2025-2026
################################

#%%
# Imports!
import rclpy
import holoviews as hv
import panel as pn 
import pandas as pd
import threading
from action_handler import ActionHandler
from node_handler import NodeHandler
from gui_helper import GUIHelper
from panel import pane as pnp
from panel import layout as pnl
from panel import widgets as pnw
pn.extension(notifications=True)
pn.extension('terminal')
hv.extension('bokeh')

"""
# GUI
# Main class of the user_interface_py_pkg, handles the display of the user interface
# Main function: RunApp - starting point for creation
    Arguments: N/A
    Returns: 
        Servable application dashboard - can be made visible programically or via command line
"""
class GUI():
    
    def __init__(self,dev_mode=False):

        dev_mode = dev_mode

        """Initialisation function. Prepares Interface for screen creation"""
        # Set button style - will affect all buttons in the UI
        self.styles = {}
        self.styles['buttons'] = ['primary','outline']
        self.styles['areas'] = {"border": "2px solid lightgray"}
        self.styles['markdown_text_title'] = {'font-size': '12pt'}
        self.styles['markdown_text_reg'] = {'font-size': '10pt'}
        self.styles['emergency_command'] = "4em"
        self.styles['command'] = '2em'

        # Set intial - prevents automatic firing of binded functions
        self.inital = True

        # Establish link to node handler
        self.node_handler = NodeHandler(dev_mode)

        # Spin node_handler on a separate thread (means main thread is not blocked)
        self.daemon_thread = threading.Thread(target=self.node_handler.Spin,daemon=True)
        self.daemon_thread.start()

        self.action_handler = ActionHandler(self.styles,dev_mode)
        self.helper = GUIHelper(self,self.node_handler,self.action_handler,self.styles,dev_mode)

        # Define pages
        self.pages = {}

        pn.state.add_periodic_callback(self._PublishActiveAction,500)

    def RunApp(self):
        """
        RunApp (Public)
        Starting point of the GUI class, prepares the user interface for presentation

        Arguments: N/A

        Returns:
            - pn.template.VanillaTemplate: app
        """
        # Create graphics
        self._CreateGraphics()

        # Organise screens
        self._OrganiseHomeScreen()
        self._OrganiseMotionScreen()
        self._OrganiseActionScreen()
        self._OrganiseLoggingScreen()
        side_bar = self._OrganiseSideBar()

        # Bind the function "_ChangePage" to the radio button group in the sidebar
        # Enabled operators to change main page content
        main_content = pn.bind(self._ChangePage,value=side_bar[4])

        # Disable intial
        # Initial is present as all triggerable functions are triggered once during creation to ensure
        # connection is created correctly, self.intial is used to stop any output from these - until app is deployed
        self.inital = False

        # Create app using VanillaTemplate - alternate templates may affect visual elements
        app = pn.template.VanillaTemplate(
            title = "V.I.S.N.A.T: Monitoring GUI",
            main = [main_content],
            sidebar = side_bar,
            collapsed_sidebar = True, # Have the sidebar start collapsed
        )

        # Start timers on load, starting the periodic callbacks
        pn.state.onload(self.helper.StartTimers)

        return app
    
    def _CreateGraphics(self):
        """
        _CreateGraphics (Private)
        Create static graphics and call helper to generate dynamic graphics

        Arguments N/A

        Returns: N/A
        - Enables self.helper_graphics to be availble: Dict, contains all dynamic graphics
        """

        # Call the helper to create the graphics
        self.helper_graphics = self.helper.CreateGraphics()


        self.motion_plan = pn.Column(self.helper_graphics['Lidar'],pnp.Markdown("Mobile Base: No Path Planned",styles=self.styles['markdown_text_title'],align='center'),sizing_mode='stretch_both')

        # Battery and paint levels are fixed for the time being, due to simulation
        self.battery_progress = pn.indicators.Progress(name='Battery Level',active=True,sizing_mode='stretch_width',bar_color='success',align='center')
        self.battery_progress.value = -1

        self.paint_indicator = pn.indicators.LinearGauge(name='Paint Levels',value=2.6,format='{value:.1f} kg',bounds=(0.7,25.4),colors=['red','gold','green'],horizontal=True,sizing_mode='stretch_width',align='center')

        # Arrange the critical information
        self.critical_info = pn.Column(
            pnp.Markdown("**Critical Information**",styles=self.styles['markdown_text_title'],align='center'),
            pn.Row(pnp.Markdown("Battery",styles=self.styles['markdown_text_title'],align='center'),self.battery_progress,align='center'),
            pnl.Divider(),
            self.helper_graphics["Action_Progress"],
            pnl.Divider(),
            self.paint_indicator,
            sizing_mode='stretch_both',
            height_policy="max"
        )

        # Arrange the action home information
        self.action_home = self.helper_graphics["Actions_Mini"]
        self.action_home.insert(0,self.helper_graphics["Action_Progress"])
        self.action_home.insert(1,pnl.Divider())

    def _OrganiseHomeScreen(self):
        """
        _OrganiseHomeScreen (Private)
        Organises the home screen layout

        Arguments: N/A

        Returns: N/A
        Adds home page to self.pages
        """

        # Turns the page into a fixed grid system
        base = pnl.GridSpec(sizing_mode="stretch_both",styles = self.styles['areas'])

        base[0:2,0:2] = self.critical_info # Essentials: battery, progress, paint levels, system health
        base[2:5,0:2] = self.helper_graphics["SystemHealth"] # Robot Information, world information

        base[0:3,2:8] = self.helper_graphics['Wall_Visual'] # 2D Localisation map, highlighted entities and wall, mobile base motion plan

        base[3:5,2:5] =  self.helper_graphics["Actions_Mini"] # Current progress, current instruction, entities nearby, next insntruction, pause, skip and stop buttons

        base[3:5,5:8] =  self.helper_graphics['Manipulator_Motion'] # Manipualtor arm motion plan

        base[0:2,8:12] =  self.helper_graphics['Camera'] # RGB Camera

        base[2:4,8:12] =  self.helper_graphics['Lidar']

        base[4:5,8:12] =  self.helper_graphics["Emergency_Commands"] # Emergency commands and other command commands
        
        # Save result to pages dictionary
        self.pages["Home"] = pn.Row(base,self.helper_graphics['Safety'])

    def _OrganiseMotionScreen(self):
        """
        _OrganiseMotionScreen (Private)
        Organise the motion screen - handles inforamtion for mobile base and manipulator arms

        Arguments: N/A 

        Returns: N/A
        Adds motion page to self.pages
        """

        # Radio button enabled user to select between Mobile Base and Manipulator Arm
        radio = pnw.RadioButtonGroup(options=["Mobile Base","Manipulator Arm"],sizing_mode="stretch_width",button_type=self.styles['buttons'][0],button_style=self.styles['buttons'][1])
        
        # Mobile base sub-page creation
        robot_base = pnl.GridSpec(sizing_mode="stretch_both",)
        robot_base[0:6,0:2] = pn.Column(
            pnp.Markdown("**Mobile Base Information**",styles=self.styles['markdown_text_title']),
            pnp.Markdown("Model: Bespoke Model",styles=self.styles['markdown_text_reg']),
            pnp.Markdown("Drive Configuration: 4 wheel drive",styles=self.styles['markdown_text_reg']),
            pnp.Markdown("Dimension: 610mm x 610mm",styles=self.styles['markdown_text_reg']),
            
            pnl.Divider(),
            pnp.Markdown("Electronics",styles=self.styles['markdown_text_title']),
            pnp.Markdown("Main Controller: Raspberry Pi Module",styles=self.styles['markdown_text_reg']),
            pnp.Markdown("Power Source: Li-ion battery pack",styles=self.styles['markdown_text_reg']),

            pnl.Divider(),

            pnp.Markdown("Dimensions",styles=self.styles['markdown_text_title']),
            pnp.Markdown("Base Dimensions: 610mm x 610mm",styles=self.styles['markdown_text_reg']),
            pnp.Markdown("Wheels diameter: 50-60mm",styles=self.styles['markdown_text_reg']),
            pnp.Markdown("Top plate thickness: 5mm",styles=self.styles['markdown_text_reg']),
            pnp.Markdown("Side plate thickness: 2mm",styles=self.styles['markdown_text_reg']),
            pnp.Markdown("Bottom plate thickness: 3mm",styles=self.styles['markdown_text_reg']),
            pnp.Markdown("Load capcity per wheel: 30-40kg per wheel",styles=self.styles['markdown_text_reg']),
            pnp.Markdown("Weight: 35-45kg",styles=self.styles['markdown_text_reg']),

            pnl.Divider(),
            pnp.Markdown("Materials",styles=self.styles['markdown_text_title']),
            pnp.Markdown("Base frame: Mild steel frame and aluminium sheet",styles=self.styles['markdown_text_reg']),
            pnp.Markdown("Top plate: Aluminium",styles=self.styles['markdown_text_reg']),
            pnp.Markdown("Side plate: Aluminium",styles=self.styles['markdown_text_reg']),
            pnp.Markdown("Bottom plate: Aluminium",styles=self.styles['markdown_text_reg']),
            scroll = True
        )
        robot_base[0:4,2:6] = self.helper_graphics['Wall_Visual'] # Motion Plan
        robot_base[0:4,6:10] = self.helper_graphics['Lidar'] # LiDAR
        robot_base[4:6,2:6] = self.action_home #Instruction information
        robot_base[4:6,6:8] = self.helper_graphics["Emergency_Commands"] # Pause and stop 
        robot_base[4:6,8:10] = pnp.Image("./images/mobile_base.jpg") # 3D Model of entire robot



        manipulator_data = pd.read_csv("./data/manipulator_dh.csv")

        # Manipulator arm sub-page creation
        manipulator_arm = pnl.GridSpec(sizing_mode="stretch_both",)
        manipulator_arm[0:6,0:2] = pn.Column(#  Manipulator Information
            pnp.Markdown("**Manipulator Information**",styles=self.styles['markdown_text_title']),
            pnp.Markdown("Model: Bespoke Model",styles=self.styles['markdown_text_reg']),
            pnp.Markdown("Degrees of Freedom: 4",styles=self.styles['markdown_text_reg']),
            pnl.Divider(),
            pnp.Markdown("Modified DH Table",styles=self.styles['markdown_text_title']),
            pnp.DataFrame(manipulator_data,sizing_mode='stretch_width'),
            pnl.Divider(),
            pnp.Markdown("Material",styles=self.styles['markdown_text_title']),
            pnp.Markdown("Hollow aluminium tubing",styles=self.styles['markdown_text_reg']),
            pnp.Markdown("Foam end-effector",styles=self.styles['markdown_text_reg']),
            pnl.Divider(),
            pnp.Markdown("Angle Limits",styles=self.styles['markdown_text_title']),
            pnp.Markdown("Joint 1 || Min: -40 deg, Max: +40 deg",styles=self.styles['markdown_text_reg']),
            pnp.Markdown("Joint 2 || Min: -32.475, Max: +72.962",styles=self.styles['markdown_text_reg']),
            pnp.Markdown("Joint 3 || Min: -175, Max: -37.568",styles=self.styles['markdown_text_reg']),
            pnp.Markdown("Joint 4 || Min: -62.597, Max: 91.928",styles=self.styles['markdown_text_reg']),
            pnp.Markdown("Joint 5 || Min: -40 deg, Max: +40 deg",styles=self.styles['markdown_text_reg']),
            scroll = True
        ) 
        manipulator_arm[0:4,2:6] = self.helper_graphics['Manipulator_Motion'] # Manipulator Plan
        manipulator_arm[0:4,6:10] = self.helper_graphics['Camera'] # Camera
        manipulator_arm[4:6,2:6] = self.action_home # Instruction information
        manipulator_arm[4:6,6:8] = self.helper_graphics["Emergency_Commands"] # Pause and stop 
        manipulator_arm[4:6,8:10] = pnp.Image("./images/manipulator_schematic.jpg") # 3D Model of entire robot

        # Bind the radio button to change subpage motion, using all values, this means that the visual will change based on radio button choice
        content = pn.bind(self._ChangeSubPageMotion,value=radio,robot_base = robot_base, manipulator_arm=manipulator_arm)
        
        # Save page to pages dictionary
        self.pages["Motion"] = pn.Column(radio,content,self.helper_graphics['Safety'])

    def _ChangeSubPageMotion(self,value,robot_base,manipulator_arm):
        """
        _ChangeSubPageMotion (Private)
        Button triggered function, changes all visuals for the motion page, flipping between robot base and manipulator ar

        Arguments: N/A

        Returns: N/A
        """

        # This is a trigger function, meaning it must return a Panel panel, hence it returns either the robot_base panel or the manipulator panel
        if value == "Mobile Base": return robot_base
        else: return manipulator_arm
 
    def _OrganiseActionScreen(self):
        """
        _OrganiseActionScreen (Private)
        Organises the action screen : Allows users to select walls and create actions
        
        Arguments: N/A

        Returns: N/A
        """

        # Define the whole page, and place areas respectivly
        base = pnl.GridSpec(sizing_mode="stretch_both")
        base[0:,0:1] = self.helper_graphics['Actions'] # Action creation info
        base[0:,1:4] = self.helper_graphics["Wall_Visual"] # Room Plan (With labeled walls)
        
        # Save as actions page
        self.pages["Actions"] = pn.Row(base,self.helper_graphics['Safety'])

    def _OrganiseLoggingScreen(self):
        """
        _OrganiseLoggingScreen
        Method to organise the logging screen

        Arguments: N/A

        Returns: N/A
        Saves page to self.pages
        """

        self.log_terminal = pnw.Terminal("V.I.S.N.A.T Terminal",sizing_mode = 'stretch_both')

        self.pages["Logging"] = self.log_terminal

    def _OrganiseSideBar(self):
        """
        _OrganiseSideBar
        Method to create the sidebar of the application, part of template

        Arguments: N/A

        Returns: pn.Column || Sidebar column containing all neccessary widgets

        """

        # Display the essential system information - including emergency stop and pause

        # Radio button for all available pages - could theoretically change the options to dict.keys
        # preventing users from accessing unfinished pages
        radio_button = pnw.RadioButtonGroup(options=["Home","Actions","Motion","Logging","Legal Information"],orientation = 'vertical',button_type=self.styles['buttons'][0],button_style=self.styles['buttons'][1],sizing_mode="stretch_both")

        # Setup the column layout
        column = pn.Column(self.critical_info,pnl.Divider(),self.helper_graphics["Emergency_Commands"],pnl.Divider(),radio_button,sizing_mode="stretch_both")
        return column
    
    def _ChangePage(self,value):
        """
        _ChangePage
        Button triggered method that changes the visible page, called from buttons in the sidebar

        Arguments: str || value || Page to swap to

        Returns: N/A
        """
        if (value in self.pages.keys()): return self.pages[value]
        else:
            # Throw warning if page is not created 
            pn.state.notifications.warning("Warning: Page not found",duration = 4000)

    async def _PublishActiveAction(self):
        """
        _PublishActiveAction
        Method to notify node_handler to publish action_handler's current active action

        Called by _PublishingLoop every <timeperiod>

        Arguments: N/A

        Returns: N/A

        """
        self.node_handler.Publish("Current_Action",self.action_handler.active_action)


    def Notify(self,type:str,msg:str,time:int):
        """
        Notify
        Method tto create panel notifications that appear on the UI

        Arguments
            - str : type || Type of message (info, warning, error, fatal, etc)
            - str : msg || The message to be displayed
            - int : time || How long to display the message for

        Returns: N/A

        """
        if (type == 'Info'):
            pn.state.notifications.info(msg,time)
        elif (type == 'Warning'):
            pn.state.notifications.warning(msg,time)
        else:
            pn.state.notifications.error(msg,time)

    def Log(self,msg,type):
        pass

def main(args=None):
    """
        main
        Starting plasce to create and present user interface

        Arguments: Cmd args, these are ignored

        Returns: N/A

        """
    
    # Create GUI class
    gui = GUI()

    # Programmically serve the app
    pn.serve(gui.RunApp())

#%%
# Activation!
if __name__ == "__main__":

    rclpy.init()

    # Create GUI class
    gui = GUI(True)

    # Get and create the app
    app = gui.RunApp()

    # Programmically serve the app
    pn.serve(app)
