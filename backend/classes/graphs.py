import plotly.graph_objects as go
import plotly.io as pio
import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from typing import List, Optional, Union, Sequence


class Graph:
    """
    Given title, X axis title, Y axis title and a list of dicts which contain the traces information,
    the class returns a graphic dictionary containing the results of the requested filter in the subclass.
    """
    def __init__(self,title="Title", xaxis_title="X Axis", yaxis_title="Y Axis",leyend_pos=["top", "right"] ):
        self.fig = go.Figure()
        self.title = title
        self.xaxis_title = xaxis_title
        self.yaxis_title = yaxis_title
        self.leyend_pos = leyend_pos
    
    def plot_graph(self):
        raise NotImplementedError(f"Subclasses should implement this method. Call one of: {[cls.__name__ for cls in Graph.__subclasses__()]}")
    
@dataclass
class TraceData:
    label: str 
    x_data: Sequence[Union[int, float]] #Sequences accept Pandas series, list or duples
    y_data: Sequence[Union[int, float]]
    z_data: Optional[Sequence[Union[int, float]]] = None
    mode: str = "lines"
    color: str = "blue"
    sample_time: Optional[float] = None
    dash: Optional[str] = None
    marker: Optional[dict] = None
    
    time: Optional[List[float]] = field(init=False, default=None)
    line: dict = field(init=False)

    def __post_init__(self):
        # Validate first (better fail early)
        if len(self.x_data) != len(self.y_data):
            raise ValueError(f"x_data and y_data must have the same length for trace '{self.label}'")
        
        # Calculate time
        self.time = (
            [x * self.sample_time for x in self.x_data]
            if self.sample_time is not None
            else list(self.x_data)
        )


        # Build line dict
        self.line = {"color": self.color}
        if self.dash:
            self.line["dash"] = self.dash
  
class PlotPointsinTime(Graph):
    def __init__(self, title, xaxis_title, yaxis_title, leyend_pos, traces:list[TraceData] ):
        super().__init__(title, xaxis_title, yaxis_title, leyend_pos)
        self.traces = traces

    def plot_graph(self):
        # Generate de graph
        fig =self.fig

        #Validate the data
        for trace in self.traces:

            fig.add_trace(go.Scatter(
            x=trace.time,
            y=trace.y_data,
            mode=trace.mode, #"lines",
            name=trace.label,
            line=trace.line,
            ))


        max_y = float(max(max(trace.y_data) for trace in self.traces))
        max_x = float(max(trace.time))

        # Style
        fig.update_layout(
            title=self.title,
            xaxis_title=self.xaxis_title,
            yaxis_title=self.yaxis_title,
            template="plotly_white",
            margin=dict(l=20, r=20, t=40, b=20),
            legend=dict(
                yanchor=self.leyend_pos[0],
                y=0.05 if self.leyend_pos[0] == "bottom" else 0.95,
                xanchor=self.leyend_pos[1],
                x=0.95 if self.leyend_pos[1] == "right" else 0.05,
                bgcolor='rgba(255,255,255,0.5)',
                bordercolor="black",
                borderwidth=1
            ),
            autosize=True, 
            yaxis=dict(range=[0, max_y],fixedrange=False), #Force to strart in y=0
            xaxis=dict(range=[0, max_x],fixedrange=False), #Force to strart in x=0
        )

        # Convert graph to HTML 
        return pio.to_html(fig, full_html=False,  config={"responsive": True})

class LogScatterPlot(Graph):
    def __init__(self, title, xaxis_title, yaxis_title, leyend_pos,traces:list[TraceData]):
        super().__init__(title, xaxis_title, yaxis_title, leyend_pos)
        self.traces = traces

    def plot_graph(self):
        # Generate de graph
        fig =self.fig

        #Validate the data
        for trace in self.traces:
            scatter_kwargs = {
                "x": trace.x_data,
                "y": trace.y_data,
                "mode": trace.mode,
                "name": trace.label,
                "line": trace.line
            }

            if trace.marker:
                scatter_kwargs["marker"] = trace.marker

            fig.add_trace(go.Scatter(**scatter_kwargs))


        #Layout
        exp_min = np.floor(np.log10(self.traces[0].x_data.min()))
        exp_max = np.ceil(np.log10(self.traces[0].x_data.max()))

        tickvals = [10 ** e for e in range(int(exp_min), int(exp_max + 1))]
        ticktext = [f"10<sup>{e}</sup>" for e in range(int(exp_min), int(exp_max + 1))]

        fig.update_layout(
            xaxis=dict(
                title=self.xaxis_title,
                type='log',
                tickvals=tickvals,
                ticktext=ticktext, 
                range=[exp_min, exp_max]
            ),
            yaxis=dict(title=self.yaxis_title),
            margin=dict(l=10, r=10, t=30, b=10),
            legend=dict(
                yanchor=self.leyend_pos[0],
                y=0.05 if self.leyend_pos[0] == "bottom" else 0.95,
                xanchor=self.leyend_pos[1],
                x=0.95 if self.leyend_pos[1] == "right" else 0.05,
                bgcolor='rgba(255,255,255,0.8)',
                bordercolor='black',
                borderwidth=1
            ),
            hovermode='closest',
            autosize=True
        )

        # Convert graph to HTML 
        return pio.to_html(fig, full_html=False,  config={"responsive": True})


