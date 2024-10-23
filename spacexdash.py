# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # TASK 1: Add a dropdown list to enable Launch Site selection
    dcc.Dropdown(id='site-dropdown',
                 options=[{'label': 'All Sites', 'value': 'ALL'}] +
                         [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()],
                 value='ALL',  # Default value to show all sites
                 placeholder="Select a Launch Site here",
                 searchable=True
                 ),
    
    html.Br(),
    
    # TASK 2: Add a pie chart to show the total successful launches count for all sites
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),

    # TASK 3: Add a slider to select payload range
    dcc.RangeSlider(id='payload-slider',
                    min=0, 
                    max=10000, 
                    step=1000,
                    marks={i: f'{i} Kg' for i in range(0, 10001, 2500)},  # Mark every 2500 Kg for better readability
                    value=[min_payload, max_payload]),

    # TASK 4: Add a scatter chart to show the correlation between payload and launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TASK 2: Callback function for the pie chart
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    # Filter the dataframe based on the selected site
    if entered_site == 'ALL':
        # Create pie chart for all sites
        fig = px.pie(spacex_df, 
                     names='Launch Site', 
                     values='class', 
                     title='Total Successful Launches by Site')
    else:
        # Filter data for the selected launch site
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        # Create pie chart for the specific site showing success and failure
        fig = px.pie(filtered_df, 
                     names='class', 
                     title=f'Total Success and Failures for site {entered_site}',
                     labels={'class': 'Outcome'},
                     color_discrete_sequence=['#28a745', '#dc3545'])
    return fig

# TASK 4: Callback function for the scatter plot
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter_chart(selected_site, selected_payload):
    # Filter data based on the payload range
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= selected_payload[0]) & 
                            (spacex_df['Payload Mass (kg)'] <= selected_payload[1])]
    
    # If ALL sites are selected, show data for all sites
    if selected_site == 'ALL':
        # Create scatter plot for all sites
        fig = px.scatter(
            filtered_df, x='Payload Mass (kg)', y='class',
            color='Booster Version Category',
            title='Correlation between Payload and Success for all Sites',
            labels={'class': 'Launch Outcome'}
        )
    else:
        # Filter data for the selected site
        site_df = filtered_df[filtered_df['Launch Site'] == selected_site]
        # Create scatter plot for the specific site
        fig = px.scatter(
            site_df, x='Payload Mass (kg)', y='class',
            color='Booster Version Category',
            title=f'Correlation between Payload and Success for {selected_site}',
            labels={'class': 'Launch Outcome'}
        )
    
    # Return the figure
    return fig


# Run the app
if __name__ == '__main__':
    app.run_server()
