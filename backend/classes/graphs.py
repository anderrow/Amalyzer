import plotly.graph_objects as go
import plotly.io as pio


class Graph:
    """
    Give title, X axis title, Y axis title and a list of dicts which contain the traces information,
    the class returns a graphic dictionary containing the results of the requested filter in the subclass.
    """
    def __init__(self, prop_id, title="Title", xaxis_title="X Axis", yaxis_title="Y Axis", ):
        self.fig = go.Figure()
        self.title = title
        self.xaxis_title = xaxis_title
        self.yaxis_title = yaxis_title
        self.prop_id=prop_id
    
    def plot_graph(self):
        raise NotImplementedError("Subclasses should implement this method.")
    
class TraceData:
    """
    Object Trace Data who contains the information of the trace. (Label, calculated time, points to plot,
    mode and color)
    """
    def __init__(self, label, sample_time,  x_data, y_data, mode="lines", color="blue"):
        self.label = label
        self.sample_time = sample_time
        self.x_data = x_data
        self.time = [x * self.sample_time for x in x_data]
        self.y_data = y_data
        self.mode = mode
        self.color = color

        if len(x_data) != len(y_data):
            raise ValueError(f"x_data and y_data must have the same length for trace '{label}'")
  
class PlotPointsinTime(Graph):
    def __init__(self, prop_id, title, xaxis_title, yaxis_title, traces:list[TraceData] ):
        super().__init__(prop_id, title, xaxis_title, yaxis_title)
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
            line=dict(color=trace.color)
            ))

        max_y = int(max(max(trace.y_data) for trace in self.traces))+1
        max_x = int(max(trace.time))

        # Style
        fig.update_layout(
            title=self.title,
            xaxis_title=self.xaxis_title,
            yaxis_title=self.yaxis_title,
            template="plotly_white",
            margin=dict(l=20, r=20, t=40, b=20),
            legend=dict(
                yanchor="top",
                y=0.95,
                xanchor="right",
                x=0.95,
                bgcolor='rgba(255,255,255,0.5)',
                bordercolor="black",
                borderwidth=1
            ),
            height=350,  # Set maximum height to 500 px 
            yaxis=dict(range=[0, max_y],fixedrange=False), #Force to strart in y=0
            xaxis=dict(range=[0, max_x],fixedrange=False), #Force to strart in x=0
        )

        # Convert graph to HTML 
        return pio.to_html(fig, full_html=False)

