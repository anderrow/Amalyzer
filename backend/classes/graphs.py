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
    
        
  
class PlotPointsinTime(Graph):
    def __init__(self, prop_id, title, xaxis_title, yaxis_title, sample_time, x_axis, y_axis, color = "blue" ):
        super().__init__(prop_id, title, xaxis_title, yaxis_title)
        self.sample_time = sample_time
        self.x_axis = x_axis
        self.y_axis = y_axis
        self.color = color

    def plot_graph(self):
        # Generate de graph
        fig = go.Figure()

        # Calculate time bassed on the sample time
        time = [value * self.sample_time for value in self.x_axis] 

        fig.add_trace(go.Scatter(
            y=self.y_axis, x=time, mode='lines', name=self.title,
            line=dict(color=self.color)
        ))

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
        )

        # Convert graph to HTML 
        return pio.to_html(fig, full_html=False)



