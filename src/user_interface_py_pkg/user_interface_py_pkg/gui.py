################################
# gui.py
# Part of the user_interface_py_pkg
#
# Part of Cranfield University MSC Robotics Group Project 2025-2026
################################

#%%
# Imports!
import numpy as np
import asyncio
import logging
import holoviews as hv
import panel as pn 
import pandas as pd
from action import Action
from node_handler import main as main_nodehandler
from node_handler import NodeHandler
from holoviews.streams import Pipe
from panel import pane as pnp
from panel import layout as pnl
from panel import widgets as pnw
pn.extension(notifications=True)
pn.extension('terminal')
hv.extension('bokeh')
import asyncio

"""
GUI Class handles the creation and utilisation of the user interface
"""
class GUI():
    
    def __init__(self):
        """Initialisation function. Prepares Interface for screen creation"""

        # Establish link to node handler
        self.node_handler = main_nodehandler()

        # Set button style - will affect all buttons in the UI
        self.styles_buttons = ['primary','outline']
        self.styles_areas={"border": "2px solid lightgray"}
        self.styles_markdown_text = {'font-size': '12pt'}
        self.styles_emergency_comands = "6em"

        # Set intial - prevents automatic firing of binded functions
        self.inital = True

        # Define pages
        self.pages = {}

        # Intialise action information
        self.active_action = 0
        self.planned_actions = []
        self.create_actions_widgets = []
        self.action_list  = 0

    def RunApp(self):
        """
        Main method called to create and deploy the user interface

        Returns: Servable application
        """
        # Createa all the screens
        self._CreateGraphics()

        self._CreateHomeScreen()
        self._CreateMotionScreen()
        self._CreateActionScreen()
        self._CreateLoggingScreen()
        side_bar = self._CreateSideBar()

        # Bind the function "_ChangePage" to the radio button group in the sidebar
        # Enabled operators to change main page content
        main_content = pn.bind(self._ChangePage,value=side_bar[2])

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

        return app
    
    def _CreateGraphics(self):

        # Create Lidar visual link
        lidar_pipe = Pipe(data = [])
        task = asyncio.create_task(self.node_handler.GetData('Lidar',lidar_pipe))
        lidar_dmap = hv.DynamicMap(hv.Scatter,streams=[lidar_pipe]).opts(responsive=True,color='black')
        robot_loc = hv.Scatter([(0,0)],label='Robot Centre').opts(color='blue',marker='star',size=10)
        self.lidar_scatter = pnl.WidgetBox(
            pnp.Markdown("**2D LiDAR**",styles=self.styles_markdown_text),
            (lidar_dmap*robot_loc),sizing_mode='stretch_both')
        
        self.motion_plan = pn.Column(self.lidar_scatter,pnp.Markdown("Mobile Base: No Path Planned",styles=self.styles_markdown_text,align='center'),sizing_mode='stretch_both')

        self.battery_progress = pn.indicators.Progress(name='Battery Level',active=True,sizing_mode='stretch_width',bar_color='success',align='center')
        self.battery_progress.value = 87
        self.paint_indicator = pn.indicators.LinearGauge(name='Paint Levels',value=2.6,format='{value:.1f} kg',bounds=(0.7,25.4),colors=['red','gold','green'],horizontal=True,sizing_mode='stretch_width',align='center')
        self.progress_progress = pnp.Markdown("No Task in Progress",styles=self.styles_markdown_text)
        self.progress_progress.value = 12

        self.critical_info = pn.Column(
            pnp.Markdown("**Critical Information**",styles=self.styles_markdown_text,align='center'),
            pn.Row(pnp.Markdown("Battery",styles=self.styles_markdown_text,align='center'),self.battery_progress,align='center'),
            pn.Row(pnp.Markdown("Action Progress",styles=self.styles_markdown_text,align='center'),self.progress_progress,align='center'),
            self.paint_indicator,
            sizing_mode='stretch_both',
            scroll = True,height_policy="max"
        )

        self.system_health = pn.Column(
            pnp.Markdown("**System Health**",styles=self.styles_markdown_text,align='center'),
            pnl.Divider(),
            pnp.Markdown("Safety Systems : Online",styles={'font-size': '10pt'}),
            pnp.Markdown("Safety Contingencies : On-Standby",styles={'font-size': '10pt'}),

            pnl.Divider(),

            pnp.Markdown("Lidar  : Online",styles={'font-size': '10pt'}),
            pnp.Markdown("Camera : Online",styles={'font-size': '10pt'}),

            pnl.Divider(),

            pnp.Markdown("Manipulator : Connected",styles={'font-size': '10pt'}),
            pnp.Markdown("Mobile Base : Connected",styles={'font-size': '10pt'}),

            pnl.Divider(),

            pnp.Markdown("Localisation: Offline",styles={'font-size': '10pt'}),
            pnp.Markdown("Mobile Base Motion Planning : Offline ",styles={'font-size': '10pt'}),
            pnp.Markdown("Manipulator Motion Planning : Offline ",styles={'font-size': '10pt'}),
            sizing_mode='stretch_both',
            scroll=True
        )

        self.emergency_commands = pn.Column(
            pnp.Markdown("**Commands**",styles=self.styles_markdown_text),
            pn.Row(
                pnw.ButtonIcon(icon='player-play',size=self.styles_emergency_comands),
                pnw.ButtonIcon(icon='player-stop',size=self.styles_emergency_comands),
                pnw.ButtonIcon(icon='player-pause',size=self.styles_emergency_comands),
                pnw.ButtonIcon(icon='player-skip-forward',size=self.styles_emergency_comands),
                align='center'
            )
        )

        img = pnp.Image("./images/snapshot.jpg",sizing_mode='stretch_both')
        self.camera_raw_panel = pn.WidgetBox(pnp.Markdown("**RGB-D Camera**",styles=self.styles_markdown_text),img,sizing_mode='stretch_both')
        self.manipulator_arm_path = pn.WidgetBox(img,pnp.Markdown("No Manipulator Path Planned",styles=self.styles_markdown_text,align='center'),sizing_mode='stretch_both')

        self.action_home = pn.WidgetBox(self.progress_progress)

    def _CreateHomeScreen(self):
        """Method to create the home screen layout"""

        # Turns the page into a fixed grid system
        base = pnl.GridSpec(sizing_mode="stretch_both",styles = self.styles_areas)

        base[0:2,0:2] = self.critical_info # Essentials: battery, progress, paint levels, system health
        base[2:5,0:2] = self.system_health # Robot Information, world information

        base[0:3,2:8] = self.motion_plan # 2D Localisation map, highlighted entities and wall, mobile base motion plan

        base[3:5,2:5] =  self.action_home # Current progress, current instruction, entities nearby, next insntruction, pause, skip and stop buttons

        base[3:5,5:8] =  self.manipulator_arm_path # Manipualtor arm motion plan

        base[0:2,8:12] =  self.camera_raw_panel # RGB Camera
        base[2:4,8:12] =  self.lidar_scatter

        base[4:5,8:12] =  self.emergency_commands # Emergency commands and other command commands
        
        # Save result to pages dictionary
        self.pages["Home"] = base

    def _CreateMotionScreen(self):
        """Method to create the robot motion screen"""

        # Radio button enabled user to select between Mobile Base and Manipulator Arm
        radio = pnw.RadioButtonGroup(options=["Mobile Base","Manipulator Arm"],sizing_mode="stretch_width",button_type=self.styles_buttons[0],button_style=self.styles_buttons[1])
        
        # Mobile base sub-page creation
        robot_base = pnl.GridSpec(sizing_mode="stretch_both",)
        robot_base[0:6,0:2] = pn.Column(
            pnp.Markdown("**Mobile Base Information**",styles=self.styles_markdown_text),
            pnp.Markdown("Model: Bespoke Model",styles={'font-size': '10pt'}),
            pnp.Markdown("Drive Configuration: 4 wheel drive",styles={'font-size': '10pt'}),
            pnp.Markdown("Dimension: 610mm x 610mm",styles={'font-size': '10pt'}),
            
            pnl.Divider(),
            pnp.Markdown("Electronics",styles=self.styles_markdown_text),
            pnp.Markdown("Main Controller: Raspberry Pi Module",styles={'font-size': '10pt'}),
            pnp.Markdown("Power Source: Li-ion battery pack",styles={'font-size': '10pt'}),

            pnl.Divider(),

            pnp.Markdown("Dimensions",styles=self.styles_markdown_text),
            pnp.Markdown("Base Dimensions: 610mm x 610mm",styles={'font-size': '10pt'}),
            pnp.Markdown("Wheels diameter: 50-60mm",styles={'font-size': '10pt'}),
            pnp.Markdown("Top plate thickness: 5mm",styles={'font-size': '10pt'}),
            pnp.Markdown("Side plate thickness: 2mm",styles={'font-size': '10pt'}),
            pnp.Markdown("Bottom plate thickness: 3mm",styles={'font-size': '10pt'}),
            pnp.Markdown("Load capcity per wheel: 30-40kg per wheel",styles={'font-size': '10pt'}),
            pnp.Markdown("Weight: 35-45kg",styles={'font-size': '10pt'}),

            pnl.Divider(),
            pnp.Markdown("Materials",styles=self.styles_markdown_text),
            pnp.Markdown("Base frame: Mild steel frame and aluminium sheet",styles={'font-size': '10pt'}),
            pnp.Markdown("Top plate: Aluminium",styles={'font-size': '10pt'}),
            pnp.Markdown("Side plate: Aluminium",styles={'font-size': '10pt'}),
            pnp.Markdown("Bottom plate: Aluminium",styles={'font-size': '10pt'}),
            scroll = True
        )
        robot_base[0:4,2:6] = self.motion_plan # Motion Plan
        robot_base[0:4,6:10] = self.lidar_scatter # LiDAR
        robot_base[4:6,2:6] = self.action_home #Instruction information
        robot_base[4:6,6:8] = self.emergency_commands # Pause and stop 
        robot_base[4:6,8:10] = pnp.Image("./images/mobile_base.jpg") # 3D Model of entire robot



        manipulator_data = pd.read_csv("./data/manipulator_dh.csv")

        # Manipulator arm sub-page creation
        manipulator_arm = pnl.GridSpec(sizing_mode="stretch_both",)
        manipulator_arm[0:6,0:2] = pn.Column(#  Manipulator Information
            pnp.Markdown("**Manipulator Information**",styles=self.styles_markdown_text),
            pnp.Markdown("Model: Bespoke Model",styles={'font-size': '10pt'}),
            pnp.Markdown("Degrees of Freedom: 4",styles={'font-size': '10pt'}),
            pnl.Divider(),
            pnp.Markdown("Modified DH Table",styles=self.styles_markdown_text),
            pnp.DataFrame(manipulator_data,sizing_mode='stretch_width'),
            pnl.Divider(),
            pnp.Markdown("Material",styles=self.styles_markdown_text),
            pnp.Markdown("Hollow aluminium tubing",styles={'font-size': '10pt'}),
            pnp.Markdown("Foam end-effector",styles={'font-size': '10pt'}),
            pnl.Divider(),
            pnp.Markdown("Angle Limits",styles=self.styles_markdown_text),
            pnp.Markdown("Joint 1 || Min: -40 deg, Max: +40 deg",styles={'font-size': '10pt'}),
            pnp.Markdown("Joint 2 || Min: -32.475, Max: +72.962",styles={'font-size': '10pt'}),
            pnp.Markdown("Joint 3 || Min: -175, Max: -37.568",styles={'font-size': '10pt'}),
            pnp.Markdown("Joint 4 || Min: -62.597, Max: 91.928",styles={'font-size': '10pt'}),
            pnp.Markdown("Joint 5 || Min: -40 deg, Max: +40 deg",styles={'font-size': '10pt'}),
            scroll = True
        ) 
        manipulator_arm[0:4,2:6] = self.manipulator_arm_path # Manipulator Plan
        manipulator_arm[0:4,6:10] = self.camera_raw_panel # Camera
        manipulator_arm[4:6,2:6] = self.action_home # Instruction information
        manipulator_arm[4:6,6:8] = self.emergency_commands # Pause and stop 
        manipulator_arm[4:6,8:10] = pnp.Image("./images/manipulator_schematic.jpg") # 3D Model of entire robot

        # Bind the radio button to change subpage motion, using all values, this means that the visual will change based on radio button choice
        content = pn.bind(self._ChangeSubPageMotion,value=radio,robot_base = robot_base, manipulator_arm=manipulator_arm)
        
        # Save page to pages dictionary
        self.pages["Motion"] = pn.Column(radio,content)

    def _ChangeSubPageMotion(self,value,robot_base,manipulator_arm):
        """Method to handle sub-page change for the Robot Motion page"""

        # This is a trigger function, meaning it must return a Panel panel, hence it returns either the robot_base panel or the manipulator panel
        if value == "Mobile Base": return robot_base
        else: return manipulator_arm
 
    def _CreateActionScreen(self):
        """Method to create the action screen"""

        # CreateActionList is a function that handles the list of actions and current action
        self.action_list = pn.Column(align='center',sizing_mode= 'stretch_both',scroll = True,height_policy="max")
        self.action_list.append(pnp.Markdown("No Actions Planned",styles={'font-size': '11pt'},align='center'))

        self.action_home.append(pnp.Markdown("No Actions Planned",styles={'font-size': '11pt'},align='center'))

        # Code to generate the modify or create action area
        action_planner_name = pnp.Markdown("**Action Planner**",styles=self.styles_markdown_text,align='center')
        action_name = pnw.TextInput(name="Action Name:",placeholder="Action X",align='center')
        
        wall_select = pnw.Select(name="Select Wall to Paint",options = [1,2,3,4],align='center')
        action_location_string = pnp.Markdown("When to start action: ",styles={'font-size': '11pt'},align='center')
        action_location = pnw.RadioButtonGroup(options=["Now","Next","Later"],value="Later",button_type=self.styles_buttons[0],button_style=self.styles_buttons[1]) # Radio button: Now, Next, Later
        confirm_button = pnw.Button(name="Save Action",button_type="success",button_style=self.styles_buttons[1],align='center')
        
        # Save the inputs as a class variable, enables access from other functions (when the 'Save Action' button is pressed)
        self.create_actions_widgets = [action_name,wall_select,action_location]

        # Conglomerate all the widgets into a dedicated area
        creation_area= pn.WidgetBox(
            action_planner_name,
            action_name,
            wall_select,
            pn.Row(action_location_string,action_location,align='center'),
            confirm_button,
            pn.bind(self._CreateActionSq,button=confirm_button),
            sizing_mode='stretch_width',
            align= 'center'
        )

        # Define action area - this involves the house plan and existing action list
        action_area = pn.WidgetBox(
            self.action_list,
            pnl.Divider(),
            creation_area,
            sizing_mode='stretch_width',
            align = 'center'
        )

        # Define the whole page, and place areas respectivly
        base = pnl.GridSpec(sizing_mode="stretch_both")
        base[0:,0:1] = action_area # Action creation info
        base[0:,1:4] = self.motion_plan # Room Plan (With labeled walls)
        
        # Save as actions page
        self.pages["Actions"] = base
    
    def _CreateActionSq(self,button):
        """Method to create actions"""

        # If not intialising
        # REMINDER: All trigger functions called once during preparation to ensure connection
        # In this case, we do NOT want a false action, hence skip if intialising
        if (self.inital == False):

            # Create action class from inputs
            action = Action(self.create_actions_widgets[0].value,self.create_actions_widgets[1].value)
            
            # If no name provided, use a default name of "Action X", where X is how many actions already exist
            if (action.name == ""): action.name = "Action "+str(len(self.planned_actions))

            # If the user wants to intrupt the current action
            if self.create_actions_widgets[2].value == 'Now':
                # Set it to be the next item
                action.SetListLoc(1)
                # Notify operator of override

                # End current action

            # If the operator wants it to be the next action
            elif self.create_actions_widgets[2].value == 'Next':
                # Set action as next to be done
                action.SetListLoc(1)

            # IF the operator wants it to be later, add to end of the list
            # Might change, to allow operator to select where to place the action
            else:
                action.SetListLoc(len(self.planned_actions))

            # If there is more than 2 actions, then use insert if Now or Next
            # Cause you can't do it otherwise
            if len(self.planned_actions) >= 2 and action.GetLoc() == 1:
                self.planned_actions.insert(1,action)
            else:
                # Add to end of planned action list
                self.planned_actions.append(action)
   
            # Call CreateActionList to update the visual list of actions
            if len(self.planned_actions) == 1:
                self.action_list.pop()
                self.action_home.pop()
                self.progress_progress = pn.indicators.Progress(name='Task Progress',active=True,sizing_mode='stretch_width',bar_color='success',align='center')
                self.progress_progress = 15
                # If the action is not active, present a play button to start, else a pause button
                if (self.active_action == 0): button = pnw.ButtonIcon(icon="player-play",size="2em",align="center")
                else: button = pnw.ButtonIcon(icon="player-pause",size="2em",align="center")

                new_item = pn.WidgetBox(
                        pnp.Markdown(f"Current Action: {action.name} || Wall: {action.wall}",styles={'font-size': '11pt'},align="center"),
                        button,
                        pnl.Divider(),
                        sizing_mode='stretch_width'
                    )
                # Otherwise display current action information
                self.action_list.append(new_item)
                self.action_home.append(new_item)

            else:
                item = pn.WidgetBox(pn.Row(
                        pnp.Markdown(f"{action.name} || Wall: {action.wall}",styles={'font-size': '11pt'},align="center"),
                        pnw.ButtonIcon(icon='edit',size="2em",align="center"),
                        pnw.ButtonIcon(icon='trash',size="2em",align="center"),
                        sizing_mode='stretch_width'
                    ))
                self.action_list.insert(action.loc,item)
                
                if action.loc == 1 and len(self.action_home) == 2:
                    self.action_home.append(pnp.Markdown(f"Next Action: {action.name} || Wall: {action.wall}",styles={'font-size': '11pt'},align="center"),)
                elif action.loc == 1:
                    self.action_home.pop()
                    self.action_home.append(pnp.Markdown(f"Next Action: {action.name} || Wall: {action.wall}",styles={'font-size': '11pt'},align="center"),)
         


    def _CreateRobotInfoScreen(self):
        pass

    def _CreateLoggingScreen(self):

        logging_info = pn.Column(pnp.Markdown("Critical Logging",styles=self.styles_markdown_text,align='center'),pnw.Terminal("V.I.S.N.A.T Terminal",sizing_mode = 'stretch_both'))
        logging_critical = pn.Column(pnp.Markdown("All Logging",styles=self.styles_markdown_text,align='center'),pnw.Terminal("V.I.S.N.A.T Critical Terminal", sizing_mode = 'stretch_both'))

        logging_base = pn.Row(logging_critical,logging_info,sizing_mode='stretch_both')

        self.pages["Logging"] = logging_base


    def _CreateSideBar(self):
        """Method to create the sidebar of the application"""

        # Display the essential system information - including emergency stop and pause
        essentials = pn.Column("Critical Information",sizing_mode="stretch_both")

        # Radio button for all available pages - could theoretically change the options to dict.keys
        # preventing users from accessing unfinished pages
        radio_button = pnw.RadioButtonGroup(options=["Home","Actions","Motion","Robot Information","Logging","Legal Information"],orientation = 'vertical',button_type=self.styles_buttons[0],button_style=self.styles_buttons[1],sizing_mode="stretch_both")

        # Setup the column layout
        column = pn.Column(essentials,pnl.Divider(),radio_button,sizing_mode="stretch_both")
        return column
    
    def _ChangePage(self,value):
        """Method to change the main page content"""
        if (value in self.pages.keys()): return self.pages[value]
        else:
            # Throw warning if page is not created 
            pn.state.notifications.warning("Warning: Page not found",duration = 4000)


def main(args=None):
    
    # Create GUI class
    gui = GUI()

    # Programmically serve the app
    pn.serve(gui.RunApp())

#%%
# Activation!
if __name__ == "__main__":
    # Create GUI class
    gui = GUI()

    # Get and create the app
    app = gui.RunApp()

    # Programmically serve the app
    pn.serve(app)

# %%
