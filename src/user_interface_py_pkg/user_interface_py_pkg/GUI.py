
#%%
import panel as pn 
from panel import pane as pnp
from panel import layout as pnl
from panel import widgets as pnw
pn.extension(notifications=True)




class GUI():
    
    def __init__(self):
        self.pages = {}

        self.button_colouring = ['primary','outline']
        pass
        

    def LinkToNodes(self):
        pass


    def RunApp(self):
        self._CreateHomeScreen()
        self._CreateTestScreen()
        self._CreateMotionScreen()
        self._CreateActionScreen()
        side_bar = self._CreateSideBar()

        main_content = pn.bind(self._ChangePage,value=side_bar[3])

        app = pn.template.VanillaTemplate(
            title = "V.I.S.N.A.T: Monitoring GUI",
            main = [main_content],
            sidebar = side_bar,
            collapsed_sidebar = True
            
        ).servable()

        return app
    


    def _CreateHomeScreen(self):
        base = pnl.GridSpec(sizing_mode="stretch_both",)

        base[0:2,0:2] = pn.Spacer(styles=dict(background='red')) # Essentials: battery, progress, paint levels, system health
        base[2:5,0:2] = pn.Spacer(styles=dict(background='blue')) # Robot Information, world information

        base[0:3,2:8] = pn.Spacer(styles=dict(background='green')) # 2D Localisation map, highlighted entities and wall, mobile base motion plan

        base[3:5,2:5] =  pn.Spacer(styles=dict(background='yellow')) # Current progress, current instruction, entities nearby, next insntruction, pause, skip and stop buttons

        base[3:5,5:8] =  pn.Spacer(styles=dict(background='cyan')) # Manipualtor arm motion plan

        base[0:2,8:12] =  pn.Spacer(styles=dict(background='magenta')) # RGB Camera
        base[2:4,8:12] =  pn.Spacer(styles=dict(background='purple')) # LiDAR Camera

        base[4:5,8:12] =  pn.Spacer(styles=dict(background='lime')) # Emergency commands and other command commands
        
        self.pages["Home"] = base

    def _CreateMotionScreen(self):

        radio = pnw.RadioButtonGroup(options=["Mobile Base","Manipulator Arm"],sizing_mode="stretch_width",button_type=self.button_colouring[0],button_style=self.button_colouring[1])
        robot_base = pnl.GridSpec(sizing_mode="stretch_both",)
        robot_base[0:6,0:2] = pn.Spacer(styles=dict(background='red')) # Mobile Base Information
        robot_base[0:4,2:6] = pn.Spacer(styles=dict(background='orange')) # Motion Plan
        robot_base[0:4,6:10] = pn.Spacer(styles=dict(background='yellow')) # LiDAR
        robot_base[4:6,2:6] = pn.Spacer(styles=dict(background='darkred')) #Instruction information
        robot_base[4:6,6:8] = pn.Spacer(styles=dict(background='darkorange')) # Pause and stop 
        robot_base[4:6,8:10] = pn.Spacer(styles=dict(background='red')) # 3D Model of entire robot

        manipulator_arm = pnl.GridSpec(sizing_mode="stretch_both",)
        manipulator_arm[0:6,0:2] = pn.Spacer(styles=dict(background='blue')) # Mobile Base Information
        manipulator_arm[0:4,2:6] = pn.Spacer(styles=dict(background='cyan')) # Motion Plan
        manipulator_arm[0:4,6:10] = pn.Spacer(styles=dict(background='purple')) # LiDAR
        manipulator_arm[4:6,2:6] = pn.Spacer(styles=dict(background='darkblue')) #Instruction information
        manipulator_arm[4:6,6:8] = pn.Spacer(styles=dict(background='turquoise')) # Pause and stop 
        manipulator_arm[4:6,8:10] = pn.Spacer(styles=dict(background='lightblue')) # 3D Model of entire robot

        content = pn.bind(self._ChangeSubPageMotion,value=radio,robot_base = robot_base, manipulator_arm=manipulator_arm)
        
        self.pages["Motion"] = pn.Column(radio,content)

    def _ChangeSubPageMotion(self,value,robot_base,manipulator_arm):
        if value == "Mobile Base": return robot_base
        else: return manipulator_arm
 


 
    def _CreateActionScreen(self):
        # Maybe change the layout, such that the current creation-area displays all
        # actions, then the dark blue 

        #Essentially, I need a way to Edit an existing action or create a new action

        # IF I do a vertical radio group, listing the actions in order, then right below it (not part of the group, mind you)
        # allow the user to select a 'create' new action' button. Selecting a radio-group button will bring that information up below
        # The current action cannot be modified.

        # I need a list pretty much, list then all, then allow the user to save or delete it. 
        # Use the radio button idea, Change the layout as needed (move the dark blue above the cyan)
        # Then it should be fine, adding a new action or saving a new action
        # Can also do the image display (at least, not the wall selection or anything yet, that needs more processing)

        house_string = pnp.Markdown("Select A House Plan",styles={'font-size': '11pt'})
        house_plan = pnw.FileInput(accept='.png')
        action_name = pnw.TextInput(name="Action Name:",placeholder="Action X")
        room_select = pnw.Select(name="Select Room",options = ["Living Room","Bedroom 1","Need to replace at later date"])
        wall_select = pnw.Select(name="Select Wall to Paint",options = [1,2,3,4])
        action_location_string = pnp.Markdown("When to start action: ",styles={'font-size': '11pt'})
        action_location = pnw.RadioButtonGroup(options=["Now","Next","Later"],value="Later") # Radio button: Now, Next, Later
        confirm_button = pnw.Button(name="Create Action") # Create an action

        creation_area = pn.WidgetBox(
            house_string, house_plan,
            pnl.Divider(),
            action_name,
            room_select,
            wall_select,
            pn.Row(action_location_string,action_location),
            confirm_button
        )

        base = pnl.GridSpec(sizing_mode="stretch_both",)
        base[0:1,0:2] = creation_area # Action creation info
        base[0:,2:4] = pn.Spacer(styles=dict(background='green')) # Room Plan (With labeled walls)
        base[1:2,0:1] = pn.Spacer(styles=dict(background='blue')) # Action Queue (All current actions, with option to delete, edit, etc)
        base[1:2,1:2] = pn.Spacer(styles=dict(background='cyan')) # Full house plan (with room marked) by an icon
        
        self.pages["Actions"] = base
    
    def _CreateActionHousePlanPresent(self,houseplan):
        pass

    def _CreateActionSq(self,name,room,wall,loc):
        pass

    def _CreateRobotInfoScreen(self):
        pass

    def _CreateLoggingScreen(self):
        pass

    def _CreateTestScreen(self):
        
        self.pages["Test"] = pn.WidgetBox("Test Screen!",sizing_mode = "stretch_both")

    def _CreateSideBar(self):

        essentials = pn.WidgetBox("System Information",sizing_mode="stretch_both")
        system_health = pn.WidgetBox("Robot Information",sizing_mode="stretch_both")

        radio_button = pnw.RadioButtonGroup(options=["Home","Actions","Motion","Robot Information","Logging","Legal Information"],orientation = 'vertical',button_type=self.button_colouring[0],button_style=self.button_colouring[1],sizing_mode="stretch_both")

        column = pn.Column(essentials,system_health,pnl.Divider(),radio_button,sizing_mode="stretch_both")
        return column
    
    def _ChangePage(self,value):

        if (value in self.pages.keys()): return self.pages[value]
        else: pn.state.notifications.warning("Warning: Page not found",duration = 4000)
            
        

if __name__ == "__main__":
    gui = GUI()
    gui.LinkToNodes()
    app = gui.RunApp()
    pn.serve(app)
# %%


