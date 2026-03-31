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
        graphics = {}
        graphics["Lidar"] = self._CreateLidarGraph()
        graphics["SystemHealth"] = self._CreateSystemHealth()

        return graphics


    def _CreateLidarGraph(self):
        lidar_pipe = Pipe(data = [])
        task = asyncio.create_task(self.node_handler.GetData('Lidar',lidar_pipe))
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
        data = self.node_handler.subscriber_data['SysHP']

        if len(self.system_health) < 2:
            print("???")
            for key in data.keys():
                self.system_health.append(
                    pnp.Markdown(f"{key} : {data[key]}",self.styles['markdown_text_reg'])
                )
        else:
            print("!!!")
            i = 2
            for key in data.keys():
                self.system_health[i](
                    pnp.Markdown(f"{key} : {data[key]}",self.styles['markdown_text_reg'])
                )
                i+=1
                
        self.system_health.sizing_mode = 'stretch_both'
        self.system_health.scroll = True

        