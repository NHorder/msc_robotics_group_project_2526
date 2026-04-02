import rclpy
import numpy as np
import asyncio
import logging
import holoviews as hv
import panel as pn 
import pandas as pd
import threading
from action import Action
from node_handler import NodeHandler
from holoviews.streams import Pipe
from panel import pane as pnp
from panel import layout as pnl
from panel import widgets as pnw
pn.extension(notifications=True)
pn.extension('terminal')
hv.extension('bokeh')
import asyncio
 

class GUI_Helper():
    
    def __init__(self,node_handler,styles):
        self.node_handler = node_handler
        self.styles = styles

    def CreateGraphics(self):
        self.graphics = {}
        self.graphics["Lidar"] = self._CreateLidarGraph()
        self.graphics["SystemHealth"] = self._CreateSystemHealth()


        self.graphics["Wall_Visual"] = self._CreateWallGraphic()
        self.graphics["Wall_Selection"]= self._CreateWallSelection()


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

    def _CreateSystemHealth(self):
        self.system_health = pn.Column(
            pnp.Markdown("**System Health**",styles=self.styles['markdown_text_title'],align='center'),
            pnl.Divider(),
            sizing_mode='stretch_both',
            scroll=True
        )

        pn.state.add_periodic_callback(self._SystemHealthCallback,500)

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

        if test and data.size > 0:
            overlay = hv.Overlay([
                hv.Segments([[x0,y0,x1,y1]],
                    kdims=['x0','y0','x1','y1'],
                    label=name
                ).opts(
                    color=hv.Cycle('Spectral'),
                    line_width=4
                )
                for x0,y0,x1,y1,name in data
            ]).opts(
                tools=['hover'],
                legend_position='right',
                show_legend=True,
                aspect='equal'
            )

            robot_loc = hv.Scatter([(0,0)],label='Robot Centre').opts(color='blue',marker='star',size=10)
            
            return overlay * robot_loc
            
        else: return hv.Overlay([])

        
    def _CreateWallSelection(self):
        self.wall_select = pnw.Select(name="Select Wall to Paint",options = [1,2,3,4],align='center')

        pn.state.add_periodic_callback(self._CreateWallSelectionCallback,500)

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