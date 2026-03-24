################################
# gui.py
# Part of the user_interface_py_pkg
#
# Part of Cranfield University MSC Robotics Group Project 2025-2026
################################

#%%
from action import Action
from node_handler import main as main_nodehandler
from node_handler import NodeHandler
import panel as pn 
from panel import pane as pnp
from panel import layout as pnl
from panel import widgets as pnw
pn.extension(notifications=True)


"""
GUI Class handles the creation and utilisation of the user interface
"""
class GUI():
    
    def __init__(self):
        """Initialisation function. Prepares Interface for screen creation"""

        # Establish link to node handler
        self.node_handler = main_nodehandler()

        # Set button style - will affect all buttons in the UI
        self.button_colouring = ['primary','outline']

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
        self._CreateHomeScreen()
        self._CreateMotionScreen()
        self._CreateActionScreen()
        side_bar = self._CreateSideBar()

        # Bind the function "_ChangePage" to the radio button group in the sidebar
        # Enabled operators to change main page content
        main_content = pn.bind(self._ChangePage,value=side_bar[3])

        # Disable intial
        # Initial is present as all triggerable functions are triggered once during creation to ensure
        # connection is created correctly, self.intial is used to stop any output from these - until app is deployed
        self.inital = False

        # Create app using VanillaTemplate - alternate templates may affect visual elements
        app = pn.template.VanillaTemplate(
            title = "V.I.S.N.A.T: Monitoring GUI",
            main = [main_content],
            sidebar = side_bar,
            collapsed_sidebar = True # Have the sidebar start collapsed
            
        ).servable()

        return app
    


    def _CreateHomeScreen(self):
        """Method to create the home screen layout"""

        # Turns the page into a fixed grid system
        base = pnl.GridSpec(sizing_mode="stretch_both",)

        base[0:2,0:2] = pn.Spacer(styles=dict(background='red')) # Essentials: battery, progress, paint levels, system health
        base[2:5,0:2] = pn.Spacer(styles=dict(background='blue')) # Robot Information, world information

        base[0:3,2:8] = pn.Spacer(styles=dict(background='green')) # 2D Localisation map, highlighted entities and wall, mobile base motion plan

        base[3:5,2:5] =  pn.Spacer(styles=dict(background='yellow')) # Current progress, current instruction, entities nearby, next insntruction, pause, skip and stop buttons

        base[3:5,5:8] =  pn.Spacer(styles=dict(background='cyan')) # Manipualtor arm motion plan

        base[0:2,8:12] =  pn.Spacer(styles=dict(background='magenta')) # RGB Camera
        base[2:4,8:12] =  pn.Spacer(styles=dict(background='purple')) # LiDAR Camera

        base[4:5,8:12] =  pn.Spacer(styles=dict(background='lime')) # Emergency commands and other command commands
        
        # Save result to pages dictionary
        self.pages["Home"] = base

    def _CreateMotionScreen(self):
        """Method to create the robot motion screen"""

        # Radio button enabled user to select between Mobile Base and Manipulator Arm
        radio = pnw.RadioButtonGroup(options=["Mobile Base","Manipulator Arm"],sizing_mode="stretch_width",button_type=self.button_colouring[0],button_style=self.button_colouring[1])
        
        # Mobile base sub-page creation
        robot_base = pnl.GridSpec(sizing_mode="stretch_both",)
        robot_base[0:6,0:2] = pn.Spacer(styles=dict(background='red')) # Mobile Base Information
        robot_base[0:4,2:6] = pn.Spacer(styles=dict(background='orange')) # Motion Plan
        robot_base[0:4,6:10] = pn.Spacer(styles=dict(background='yellow')) # LiDAR
        robot_base[4:6,2:6] = pn.Spacer(styles=dict(background='darkred')) #Instruction information
        robot_base[4:6,6:8] = pn.Spacer(styles=dict(background='darkorange')) # Pause and stop 
        robot_base[4:6,8:10] = pn.Spacer(styles=dict(background='red')) # 3D Model of entire robot

        # Manipulator arm sub-page creation
        manipulator_arm = pnl.GridSpec(sizing_mode="stretch_both",)
        manipulator_arm[0:6,0:2] = pn.Spacer(styles=dict(background='blue')) # Manipulator Information
        manipulator_arm[0:4,2:6] = pn.Spacer(styles=dict(background='cyan')) # Manipulator Plan
        manipulator_arm[0:4,6:10] = pn.Spacer(styles=dict(background='purple')) # Camera
        manipulator_arm[4:6,2:6] = pn.Spacer(styles=dict(background='darkblue')) # Instruction information
        manipulator_arm[4:6,6:8] = pn.Spacer(styles=dict(background='turquoise')) # Pause and stop 
        manipulator_arm[4:6,8:10] = pn.Spacer(styles=dict(background='lightblue')) # 3D Model of entire robot

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
        self.action_list = pn.Column(align='center',sizing_mode= 'stretch_both',scroll = True,height_policy="max" )
        self.action_list.append(pnp.Markdown("No Actions Planned",styles={'font-size': '11pt'},align='center'))

        # Code to generate the modify or create action area
        action_planner_name = pnp.Markdown("Action Planner",styles={'font-size': '11pt'},align='center')
        action_name = pnw.TextInput(name="Action Name:",placeholder="Action X",align='center')
        
        wall_select = pnw.Select(name="Select Wall to Paint",options = [1,2,3,4],align='center')
        action_location_string = pnp.Markdown("When to start action: ",styles={'font-size': '11pt'},align='center')
        action_location = pnw.RadioButtonGroup(options=["Now","Next","Later"],value="Later",button_type=self.button_colouring[0],button_style=self.button_colouring[1]) # Radio button: Now, Next, Later
        confirm_button = pnw.Button(name="Save Action",button_type="success",button_style=self.button_colouring[1],align='center')
        
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
        base[0:,1:4] = pn.Spacer(styles=dict(background='green')) # Room Plan (With labeled walls)
        
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
                # If the action is not active, present a play button to start, else a pause button
                if (self.active_action == 0): button = pnw.ButtonIcon(icon="player-play",size="2em",align="center")
                else: button = pnw.ButtonIcon(icon="player-pause",size="2em",align="center")

                # Otherwise display current action information
                self.action_list.append(
                    pn.WidgetBox(
                        pnp.Markdown("Current Action",align="center"),
                        pnp.Markdown(f"{action.name} || Wall: {action.wall}",styles={'font-size': '11pt'},align="center"),
                        button,
                        pnl.Divider(),
                        sizing_mode='stretch_width'
                    )
                )
            else:
                self.action_list.insert(action.loc,
                    pn.WidgetBox(pn.Row(
                        pnp.Markdown(f"{action.name} || Wall: {action.wall}",styles={'font-size': '11pt'},align="center"),
                        pnw.ButtonIcon(icon='edit',size="2em",align="center"),
                        pnw.ButtonIcon(icon='trash',size="2em",align="center"),
                        sizing_mode='stretch_width'
                    ))
                )
         


    def _CreateRobotInfoScreen(self):
        pass

    def _CreateLoggingScreen(self):
        pass



    def _CreateSideBar(self):
        """Method to create the sidebar of the application"""

        # Display the essential system information - including emergency stop and pause
        essentials = pn.WidgetBox("System Information",sizing_mode="stretch_both")

        # Display the system health - is everything runnning well? What's having errors or anomalous stuff
        system_health = pn.WidgetBox("Robot Information",sizing_mode="stretch_both")

        # Radio button for all available pages - could theoretically change the options to dict.keys
        # preventing users from accessing unfinished pages
        radio_button = pnw.RadioButtonGroup(options=["Home","Actions","Motion","Robot Information","Logging","Legal Information"],orientation = 'vertical',button_type=self.button_colouring[0],button_style=self.button_colouring[1],sizing_mode="stretch_both")

        # Setup the column layout
        column = pn.Column(essentials,system_health,pnl.Divider(),radio_button,sizing_mode="stretch_both")
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

    # Get and create the app
    app = gui.RunApp()

    # Programmically serve the app
    pn.serve(app)

#%%
# Activation!
if __name__ == "__main__":
    main()

