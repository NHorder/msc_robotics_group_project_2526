################################
# action_handler.py
# Part of the user_interface_py_pkg
#
# Author: Nathan Horder (nathan.horder.700@cranfield.ac.uk)
# Part of Cranfield University MSC Robotics Group Project 2025-2026
################################
#%%
import panel as pn
import panel.widgets as pnw
from panel import pane as pnp
from panel import layout as pnl

"""
Action
Class to contain 'action' related data
"""
class Action():

    def __init__(self,name:str,wall:str):
        self.name = name
        self.wall = wall
    
"""
ActionHandler
Class to handle wanted user action (I.e paint wallA, then wallB, etc)
"""
class ActionHandler():

    def __init__(self,styles=None,dev_mode=False):

        # If styles is None, define default
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

        # Dev mode is used to remove certain restrictions within the system, I.e creating actions when walls are not present
        self.dev_mode = dev_mode

        # Define the active action - this is the action the robot is currently performing
        self.active_action = None

        # Define the planned actions, these are all actions the robot will complete in order
        self.planned_actions = []

        # Define visual component of planned actions
        self.graphics_list = pn.Column(align='center',sizing_mode= 'stretch_both',scroll = True,height_policy="max")
        self.graphics_list.append(pnp.Markdown("No Actions Planned",styles={'font-size': '11pt'},align='center'))
        
        # Define a minimised visual component of planned actions (contains current and next ONLY)
        self.reduced_graphics_list = pn.Column(align='center',sizing_mode= 'stretch_both',scroll = True,height_policy="max")
        self.reduced_graphics_list.append(pnp.Markdown("No Actions Planned",styles={'font-size': '11pt'},align='center'))

        # Define action counter
        self.counter = 0

        self.initialising = True
    
    def CreateGraphics(self,ui_helper):
        """
        CreateGraphics (Public)
        Method to generate graphics for action control

        Arguments
            - GUI_Helper : ui_helper || Link to GUI_Helper to retrieve specific graphics 

        Returns:
            - tuple : (pn.WidgetBox: action_area, pn.Column: self.reduced_graphics_list, pn.Column: self.progress) || Returns 3 visuals, action creation area, a minimal action presention and progress for current action

        """
        # Acquire graphics dictionary from the UI helper
        self.helper_graphics = ui_helper.graphics

        # Set wall name, wall selection and action location
        self.action_name = pnw.TextInput(name="Action Name:",placeholder="Action X",align='center') 
        self.wall_select = self.helper_graphics["Wall_Selection"]                               # WHERE to perform action
        self.action_location = pnw.Select(name="Select when to perform action",options=["Now"]) # WHEN to perform action

        # Code to generate the modify or create action area
        action_planner_name = pnp.Markdown("**Action Planner**",styles=self.styles['markdown_text_title'],align='center')

        # A confirm button is needed, else when one of name, wall select, action loc are selected a new action would be created.
        confirm_button = pnw.Button(name="Save Action",button_type="success",button_style=self.styles['buttons'][1],align='center')

        # Conglomerate all the widgets into a dedicated area
        creation_area = pn.WidgetBox(
            action_planner_name,
            self.action_name,
            self.wall_select,
            self.action_location,
            pn.Row(confirm_button,self.helper_graphics['Rescan'],align='center'),
            pn.bind(self.CreateAction,button = confirm_button),
            sizing_mode='stretch_width',
            align= 'center'
        )

        # Define action area - this involves the house plan and existing action list
        action_area = pn.WidgetBox(
            self.graphics_list,
            pnl.Divider(),
            creation_area,
            sizing_mode='stretch_width',
            align = 'center'
        )

        # Progress
        self.progress = pn.Column(
            pnp.Markdown("**Progress**",styles=self.styles['markdown_text_title'],align='center'),
            pnp.Markdown("No Task in Progress",styles=self.styles['markdown_text_reg'],align='center'),
            pnp.Markdown("",styles=self.styles['markdown_text_reg'],align='center'),
            pnp.Markdown("Progress: N/A ",styles = self.styles['markdown_text_reg'],align='center'),
            sizing_mode = 'stretch_width',
            align='center',
        )


        self.initialising = False

        return action_area, self.reduced_graphics_list, self.progress

    def CreateAction(self, button):
        """
        CreateAction (Public)
        Method to create an action

        Arguments
            - <unknown>: button: Ignored input, required by Panel for button link

        Returns: N/A
        """
        if self.initialising:
            return
        
        # Acquire values for name, wall and action placement
        name = self.action_name.value
        wall = self.wall_select.value
        idx = self.action_location.value

        # Prevent action from being created if there are no walls that have been identified
        if not self.dev_mode and wall == "No Walls Identified, please move to better position":
            # Don't do anything, WE NEED WALLS to make any action
            # UI helper handles notification of this
            return 
       
        # Update counter for total actions created
        self.counter +=1 

        ## Create Action

        # If no name provided, use a default name of "Action X", where X is how many actions already exist
        if (name == ""): name = "Action "+str(self.counter)
        action = Action(name,wall)

        ## Create Action Visual

        # Creation of visual
        edit_button = pnw.ButtonIcon(icon='edit',size="2em",align="center")
        delete_button = pnw.ButtonIcon(icon='trash',size="2em",align="center")

        # Create visual
        visual = pn.WidgetBox(pn.Row(
            pnp.Markdown(f"{name} || Wall: {wall}",styles={'font-size': '11pt'},align="center"),
            edit_button,
            delete_button,
            sizing_mode='stretch_width'
        ))


        ## Place into list(s)
        # graphic list mirrors planned action

        # If there are no items in the list, it's gonna be appended (then update the visual)
        if (len(self.planned_actions) <= 0):
            self.graphics_list.pop(0)

            self.planned_actions.append(action)
            self.graphics_list.append(visual)
            self._UpdateFirstItem()

        elif (idx == 'Now'):
            # IF now, insert at first location
            # Already done checks to ensure there is at least one item in the list
            self.planned_actions.insert(0,action)
            self.graphics_list.insert(0,visual)

            # Update first graphic
            self._UpdateFirstItem()
            self._UpdateMovedItem()
        
        elif (idx == 'Next'):
            self.planned_actions.insert(1,action)
            self.graphics_list.insert(1,visual)
        
        elif (idx == 'Later' or int(idx) >= len(self.planned_actions)):
            # If the idx is Later or if its larger than expected, add to end 
            self.planned_actions.append(action)
            self.graphics_list.append(visual)

        else:
            # Else, convert place it at the index
            # Casting is now safe (as 'Later' and 'Now' have been checked for)
            self.planned_actions.insert(int(idx),action)
            self.graphics_list.insert(int(idx),visual)
        
        # Call update to options - updates the graphic for wall options
        self._UpdateOptions()

        # Call update for minimal graphics list (in instances where the current action or next action has been replaced or changed)
        self._UpdateMinimalGraphicsList()

        # Link edit and delete buttons to related actions
        edit_button.on_click(lambda exec : self.EditAction(action))
        delete_button.on_click(lambda exec : self.DeleteAction(action))

    def _UpdateFirstItem(self):
        """
        _UpdateFirstItem (Private)
        Method to update the visual for the first action in the planned_action list

        Arguments: N/A

        Returns: N/A
        """

        # Check if there is an item
        if (len(self.planned_actions) > 0):
            # Acquire first action
            action = self.planned_actions[0]

            # Re-create the first graphic (different from standardised graphic)
            first_item = pn.WidgetBox(
                    pnp.Markdown(f"**Current Action**:   {action.name} || Wall: {action.wall}",styles={'font-size': '11pt'},align="center"),
                    self.helper_graphics["Commands"],
                    pnl.Divider(),
                    align='center',
                    sizing_mode='stretch_width'
                )
            
            # Overwrite the first graphic
            self.graphics_list[0] = first_item

    def _UpdateMovedItem(self):
        """
        _UpdateMovedItem (Private)
        Method to update the visual for a moved item

        Arguments: N/A

        Returns: N/A
        """
        # Acquire the next action
        action = self.planned_actions[1]

        # Creation of visual
        edit_button = pnw.ButtonIcon(icon='edit',size="2em",align="center")
        delete_button = pnw.ButtonIcon(icon='trash',size="2em",align="center")

        # Update the visual
        visual = pn.WidgetBox(pn.Row(
            pnp.Markdown(f"{action.name} || Wall: {action.wall}",styles={'font-size': '11pt'},align="center"),
            edit_button,
            delete_button,
            sizing_mode='stretch_width'
        ))

        # Link edit and delete buttons
        edit_button.on_click(lambda exec : self.EditAction(action))
        delete_button.on_click(lambda exec : self.DeleteAction(action))

        # Update the graphics list of update
        self.graphics_list[1] = visual

    def _UpdateOptions(self):
        """
        _UpdateOptions (Private)
        Method to update options for placement of next action

        Arguments: N/A

        Returns: N/A
        """
        # Do loop to update action_location
        opts = []
        for idx in range(len(self.planned_actions)):
            if idx == 0:
                opts.append('Now')
            elif idx == 1:
                opts.append('Next')
            else:
                opts.append(idx)

        # Minor implementation for semantic text
        if (len(self.planned_actions) == 1): opts.append("Next")
        else: opts.append('Later') # Later does refer to end of list
        self.action_location.options = opts
    
    def _UpdateMinimalGraphicsList(self):
        """
        _UpdateMinimalGraphicsList (Private)
        Method for dynamically updating the minimal display of planned actions

        Arguments: N/A

        Returns: N/A
        """
        # Empty the list
        self.reduced_graphics_list.clear()

        # Retrieve data from main list
        data = self.graphics_list[:2]

        # If there is one item, just append it
        if len(data) == 1:
            self.reduced_graphics_list.append(data[0])
        
        # If there are more than two items, re-create the next item (idx = 1)
        elif (len(data) >= 2):
            # Append the first item (current action)
            self.reduced_graphics_list.append(data[0])

            # Prepare the next action visual
            action = self.planned_actions[1]
            next_item = pn.WidgetBox(
                    pnp.Markdown(f"**Next Action**:   {action.name} || Wall: {action.wall}",styles={'font-size': '11pt'},align="center"),
                    pnl.Divider(),
                    align='center',
                    sizing_mode='stretch_width'
                )
            
            # Append to list
            self.reduced_graphics_list.append(next_item)


    def EditAction(self,action):
        """
        EditAction (Public)
        Method for preparing actions to be updated

        NOTE: Removes action from list, updates creation area with values

        Arguments: N/A

        Returns: N/A
        """
        if self.initialising:
            return
        
        # Identify index of the action to edit
        idx = self.planned_actions.index(action)

        # Delete action from list
        self.planned_actions.pop(idx)
        self.graphics_list.pop(idx)

        # Update planner graphic
        self.wall_select.value = action.wall
        self.action_name.value = action.name

    def DeleteAction(self,item):
        """
        DeleteAction (Public)
        Method to delete actions

        Arguments
            - int : item || Index of item to remove

        Returns: N/A
        """
        if self.initialising:
            return
        
        idx = self.planned_actions.index(item)

        # Delete action from list
        self.planned_actions.pop(idx)
        self.graphics_list.pop(idx)

        # if there are no planned actions, then append "No Actions Planned" to the visual graphic
        if (len(self.planned_actions) < 1):
            self.graphics_list.append(pnp.Markdown("No Actions Planned",styles={'font-size': '11pt'},align='center'))

    def ConcludeAction(self):
        """
        ConcludeAction (Public)
        Method to end the current action

        Arguments: N/A

        Returns: N/A
        """
        # Delete action from list
        self.DeleteAction(0)

        # Set no action selected, as the current action has concluded
        self.progress[1] = pnp.Markdown("No Action Selection",styles = self.styles['markdown_text_reg'],align='center')
        self.progress[2] = pnp.Markdown("",styles = self.styles['markdown_text_reg'],align='center')
        self.progress[3] = pnp.Markdown("Progress: N/A",styles = self.styles['markdown_text_reg'],align='center')

        # Update visual of following action
        self._UpdateFirstItem()


    def PlayAction(self):
        """
        PlayAction (Public)
        Method to set begin execution of current action

        Arguments: N/A

        Returns: N/A
        """
        if not self.initialising:
            # Assume first action is always the current action

            # Check if there are any planned actions, and there is no active action
            if len(self.planned_actions) > 0 and self.active_action == None:
                self.active_action = self.planned_actions[0]
                self.progress[1] = pnp.Markdown(f"**Action**:  {self.active_action.name} || Wall: {self.active_action.wall}",styles = self.styles['markdown_text_reg'],align='center')
                self.progress[2] = pnp.Markdown(f"**Status**: Active",styles = self.styles['markdown_text_reg'],align='center')
                self.progress[3] = pnp.Markdown("Progress:  0%",styles = self.styles['markdown_text_reg'],align='center')
            else:
                pass

    def PauseAction(self):
        """
        PauseAction (Public)
        Method to pause the current action
        NOTE: Sets active action to None

        DEV NOTE: Potential issue for restarting tasks, as prior information is not handled - progress tracker is maintained, but only locally

        Arguments: N/A

        Returns: N/A

        """
        if not self.initialising:
            # If there is an active action, set it to None
            # Stopping the sequence
            if self.active_action != None:
                self.progress[2] = pnp.Markdown(f"**Status**: Paused",styles = self.styles['markdown_text_reg'],align='center')
                self.active_action = None
            else:
                pass

    def SkipAction(self):
        """
        SkipAction
        Method to conclude current action and prepare for next action

        Arguments: N/A

        Returns: N/A

        """
        self.active_action = None
        self.ConcludeAction()

    def Rescan(self):
        """
        Rescan
        Method following execution of rescan

        Arguments: N/A

        Returns: N/A

        """
        
        # Since we are rescanning the walls, all previous information becomes redundant
        # cannot confirm that Wall A in previous scan is same wall in new scan, hence reset

        # Set current action to None
        self.active_action = None
        # Clear list
        self.planned_actions.clear()

        self._UpdateFirstItem()
        self._UpdateMovedItem()
        self._UpdateOptions()
        self._UpdateMinimalGraphicsList()

        # Set no action selected
        self.progress[1] = pnp.Markdown("No Action Selection",styles = self.styles['markdown_text_reg'],align='center')
        self.progress[2] = pnp.Markdown("",styles = self.styles['markdown_text_reg'],align='center')
        self.progress[3] = pnp.Markdown("Progress: N/A",styles = self.styles['markdown_text_reg'],align='center')
        
    def _RetrieveActionProgress(self):
        """
        _RetrieveActionProgress
        Method to dynamically update progress visual

        Arguments: N/A

        Returns: N/A

        NOTE: Development in Progress
        """
        pass

