import rclpy
import numpy as np
import asyncio
import logging
import holoviews as hv
import panel as pn 
import pandas as pd
import threading
import asyncio
from node_handler import NodeHandler
from PIL import Image
from holoviews.streams import Pipe
from panel import pane as pnp
from panel import layout as pnl
from panel import widgets as pnw
pn.extension(notifications=True)
pn.extension('terminal')
hv.extension('bokeh')
 

class GUI_Helper():
    
    def __init__(self,gui, node_handler,action_handler, styles=None,dev_mode=False):
        self.gui = gui
        self.node_handler = node_handler
        self.action_handler = action_handler
        self.dev_mode = dev_mode
        
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



    def StartTimers(self):
        pn.state.add_periodic_callback(self._CreateCameraImageCallback,100)
        pn.state.add_periodic_callback(self._SystemHealthCallback,500)
        pn.state.add_periodic_callback(self._CreateWallSelectionCallback,500)

    def CreateGraphics(self):
        self.graphics = {}
        self.graphics["Lidar"] = self._CreateLidarGraph()
        self.graphics["Camera"] = self._CreateCameraImage()
        self.graphics["SystemHealth"] = self._CreateSystemHealth()
        self.graphics["Wall_Visual"] = self._CreateWallGraphic()
        self.graphics["Wall_Selection"]= self._CreateWallSelection()
        self.graphics["Emergency_Commands"] = self._CreateCommandsEm()
        self.graphics["Commands"] = self._CreateCommands()

        actions = self.action_handler.CreateGraphics(self)
        self.graphics["Actions"] = actions[0]
        self.graphics["Actions_Mini"] = actions[1]
        self.graphics["Action_Progress"] = actions[2]

        return self.graphics


    def _CreateLidarGraph(self):
        lidar_pipe = Pipe(data = [])
        task = asyncio.create_task(self.node_handler.GetDataAsync('Lidar',lidar_pipe))
        lidar_dmap = hv.DynamicMap(hv.Scatter,streams=[lidar_pipe]).opts(responsive=True,color='black')
        robot_loc = hv.Scatter([(0,0)],label='Robot Centre').opts(color='blue',marker='star',size=10)
        lidar_scatter = pnl.WidgetBox(
            pnp.Markdown("**2D LiDAR**",styles=self.styles['markdown_text_title']),
            (lidar_dmap*robot_loc),sizing_mode='stretch_both')
        
        return lidar_scatter
    
    def _CreateCameraImage(self):
        self.camera_img = pnp.Image(sizing_mode='scale_both')

        return pn.WidgetBox(pnp.Markdown("**RGB-D Camera**",styles=self.styles['markdown_text_title']),
                            self.camera_img,
                            sizing_mode='stretch_both')
    
    def _CreateCameraImageCallback(self):
        data = self.node_handler.GetData('Camera')
        if data is not None and data != []:
            img = Image.fromarray(data)
            self.camera_img.object = img

    def _CreateSystemHealth(self):
        self.system_health = pn.Column(
            pnp.Markdown("**System Health**",styles=self.styles['markdown_text_title'],align='center'),
            pnl.Divider(),
            sizing_mode='stretch_both',
            scroll=True
        )

        return self.system_health

    def _SystemHealthCallback(self):
        data = self.node_handler.GetData('SysHP')

        if len(self.system_health) < 2:
            print("???")
            for key in data.keys():
                self.system_health.append(
                    pnp.Markdown(f"{key} : {data[key]}",self.styles['markdown_text_reg'])
                )
        else:
            i = 2
            for key in data.keys():
                self.system_health[i](
                    pnp.Markdown(f"{key} : {data[key]}",self.styles['markdown_text_reg'])
                )
                i+=1
                
        self.system_health.sizing_mode = 'stretch_both'
        self.system_health.scroll = True

    def _CreateWallGraphic(self):
        pipe = Pipe(data=[])
        task = asyncio.create_task(self.node_handler.GetDataAsync('Wall_Visual',pipe))
        # Create Dynamic map
        dmap = hv.DynamicMap(self._CreateWallGraphic_Callback,streams = [pipe]).opts(responsive=True)

        wall_graphic = pnl.WidgetBox(
            pnp.Markdown("**Room Walls**",styles=self.styles['markdown_text_title']),
            (dmap), sizing_mode = 'stretch_both'
        )
        
        return wall_graphic
    
    def _CreateWallGraphic_Callback(self,data):

        test = False

        # Check if the array actually has data - update test if so
        # This is used as the data may be a 0d-array, which then throws errors when drawing the graph
        # hence the test to see if the data has more than 0 dimensions
        try:
            _ = data[0]
            test = True
        except:
            pass

        robot_loc = hv.Scatter([(0,0)],label='Robot Centre').opts(color='blue',marker='star',size=10)

        if test and data.size > 0:
            overlay = hv.Overlay([
                hv.Segments([[x,y,x1,y1]],
                    kdims=['x','y','x1','y1'],
                    label=name
                ).opts(
                    color=hv.Cycle('Spectral'),
                    line_width=4
                )
                for x,y,x1,y1,name in data
            ]).opts(
                tools=['hover'],
                legend_position='right',
                show_legend=True,
                aspect='equal'
            )
            
            return overlay * robot_loc
            
        else: 
            
            return hv.Overlay([]) * robot_loc

        
    def _CreateWallSelection(self):
        self.wall_select = pnw.Select(name="Select Wall to Paint",options = [1,2,3,4],align='center')

        return self.wall_select
    
    def _CreateWallSelectionCallback(self):
        
        # Get data
        data = self.node_handler.GetData('Wall_Visual')

        # Retrieve wall names
        wall_options = []

        if (len(data) == 0):
            wall_options.append("No Walls Identified, please move to better position")

        for item in data:
            wall_options.append(item[4]) # Item = [x0,y0,x1,y1,name,orientation]

        # Update the graphic to display wall names
        self.wall_select.options = wall_options
    

    def _CreateCommandsEm(self):

        self.command_action_play_em = pnw.ButtonIcon(icon='player-play',size=self.styles['emergency_command'])
        self.command_action_stop_em = pnw.ButtonIcon(icon='player-stop',size=self.styles['emergency_command'])
        self.command_action_skip_em =  pnw.ButtonIcon(icon='player-skip-forward',size=self.styles['emergency_command'])
        self.command_action_stop_em.visible = False

        self.command_action_play_em.on_click(lambda exec : self._CreateCommandsCallback(caller='Play'))
        self.command_action_stop_em.on_click(lambda exec : self._CreateCommandsCallback(caller='Stop'))
        self.command_action_skip_em.on_click(lambda exec : self._CreateCommandsCallback(caller='Skip'))

        emergency_commands = pn.Column(
            pnp.Markdown("**Commands**",styles=self.styles['markdown_text_title']),
            pn.Row(
                self.command_action_play_em,
                self.command_action_stop_em,
                self.command_action_skip_em,
                align='center'
            )
        )

        return emergency_commands

    def _CreateCommands(self):
        self.command_action_play = pnw.ButtonIcon(icon='player-play',size=self.styles['command'],align='center')
        self.command_action_stop = pnw.ButtonIcon(icon='player-stop',size=self.styles['command'],align='center')
        self.command_action_skip =  pnw.ButtonIcon(icon='player-skip-forward',size=self.styles['command'],align='center')
        self.command_action_stop.visible = False

        self.command_action_play.on_click(lambda exec : self._CreateCommandsCallback(caller='Play'))
        self.command_action_stop.on_click(lambda exec : self._CreateCommandsCallback(caller='Stop'))
        self.command_action_skip.on_click(lambda exec : self._CreateCommandsCallback(caller='Skip'))

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
        

        return commands

    def _CreateCommandsCallback(self,caller):

        if caller == 'Play' and len(self.action_handler.planned_actions) > 0:
            # Hide play button, present the stop button
            self.command_action_play_em.visible=False
            self.command_action_stop_em.visible = True

            self.command_action_play.visible = False
            self.command_action_stop.visible = True

            # Call GUI to start action
            self.action_handler.PlayAction()

        elif caller == 'Stop':
            # Hide stop button, present play button
            self.command_action_play_em.visible=True
            self.command_action_stop_em.visible = False

            self.command_action_play.visible = True
            self.command_action_stop.visible = False
            
            # Call GUI to pause the action
            self.action_handler.PauseAction()

        elif caller == 'Skip' and len(self.action_handler.planned_actions) > 0:
            self.command_action_play_em.visible=True
            self.command_action_stop_em.visible = False

            self.command_action_play.visible = True
            self.command_action_stop.visible = False
            
            # Call GUI to move onto the next action
            self.action_handler.SkipAction()

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

        else:
            pass

