################################
# gui_helper.py
# Part of the user_interface_py_pkg
#
# Author: Nathan Horder (nathan.horder.700@cranfield.ac.uk)
# Part of Cranfield University MSC Robotics Group Project 2025-2026
################################
# Imports!
import asyncio
import holoviews as hv
import panel as pn 
import asyncio
from PIL import Image
from holoviews.streams import Pipe
from panel import pane as pnp
from panel import layout as pnl
from panel import widgets as pnw
pn.extension(notifications=True)
pn.extension('terminal')
hv.extension('bokeh')

 
"""
GUIHelper
Class to create and handle dynamic graphics for the user interface 
Main Function: CreateGraphics
    Arguments: N/A
    Returns: dict : graphics || Graphics : Graphics Data (Primarily consists of Panel data)
"""
class GUIHelper():
    
    def __init__(self,gui, node_handler,action_handler, styles=None,dev_mode=False):
        self.gui = gui
        self.node_handler = node_handler
        self.action_handler = action_handler
        self.dev_mode = dev_mode
        self.no_walls_notified = False
        
        # Set styles if styles are None
        if (styles == None):
            self.styles = {}
            self.styles['buttons'] = ['primary','outline']
            self.styles['areas'] = {"border": "2px solid lightgray"}
            self.styles['markdown_text_title'] = {'font-size': '12pt'}
            self.styles['markdown_text_reg'] = {'font-size': '10pt'}
            self.styles['emergency_command'] = "4em"
            self.styles['command'] = '2em'
        else:
            self.styles = styles


        self.system_notifications = {}
        self.previous_system_health = {}

    def StartTimers(self):
        """
        StartTimers (Public)
        Method to start periodic callback timers

        Arguments: N/A

        Returns: N/A
        """
        pn.state.add_periodic_callback(self._CreateSafetyMessageCallback,100) # Run every 100ms
        pn.state.add_periodic_callback(self._CreateCameraImageCallback,100) # Run every 100ms
        pn.state.add_periodic_callback(self._SystemHealthCallback,250) # Run every 250ms
        pn.state.add_periodic_callback(self._CreateWallSelectionCallback,250) # Run every 250ms
        pn.state.add_periodic_callback(self._CreateWallRescanPeriodicCallback,250) # Run every 250ms

    def CreateGraphics(self):
        """
        CreateGraphics (Public)
        Main method of class, used to create all dynamic graphics of the user interface

        Arguments: N/A

        Returns:
            - dict: graphics || Dictionary containing all dynamic graphics

        """

        # Create all graphics
        self.graphics = {}
        self.graphics["Safety"] = self._CreateSafetyMessage()
        self.graphics["Lidar"] = self._CreateLidarGraph()
        self.graphics["Camera"] = self._CreateCameraImage()
        self.graphics["SystemHealth"] = self._CreateSystemHealth()
        self.graphics["Wall_Visual"] = self._CreateWallGraphic()
        self.graphics["Wall_Selection"]= self._CreateWallSelection()
        self.graphics["Rescan"] = self._CreateWallRescan()
        self.graphics["Emergency_Commands"] = self._CreateCommandsEm()
        self.graphics["Commands"] = self._CreateCommands()

        # Acquire graphics from action handler, break them down to separate them into respective panels
        # Mini refers to the limited action graphic (Just current and next action)
        actions = self.action_handler.CreateGraphics(self)
        self.graphics["Actions"] = actions[0]
        self.graphics["Actions_Mini"] = actions[1]
        self.graphics["Action_Progress"] = actions[2]

        return self.graphics

    def _CreateSafetyMessage(self):
        """
        _CreateSafetyMessage (Private)
        Method to generate graphics for safety

        Arguments: N/A

        Returns:
            - pn.Modal : self.announcement || A dedicated red box appears when a fatal error occurs
        """

        # Define standard fixed text
        title = pnp.Markdown("**Emergency**",styles=self.styles['markdown_text_title'])
        description = pnp.Markdown("V.I.S.N.A.T functions have been terminated. The cause of this may result from faulty sensors, " \
            "faulty systems or an entity is too close to the mobile base. Once a solution has been determined, please select 'RESET' to continue the current action",styles=self.styles['markdown_text_reg'])
        
        # Set the reset button
        reset_system = pnw.Button(name='RESET',button_type = 'danger',button_style='solid')
        # Link reset button to a function
        reset_system.on_click(self._CreateSafetyMessageButtonCallback)

        # Organise the announcement Modal
        self.announcement = pn.Modal(
            title,
            description,
            reset_system,
            background_close = False,
            show_close_button = False
        )

        # Immediately hide it, as no fatal error begins on launch
        self.announcement.hide()

        # Set msg shown to False
        # This is used in tandem with Slow, Terminate and Normal, hence need to set these on creation
        self.safety_terminate_msg_shown = False
        self.safety_slow_added = False
        self.safety_slow_removed = False

        return self.announcement

    def _CreateSafetyMessageCallback(self):
        """
        _CreateSafetyMessageCallback (Private)
        Method to activate safety information

        Arguments: N/A

        Returns: N/A
        """

        # Get the safety related message
        msg = self.node_handler.GetData('Safety')

        # If the msg is 'terminate'
        if msg == 'terminate':
            if (not self.safety_terminate_msg_shown):
                # Present the announcement, assume all other systems are stopped during this time. Await confirmation to reset
                self.announcement.show()

                # Pause current action
                self.action_handler.PauseAction()
                
                # Prevent flickering visual
                self.safety_slow_added = False
                self.safety_slow_removed = False
                self.safety_terminate_msg_shown = True

        # If the msg is 'slow'
        elif msg == 'slow':
            
            if (not self.safety_slow_added and self.action_handler.active_action != None):
                # Update current progress
                self.action_handler.progress[3].object = self.action_handler.progress[3].object + " (Slow)"

                self.gui.Notify(type='Warning',msg=f'WARNING: Slowing all process speed, at least one entity is near the robot',time=10000)

                # Prevent flickering visual
                self.safety_slow_added = True
                self.safety_slow_removed = False
                self.safety_terminate_msg_shown = False
        
        # Else it's functioning normally
        else:
            if (not self.safety_slow_removed):
                self.action_handler.progress[3].object = (self.action_handler.progress[3].object).strip("(Slow)")
                
                # Prevent flickering visual
                self.safety_slow_added = False
                self.safety_slow_removed = True
                self.safety_terminate_msg_shown = False

    def _CreateSafetyMessageButtonCallback(self,event):
        """
        _CreateSafetyMessageButtonCallback (Private)
        Callback method for safety reset button

        Arguments: N/A

        Returns:
            - pn.Modal : self.announcement || A dedicated red box appears when a fatal error occurs
        """
        # Hide the annoucement
        self.announcement.hide()

        # Notify safety systems to reset
        # NOTE: Safety systems are not used during the simulation, see sensor_safety_py_pkg for more information

    def _CreateLidarGraph(self):
        """
        _CreateLidarGraph (Private)
        Method to generate dynamic graphics for Lidar data

        Arguments: N/A

        Returns:
            - pnl.WidgetBox : lidar_scatter || Lidar Scatter widgetbox, contains hv.DynamicMap, updates through asyncio and Pipes
        """
        # Create pipe
        lidar_pipe = Pipe(data = [])

        # Create ayncio (multi-thread path)
        task = asyncio.create_task(self.node_handler.GetDataAsync('Lidar',lidar_pipe))
        
        # Create the dynamic map using the pipe - this allows streaming of live lidar to the scatter graphic
        self.lidar_dmap = hv.DynamicMap(hv.Scatter,streams=[lidar_pipe]).opts(responsive=True,color='black',shared_axes=False,tools=['hover'])

        # Set the robot location, which is at 0,0 (based on lidar location)
        robot_loc = hv.Scatter([(0,0)],label='Robot Centre').opts(color='blue',marker='star',size=10,shared_axes=False,tools=['hover'])
        
        # Create panel visual
        lidar_scatter = pnl.WidgetBox(
            pnp.Markdown("**2D LiDAR**",styles=self.styles['markdown_text_title']),
            (self.lidar_dmap*robot_loc),sizing_mode='stretch_both')

        # Return visual      
        return lidar_scatter
    
    def _CreateCameraImage(self):
        """
        _CreateCameraImage (Private)
        Method to create camera image

        Arguments: N/A

        Returns:
             pn.WidgetBox || Camera image box, with text
        """
        # Create the image panel visual
        self.camera_img = pnp.Image(sizing_mode='scale_both')

        # Return the visual for the whole image
        return pn.WidgetBox(pnp.Markdown("**RGB-D Camera**",styles=self.styles['markdown_text_title']),
                            self.camera_img,
                            sizing_mode='stretch_both')
    
    def _CreateCameraImageCallback(self):
        """
        _CreateCameraImageCallback (Private)
        Method to update image of camera_img (Created by _CreateCameraImage)
        Called periodically by related timer

        Arguments: N/A

        Returns: N/A
        """
        # Capture the data
        data = self.node_handler.GetData('Camera')

        # If the data is not none and not a 0d numpy array
        if data is not None and data.size > 0:

            # Update image visual
            img = Image.fromarray(data)
            self.camera_img.object = img

    def _CreateSystemHealth(self):
        """
        _CreateSystemHealth (Private)
        Method to create dynamic system health visual

        Arguments: N/A

        Returns:
            - pn.Column : self.system_health || System Health visual
        """
        # Create visual
        self.system_health = pn.Column(
            pnp.Markdown("**System Health**",styles=self.styles['markdown_text_title'],align='center'),
            pnl.Divider(),
            sizing_mode='stretch_both',
            scroll=True
        )

        # Create intial systems to be displayed
        systems_health = ['GUI','Mobile_Base','Manipulator_Arm','Visual_Sensor_Systems','Data_Processing','Path_Planning','Path_Following','Simulation']

        # Display each system, by adding it to the list, add 'Checking' param to notify operator
        for system in systems_health:
            self.system_health.append(pnp.Markdown(f"{system}: Checking"))

        # Return the visual
        return self.system_health

    def _SystemHealthCallback(self):
        """
        _SystemHealthCallback (Private)
        Callback method for System Health, updates visual periodically

        Arguments: N/A

        Returns: N/A
        """

        #Acquire the data and it's keys
        data = self.node_handler.GetData("SysHP")
        keys = list(data.keys())

        # Check that it's data is not empty, and it has more than one key
        if data != {} and len(keys) > 1:
            
            # Define key being looked at
            key_idx = 0

            # Loop all items within the visual, ignoring the first two items (Text and a divider)
            for idx in range(2,len(self.system_health)):

                # If a divider is found, skip past it
                if (self.system_health[idx] == pnl.Divider()):
                    continue

                else:
                    # Update the visual item with the new information, based on the key idx
                    self.system_health[idx].object = f"{keys[key_idx]} : {data[keys[key_idx]]}"

                    # Check if there is a previous system health saved
                    # AND the key exists in the previous system health
                    # AND the current value does not equal the saved value
                    # Resulting in notifying the operator on change, instead of all the time
                    if (self.previous_system_health != {} and keys[key_idx] in self.previous_system_health.keys() and data[keys[key_idx]] != self.previous_system_health[keys[key_idx]]):

                        match data[keys[key_idx]]:
                            case "NO-CONNECTION":
                                # Throw panel warning notification
                                self.gui.Notify(type='Warning',msg=f'WARNING: Failed to establish connection to {keys[key_idx]}.',time=3000) # Retain notification for 3 seconds

                            case "ANOMALOUS":
                                # Throw panel warning notification
                                self.gui.Notify(type='Warning',msg=f'WARNING: Inconsistiencies have been identified in: {keys[key_idx]}',time=10000)  # Retain notification for 10 seconds

                            case "FATAL":
                                # Throw panel warning notification
                                self.gui.Notify(type='Error',msg=f'ERROR: {keys[key_idx]} is faulty.',time=0) # Retain notificaiton until operator dismisses it
                    
                    # Increment key
                    key_idx += 1
        
        # Update previously known data
        self.previous_system_health = data

    def _CreateWallGraphic(self):
        """
        _CreateWallGraphic (Private)
        Method to create visualisation of walls

        Arguments: N/A

        Returns: pnl.WidgetBox : wall_graphic || Dynamic visual of wall graphic, contains a hv.DynamicMap that udpates via asyncio and Pipes

        """
        # Create pipe for streaming data
        pipe = Pipe(data=[])
        
        # Create task to update the pipe
        task = asyncio.create_task(self.node_handler.GetDataAsync('Wall_Visual',pipe))

        # Create Dynamic map
        dmap = hv.DynamicMap(self._CreateWallGraphicCallback,streams = [pipe]).opts(responsive=True,tools=['hover'])

        # Create the graphic
        wall_graphic = pnl.WidgetBox(
            pnp.Markdown("**Room Walls**",styles=self.styles['markdown_text_title']),
            (dmap), sizing_mode = 'stretch_both'
        )
        
        # Return the graphic
        return wall_graphic
    
    def _CreateWallGraphicCallback(self,data):
        """
        _CreateWallGraphicCallback (Private)
        Callback method to update the walll graphic

        Arguments: N/A

        Returns:
            - hv.Overlay || Overlay of robot position and wall visualisation
        """

        # Test is used to ensure the array is not empty
        test = False

        # Check if the array actually has data - update test if so
        # This is used as the data may be a 0d-array, which then throws errors when drawing the graph
        # hence the test to see if the data has more than 0 dimensions
        try:
            _ = data[0]
            test = True
        except:
            pass

        # Create the robot location sactter, this indicates the position of the lidar
        robot_loc = hv.Scatter([(0,0)],kdims=['x','y'],label='Robot Centre').opts(color='blue',marker='star',size=10,aspect=None,tools=['hover'])

        # If data was found, and there is more than one item
        if test and data.size > 0:

            # Create an overlay, with a inner function which draws each line
            # this is done to ensure that the legend contains the wall names
            overlay = hv.Overlay([
                hv.Segments([[x,y,x1,y1,name]],
                    kdims=['x','y','x1','y1'],
                    vdims=['Name'],
                    label=name
                ).opts(
                    color=hv.Cycle('Muted'), # Cycled colour list, ensures all walls have different colour contrasts
                    line_width=4,
                    tools=['hover'],
                    hover_tooltips = ["Name"],
                )
                for x,y,x1,y1,name in data
            ]).opts(
                legend_position='right',
                show_legend=True,
                aspect=None,
                tools=['hover'],
            )
            # Return a combination of the overlay and robot location
            return overlay * robot_loc
            
        else: 
            # Return the robot location
            return hv.Overlay([]) * robot_loc

    def _CreateWallSelection(self):
        """
        _CreateWallSelection (Private)
        Method to create options for wall selection

        Arguments: N/A

        Returns: pnw.Select : self.wall_select || Selection box with options for each wall

        """
        # Create visual
        self.wall_select = pnw.Select(name="Select Wall to Paint",options = [1,2,3,4],align='center',sizing_mode='stretch_width')

        # Return visual
        return self.wall_select
    
    def _CreateWallSelectionCallback(self):
        """
        _CreateWallSelectionCallback (Private)
        Callback method for Wall Selection, updates options based on available walls

        Arguments: N/A

        Returns: N/A
        """
        # Get data
        data = self.node_handler.GetData('Wall_Visual')

        # Retrieve wall names
        wall_options = []

        # If there is no data
        if (len(data) == 0):

            # Set the options to below
            # NOTE: This is used as a checker to prevent actions from being made, modifications to this text will require updating action_handler
            wall_options.append("No Walls Identified, please move to better position")
            
            # If no notifications have been made, make one - stop another from being made after (until a rescan is completed)
            # Prevents spam of notifications that no wall exists
            if (not self.no_walls_notified):
                self.gui.Notify(type='Warning',msg=f'WARNING: No walls identified, please move to a better position then rescan',time=10000)
                self.no_walls_notified = True
            
        # Loop through each item and add it (Note, if items DO not exist, the loop is skipped)
        for item in data:
            wall_options.append(item[4]) # Item = [x0,y0,x1,y1,name,orientation]

        # Update the graphic to display wall names
        self.wall_select.options = wall_options

    def _CreateWallRescan(self):
        """
        _CreateWallRescan (Private)
        Method to create visual for rescanning walls

        Arguments: N/A

        Returns:
            - pnw.Button : wall_rescan || Visual button for rescanning walls
        """
        # Create visual
        wall_rescan = pnw.Button(name='Rescan for walls',button_type = self.styles['buttons'][0],button_style=self.styles['buttons'][1],align='center')
        
        #Establish link to callback
        wall_rescan.on_click(self._CreateWallRescanCallback)

        # Return visual
        return wall_rescan

    def _CreateWallRescanCallback(self):
        """
        _CreateWallRescanCallback (Private)
        Callback method for rescanning for walls

        Arguments: N/A

        Returns: N/A
        """
        # Notify action handler of rescan
        self.action_handler.Rescan()

        # Set notifcation to false, can notify if no walls are detected
        self.no_walls_notified = False

        # Announce that we are rescanning for walls
        self.node_handler.Publish('Rescan',True)

        # Notify that we are rescanning
        self.gui.Notify(type="Info",msg=f'INFO: Rescanning for walls... ',time=3000)
    
    def _CreateWallRescanPeriodicCallback(self):
        """
        _CreateWallRescanPeriodicCallback (Private)
        Callback method for periodic publish of rescanning

        Arguments: N/A

        Returns: N/A
        """
        # Publish rescan is false, as aa single change will trigger a rescan
        # we don't want that single call to repeatedly rescan - only once
        self.node_handler.Publish('Rescan',False)

    def _CreateCommandsEm(self):
        """
        _CreateCommandsEm (Private)
        Method to create Emergency Commands

        Arguments: N/A

        Returns:
            - pn.Column : emergency_commands || Column containing play, stop and skip commands

        """
        
        # Create buttons
        self.command_action_play_em = pnw.ButtonIcon(icon='player-play',size=self.styles['emergency_command'])
        self.command_action_stop_em = pnw.ButtonIcon(icon='player-stop',size=self.styles['emergency_command'])
        self.command_action_skip_em =  pnw.ButtonIcon(icon='player-skip-forward',size=self.styles['emergency_command'])
        self.command_action_stop_em.visible = False

        # Link button clicks to callback
        self.command_action_play_em.on_click(lambda exec : self._CreateCommandsCallback(caller='Play'))
        self.command_action_stop_em.on_click(lambda exec : self._CreateCommandsCallback(caller='Stop'))
        self.command_action_skip_em.on_click(lambda exec : self._CreateCommandsCallback(caller='Skip'))

        # Arrange buttons 
        emergency_commands = pn.Column(
            pnp.Markdown("**Commands**",styles=self.styles['markdown_text_title']),
            pn.Row(
                self.command_action_play_em,
                self.command_action_stop_em,
                self.command_action_skip_em,
                align='center'
            )
        )

        # Return data
        return emergency_commands

    def _CreateCommands(self):
        """
        _CreateCommands (Private)
        Method to create action commands

        Arguments: N/A

        Returns: pn.Column : comands || Column containing play, stop and skip commands

        """
        # Create pause, play and skip buttons
        self.command_action_play = pnw.ButtonIcon(icon='player-play',size=self.styles['command'],align='center')
        self.command_action_stop = pnw.ButtonIcon(icon='player-stop',size=self.styles['command'],align='center')
        self.command_action_skip =  pnw.ButtonIcon(icon='player-skip-forward',size=self.styles['command'],align='center')
        
        # hide the stop button, as no actions would have been started yet
        self.command_action_stop.visible = False

        # Link all buttons on-click event to the dedicated callback
        self.command_action_play.on_click(lambda exec : self._CreateCommandsCallback(caller='Play'))
        self.command_action_stop.on_click(lambda exec : self._CreateCommandsCallback(caller='Stop'))
        self.command_action_skip.on_click(lambda exec : self._CreateCommandsCallback(caller='Skip'))

        # Create visual for commands
        commands = pn.Column(pn.Row(
                self.command_action_play,
                self.command_action_stop,
                self.command_action_skip,
                align='center',
                sizing_mode='stretch_width'
            ),
            align='center',
            sizing_mode = 'stretch_both'
            )
        
        # Return commands
        return commands

    def _CreateCommandsCallback(self,caller):
        """
        _CreateCommandsCallback (Private)
        Callback method for Emergency and regular commands, performs actions based on what called it

        Arguments:
            - str : caller || Which command button called this function

        Returns: N/A

        """

        if caller == 'Play' and len(self.action_handler.planned_actions) > 0:
            # Hide play button, present the stop button
            self.command_action_play_em.visible=False
            self.command_action_stop_em.visible = True

            self.command_action_play.visible = False
            self.command_action_stop.visible = True

            # Call GUI to start action
            self.action_handler.PlayAction()
            self.gui.Notify(type="Info",msg=f'INFO: Action has begun',time=3000)

        elif caller == 'Stop':
            # Hide stop button, present play button
            self.command_action_play_em.visible=True
            self.command_action_stop_em.visible = False

            self.command_action_play.visible = True
            self.command_action_stop.visible = False
            
            # Call GUI to pause the action
            self.action_handler.PauseAction()
            self.gui.Notify(type="Info",msg=f'INFO: Action has paused',time=3000)

        elif caller == 'Skip' and len(self.action_handler.planned_actions) > 1:
            self.command_action_play_em.visible=True
            self.command_action_stop_em.visible = False

            self.command_action_play.visible = True
            self.command_action_stop.visible = False
            
            # Call GUI to move onto the next action
            self.action_handler.SkipAction()
            self.gui.Notify(type="Info",msg=f'INFO: Action has been skipped',time=3000)

        elif caller == 'terminate':
            self.command_action_play_em.visible=True
            self.command_action_stop_em.visible = False

            self.command_action_play.visible = True
            self.command_action_stop.visible = False
            # Set current action to None, throw warning about termination
            
        elif caller == 'complete':
            self.command_action_play_em.visible=True
            self.command_action_stop_em.visible = False

            self.command_action_play.visible = True
            self.command_action_stop.visible = False
            # Notify of completion, load next action
            
            # Call gui to start the next action
            self.gui.SkipAction()
            self.gui.Notify(type="Info",msg=f'INFO: Action has completed',time=3000)

        else:
            pass

    
