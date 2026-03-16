
#%%
import panel as pn 
pn.extension()



class GUI():
    
    def __init__(self):
        nodes = {}
        

    def LinkToNodes(self):
        pass


    def RunApp(self):
        main_nodes = pn.pane.Str("Saluations!")

        app = pn.template.ReactTemplate(
            title = "V.I.S.N.A.T: Monitoring GUI",
            main = main_nodes
        ).servable()

        return app
    
    def CreateHomeScreen(self):
        pass


#%%
if __name__ == "__main__":
    gui = GUI()
    gui.LinkToNodes()
    app = gui.RunApp()
    pn.serve(app)
# %%
