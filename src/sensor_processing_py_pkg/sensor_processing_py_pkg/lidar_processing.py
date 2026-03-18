
#%%
import open3d as o3d
import numpy as np
import plotly.graph_objects as go


#%%
dataset = o3d.data.PLYPointCloud()
pcd = o3d.io.read_point_cloud(dataset.path)


#%%
points = np.asarray(pcd.points)
points[:,1] *= -1
fig = go.Figure(data=[go.Scatter3d(
    x=points[:,0],
    y=points[:,2],
    z=points[:,1],
    mode='markers',
    marker=dict(size=2, color=points[:,2], colorscale='Viridis')
)])
fig.show()
# %%
