import plotly.graph_objects as go
import plotly.io as pio
import numpy as np
import pandas as pd

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
    
class TraceData:
    """
    Object Trace Data who contains the information of the trace. (Label, calculated time, points to plot,
    mode and color)
    """
    def __init__(self, label, x_data, y_data, z_data = None,  mode="lines", color="blue",sample_time=None,  dash=None, marker=None):
        self.label = label
        self.sample_time = sample_time
        self.x_data = x_data
        self.y_data = y_data
        self.mode = mode
        self.color = color
        self.dash = dash
        self.marker = marker
        self.z_data = z_data

        # Calculate time if it's needed
        if sample_time:
            self.time = [x * self.sample_time for x in x_data]
        
        # Build line dictionary
        if self.dash:
            self.line = {"color": self.color, "dash": self.dash}
        else:
            self.line = {"color": self.color}

        if len(x_data) != len(y_data):
            raise ValueError(f"x_data and y_data must have the same length for trace '{label}'")
  
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
            height=400,  # Set maximum height to 350 px 
            yaxis=dict(range=[0, max_y],fixedrange=False), #Force to strart in y=0
            xaxis=dict(range=[0, max_x],fixedrange=False), #Force to strart in x=0
        )

        # Convert graph to HTML 
        return pio.to_html(fig, full_html=False)

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
            #title=self.title,
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
            height=850
        )

        # Convert graph to HTML 
        return pio.to_html(fig, full_html=False)


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
            zaxis=dict(range=[900, 0])  # Range from 0 to 900 and inverted in Z
        ),
        width=1150, 
        height=700,
        margin=dict(r=10, l=10, b=10, t=10), #Small margin
        showlegend=True
        )

        return pio.to_html(fig, full_html=False)
    
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
        n = len(trace_list[0].y_data)
        x, y, z = [], [], []

        for trace in trace_list:
            x.append(np.array(trace.x_data))
            y.append(np.array(trace.y_data))
            z.append(np.array(trace.z_data))

        x = np.concatenate(x)
        y = np.concatenate(y)
        z = np.concatenate(z)

        total_lines = len(trace_list)
        i, j, k = [], [], []

        for p in range(n - 1):
            for line in range(total_lines - 1):
                offset = line * n
                i.append(p + offset)
                j.append(p + offset + n)
                k.append(p + offset + 1)

                i.append(p + offset + 1)
                j.append(p + offset + n)
                k.append(p + offset + n + 1)

        return go.Mesh3d(
            x=x, y=y, z=z,
            i=i, j=j, k=k,
            opacity=0.5,
            color='tan',
            flatshading=True,
            name='Mesh'
        )