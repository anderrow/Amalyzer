import plotly.graph_objects as go
import plotly.io as pio
import numpy as np
import pandas as pd

class Graph:
    """
    Give title, X axis title, Y axis title and a list of dicts which contain the traces information,
    the class returns a graphic dictionary containing the results of the requested filter in the subclass.
    """
    def __init__(self, prop_id, title="Title", xaxis_title="X Axis", yaxis_title="Y Axis",leyend_pos=["top", "right"] ):
        self.fig = go.Figure()
        self.title = title
        self.xaxis_title = xaxis_title
        self.yaxis_title = yaxis_title
        self.prop_id=prop_id
        self.leyend_pos = leyend_pos
    
    def plot_graph(self):
        raise NotImplementedError("Subclasses should implement this method.")
    
class TraceData:
    """
    Object Trace Data who contains the information of the trace. (Label, calculated time, points to plot,
    mode and color)
    """
    def __init__(self, label, x_data, y_data, mode="lines", color="blue",sample_time=None,  dash=None, marker=None):
        self.label = label
        self.sample_time = sample_time
        self.x_data = x_data
        self.y_data = y_data
        self.mode = mode
        self.color = color
        self.dash = dash
        self.marker = marker
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
    def __init__(self, prop_id, title, xaxis_title, yaxis_title, leyend_pos, traces:list[TraceData] ):
        super().__init__(prop_id, title, xaxis_title, yaxis_title, leyend_pos)
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
            height=350,  # Set maximum height to 350 px 
            yaxis=dict(range=[0, max_y],fixedrange=False), #Force to strart in y=0
            xaxis=dict(range=[0, max_x],fixedrange=False), #Force to strart in x=0
        )

        # Convert graph to HTML 
        return pio.to_html(fig, full_html=False)

#Needs to be done 
class LogScatterPlot(Graph):
    def __init__(self, prop_id, title, xaxis_title, yaxis_title, leyend_pos,traces:list[TraceData]):
        super().__init__(prop_id, title, xaxis_title, yaxis_title, leyend_pos)
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
        exp_min = int(np.floor(np.log10(self.traces[0].x_data.min())))
        exp_max = int(np.ceil(np.log10(self.traces[0].x_data.max())))
        tickvals = [10 ** e for e in range(exp_min, exp_max + 1)]
        ticktext = [f"10<sup>{e}</sup>" for e in range(exp_min, exp_max + 1)]

        fig.update_layout(
            #title=self.title,
            xaxis=dict(
                title=self.xaxis_title,
                type='log',
                tickvals=tickvals,
                ticktext=ticktext
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
            height=700
        )

        # Convert graph to HTML 
        return pio.to_html(fig, full_html=False)

#def add_traces