class Traces3DPlot(Graph):
    def __init__(self, traces: list[TraceData]):
        if not traces:
            raise ValueError("The trace list is empty.")

        lengths = [len(t.x_data) for t in traces]
        if len(set(lengths)) != 1:
            raise ValueError(f"All traces must have the same length. Lengths found: {lengths}")
        
        self.traces = traces

    def plot_graph(self):
        #Generate figure
        fig = go.Figure()

        # We add the mesh (Mesh3d) first and then the traces (Scatter3d) so that the traces are visually on top.
        # Plotly renders objects in the order they are added, this way we prevent the mesh from covering important data.

        fig.add_trace(self.build_mesh3d_traces(self.traces))

        #Add all the traces to the figure (PlotTraces transform normal traces in 3D traces)
        for trace in self.plot_traces(self.traces):
            fig.add_trace(trace)

        fig.update_layout(
        scene=dict(
            xaxis_title='Box width (367)',
            yaxis_title='Box length (570)',
            zaxis_title='Distance to sensor (mm)',
            xaxis=dict(nticks=5), # Display 5 ticks in X axis
            yaxis=dict(nticks=10), # Display 10 ticks in Y axis
            zaxis=dict(range=[650, 0]),  # Range from 0 to 900 and inverted in Z
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1),
            )
        ),
        autosize=True,
        margin=dict(r=10, l=10, b=10, t=10), #Small margin
        showlegend=True
        )

        return pio.to_html(fig, full_html=False, config={"responsive": True})

    
    def plot_traces(self, trace_list):
        traces3D=[]
        for trace in trace_list:
            traces3D.append(go.Scatter3d(
                x=trace.x_data,
                y=trace.y_data,
                z=trace.z_data,
                mode=trace.mode,
                line=trace.line,
                marker=trace.marker,
                name=trace.label
            ))
        return traces3D
    
    def build_mesh3d_traces(self, trace_list):
        # Number of points in each trace (assumed to be equal)
        n = len(trace_list[0].y_data)

        # Prepare empty lists for x, y, and z coordinates
        x, y, z = [], [], []

        # Extract coordinate data from each trace
        for trace in trace_list:
            x.append(np.array(trace.x_data))
            y.append(np.array(trace.y_data))
            z.append(np.array(trace.z_data))

        # Concatenate all coordinate arrays into single arrays
        x = np.concatenate(x)
        y = np.concatenate(y)
        z = np.concatenate(z)

        total_lines = len(trace_list)  # Total number of vertical traces
        i, j, k = [], [], []  # Lists to hold triangle vertex indices

        # Create two triangles (i, j, k) for each quad in the mesh
        for p in range(n - 1):  # Iterate through points in the vertical direction
            for line in range(total_lines - 1):  # Iterate through horizontal connections
                offset = line * n  # Offset to locate the correct index in the flattened array

                # First triangle of the quad
                i.append(p + offset)
                j.append(p + offset + n)
                k.append(p + offset + 1)

                # Second triangle of the quad
                i.append(p + offset + 1)
                j.append(p + offset + n)
                k.append(p + offset + n + 1)

        # Return a Plotly Mesh3d object with the computed geometry
        return go.Mesh3d(
            x=x, y=y, z=z,
            i=i, j=j, k=k,  # Triangle definitions
            opacity=0.5,
            color='tan',
            flatshading=True,
            name='Mesh',
            hoverinfo='skip',  # Disable hover for mesh
            showscale=False    # Optional: don't show color scale
        )
