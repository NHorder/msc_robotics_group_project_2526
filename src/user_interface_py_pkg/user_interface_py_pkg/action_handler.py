
#%%
import panel as pn
import panel.widgets as pnw
from panel import pane as pnp
from panel import layout as pnl


class Action():

    def __init__(self,name:str,wall:str):
        self.name = name
        self.wall = wall
    

class Action_Handler():

    def __init__(self,styles=None,dev_mode=False):

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

        self.dev_mode = dev_mode

        self.active_action = None

        self.planned_actions = []
        self.graphics_list = pn.Column(align='center',sizing_mode= 'stretch_both',scroll = True,height_policy="max")
        self.graphics_list.append(pnp.Markdown("No Actions Planned",styles={'font-size': '11pt'},align='center'))

        self.reduced_graphics_list = pn.Column(align='center',sizing_mode= 'stretch_both',scroll = True,height_policy="max")
        self.reduced_graphics_list.append(pnp.Markdown("No Actions Planned",styles={'font-size': '11pt'},align='center'))

        self.counter = 0

        self.initialising = True
    
    def CreateGraphics(self,helper_graphics):
        self.helper_graphics = helper_graphics.graphics

        self.action_name = pnw.TextInput(name="Action Name:",placeholder="Action X",align='center')
        self.wall_select = self.helper_graphics["Wall_Selection"]
        self.action_location = pnw.Select(name="Select when to perform action",options=["Now"])

        # Code to generate the modify or create action area
        action_planner_name = pnp.Markdown("**Action Planner**",styles=self.styles['markdown_text_title'],align='center')
        
        confirm_button = pnw.Button(name="Save Action",button_type="success",button_style=self.styles['buttons'][1],align='center')

        # Conglomerate all the widgets into a dedicated area
        creation_area = pn.WidgetBox(
            action_planner_name,
            self.action_name,
            self.wall_select,
            self.action_location,
            confirm_button,
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
        if self.initialising:
            return
        
        name = self.action_name.value
        wall = self.wall_select.value
        idx = self.action_location.value


        if not self.dev_mode and wall == "No Walls Identified, please move to better position":
            # Throw warning

            # Then don't do anything, WE NEED WALLS to make any action
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
            self.UpdateFirstItem()

        elif (idx == 'Now'):
            # IF now, insert at first location
            # Already done checks to ensure there is at least one item in the list
            self.planned_actions.insert(0,action)
            self.graphics_list.insert(0,visual)

            # Update first graphic
            self.UpdateFirstItem()
            self.UpdateMovedItem()
        
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
        

        self.UpdateOptions()
        self.UpdateMinimalGraphicsList()

        # Shite - needs to know where it is at all times
        edit_button.on_click(lambda exec : self.EditAction(action))
        delete_button.on_click(lambda exec : self.DeleteAction(action))

    def UpdateFirstItem(self):

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

    def UpdateMovedItem(self):
        action = self.planned_actions[1]

        # Creation of visual
        edit_button = pnw.ButtonIcon(icon='edit',size="2em",align="center")
        delete_button = pnw.ButtonIcon(icon='trash',size="2em",align="center")

        visual = pn.WidgetBox(pn.Row(
            pnp.Markdown(f"{action.name} || Wall: {action.wall}",styles={'font-size': '11pt'},align="center"),
            edit_button,
            delete_button,
            sizing_mode='stretch_width'
        ))

        edit_button.on_click(lambda exec : self.EditAction(action))
        delete_button.on_click(lambda exec : self.DeleteAction(action))

        self.graphics_list[1] = visual

    def UpdateOptions(self):
        # Do loop to update action_location
        opts = []
        for idx in range(len(self.planned_actions)):
            if idx == 0:
                opts.append('Now')
            elif idx == 1:
                opts.append('Next')
            else:
                opts.append(idx)

        if (len(self.planned_actions) == 1): opts.append("Next")
        else: opts.append('Later')
        self.action_location.options = opts
    
    def UpdateMinimalGraphicsList(self):
        self.reduced_graphics_list.clear()

        data = self.graphics_list[:2]

        if len(data) == 1:
            self.reduced_graphics_list.append(data[0])
        elif (len(data) >= 2):
            self.reduced_graphics_list.append(data[0])

            action = self.planned_actions[1]
            next_item = pn.WidgetBox(
                    pnp.Markdown(f"**Next Action**:   {action.name} || Wall: {action.wall}",styles={'font-size': '11pt'},align="center"),
                    pnl.Divider(),
                    align='center',
                    sizing_mode='stretch_width'
                )
            
            self.reduced_graphics_list.append(next_item)


    def EditAction(self,action):
        if self.initialising:
            return
        
        idx = self.planned_actions.index(action)

        # Delete action from list
        self.planned_actions.pop(idx)
        self.graphics_list.pop(idx)

        # Update planner graphic
        self.wall_select.value = action.wall
        self.action_name.value = action.name

    def DeleteAction(self,item):
        if self.initialising:
            return
        
        idx = self.planned_actions.index(item)

        # Delete action from list
        self.planned_actions.pop(idx)
        self.graphics_list.pop(idx)

        if (len(self.planned_actions) < 1):
            self.graphics_list.append(pnp.Markdown("No Actions Planned",styles={'font-size': '11pt'},align='center'))

    def ConcludeAction(self):
        # Delete action from list
        self.DeleteAction(0)

        self.progress[1] = pnp.Markdown("No Action Selection",styles = self.styles['markdown_text_reg'],align='center')
        self.progress[2] = pnp.Markdown("",styles = self.styles['markdown_text_reg'],align='center')
        self.progress[3] = pnp.Markdown("Progress: N/A",styles = self.styles['markdown_text_reg'],align='center')

        # Update visual of following action
        self.UpdateFirstAction()


    def PlayAction(self):
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
        if not self.initialising:
            # If there is an active action, set it to None
            # Stopping the sequence
            if self.active_action != None:
                self.progress[2] = pnp.Markdown(f"**Status**: Paused",styles = self.styles['markdown_text_reg'],align='center')
                self.active_action = None
            else:
                pass

    def SkipAction(self):
        self.active_action = None
        self.ConcludeAction()


    def RetrieveActionProgress(self):
        pass

