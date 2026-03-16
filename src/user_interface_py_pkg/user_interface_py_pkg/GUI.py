
#%%
import panel as pn 
from panel import pane as pnp
from panel import layout as pnl
from panel import widgets as pnw
from panel.layout.gridstack import GridStack
pn.extension()



class GUI():
    
    def __init__(self):

        self.img_opts = ["World","Camera 1","Camera 2", "Floor Plan", "Motion Plan"]
        pass
        

    def LinkToNodes(self):
        pass


    def RunApp(self):
        main_nodes = self._CreateHomeScreen()

        app = pn.template.ReactTemplate(
            title = "V.I.S.N.A.T: Monitoring GUI",
            main = main_nodes
        ).servable()

        return app
    
    def _CreateHomeScreen(self):

        base = GridStack(sizing_mode="stretch_both",min_height=600)



        critical_info = pnl.WidgetBox(pnl.Column(pnp.Str("Battery level"), pnp.Str("Paint level"), pnp.Str("Action Progress")))

        world_info = pnl.WidgetBox(pnl.Column(pnp.Str("Robot Pos (Rel 0,0): "),pnp.Str("Room"),pnp.Str("Other stuff")))

        focus_tabs = pnl.WidgetBox(pnl.Column(pnp.Str("Quick swap to somewher else")))

        main_image = pnl.WidgetBox(
            pnl.Column(
                pnw.RadioButtonGroup(name="helo",options = self.img_opts, button_type="success",sizing_mode="stretch_width")

                )
        )

        current_action_info = pnl.WidgetBox()

        system_status = pnl.WidgetBox()

        notifications = pnl.WidgetBox()

        sub_image_a = pnl.WidgetBox(
            pnl.Column(
                pnw.RadioButtonGroup(name="helo",options = self.img_opts, button_type="success",sizing_mode="stretch_width")

                )
        )

        sub_image_b = pnl.WidgetBox(
            pnl.Column(
                pnw.RadioButtonGroup(name="helo",options = self.img_opts, button_type="success",sizing_mode="stretch_width")

                )
        )


        base[0,0] = critical_info
        base[1,0] = world_info
        base[2:6,0:] = focus_tabs
        base[0,1:5] = main_image 
        return base


        

if __name__ == "__main__":
    gui = GUI()
    gui.LinkToNodes()
    app = gui.RunApp()
    pn.serve(app)
# %%
