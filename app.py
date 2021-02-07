import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
import numpy as np

# Helper functions for layout

def get_tree_species(output=None):
    soql_url = ('https://data.cityofnewyork.us/resource/nwxe-4ae8.json?' +
                '$select=distinct(spc_common)').replace(' ', '%20')
    trees = pd.read_json(soql_url).dropna()
    trees = list(trees.spc_common_1)
    if output=='dict':
        return [{'label': spc, 'value': spc} for spc in sorted(trees)]
    else:
        return trees

# Layout

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

app.layout = html.Div(children=[
    html.H1(children='NYC Tree Health Dashboard'),
    html.Div(className='row',  # Define the row element
        children=[
            html.Div(className='two columns div-user-controls',
                children=[
                    html.Label('Select borough:'),
                    dcc.Dropdown(
                        options=[
                            {'label':'Manhattan', 'value':'Manhattan'},
                            {'label':'Brooklyn', 'value':'Brooklyn'},
                            {'label':'Queens', 'value':'Queens'},
                            {'label':'Bronx', 'value':'Bronx'},
                            {'label':'Staten Island', 'value':'Staten Island'}
                        ],
                        value='Bronx',
                        id='dropdown-boro'
                    ),
                    html.Label('Select species:'),
                    dcc.Dropdown(
                        options=get_tree_species(output='dict'),
                        value='American beech',
                        id='dropdown-species'
                    )
                ]
            ),  # End of left element

            html.Div(className='ten columns div-user-controls',
                children=[
                    # Main graph
                    # dcc.Graph(
                    #     id='species-boro-graph'
                    # ),
                    # Subgraphs
                    html.Div(className='row',  # Define the row element
                        children=[
                            html.Div(className='six columns div-for-lower-left-chart',
                                children=[
                                    # dcc.Graph(
                                    #     id='tree-prop-graph'
                                    # ),
                                    dcc.Graph(
                                        id='tree-prop-map'
                                    )
                                ]
                            ), # End of left chart element
                            html.Div(className='six columns div-for-lower-right-chart',
                                children=[
                                    # dcc.Graph(
                                    #     id='tree-steward-graph'
                                    # ),
                                    dcc.Graph(
                                        id='tree-steward-detail-graph'
                                    )
                                ]
                            ) # End of right chart element
                        ]
                    )
                ]
            ) # End of right element
      ])

])

# Helper functions

def get_tree_info():
    tree_info = pd.DataFrame()
    for boro in ['Bronx', 'Brooklyn', 'Manhattan', 'Queens', 'Staten Island']:
        soql_url = ('https://data.cityofnewyork.us/resource/nwxe-4ae8.json?' + \
                    '$select=spc_common,count(tree_id),health,steward' + \
                    '&$where=boroname=\'{}\'' + \
                    '&$group=spc_common,health,steward').format(boro).replace(' ', '%20')
        soql_trees = pd.read_json(soql_url)
        soql_trees['borough'] = boro
        soql_trees = soql_trees.dropna()
        tree_info = tree_info.append(soql_trees)
    return tree_info

# Callbacks

@app.callback(
    Output('tree-prop-map', 'figure'),
    [Input('dropdown-boro', 'value'),
     Input('dropdown-species', 'value')])
def tree_prop_map(borough, species):
    treeinfo = get_tree_info()
    trees = treeinfo[(treeinfo.spc_common==species)&(treeinfo.borough==borough)]
    t = trees.groupby(['health']).agg({'count_tree_id':'sum'})
    t_prop = t.apply(lambda x: 100 * x / float(x.sum()))
    t_prop = t_prop.reset_index()
    t_prop.health = pd.Categorical(t_prop.health, categories=["Poor", "Fair", "Good"],ordered=True)
    t_prop = t_prop.sort_values('health', axis=0)
    fig = px.treemap(t_prop, path=['health'], values='count_tree_id',
                     color_discrete_sequence = ['rgb(35,139,69)','rgb(116,196,118)','rgb(199,233,192)'])
    fig.update_layout(title_text='Tree Health Proportion', title_x=0.5)
    fig.update_traces(textinfo = "label+percent parent", hovertemplate=None, hoverinfo='skip')
    return fig

@app.callback(
    Output('tree-steward-detail-graph', 'figure'),
    [Input('dropdown-boro', 'value'),
     Input('dropdown-species', 'value')])
def steward_impact_detail(borough, species):
    treeinfo = get_tree_info()
    trees = treeinfo[(treeinfo.spc_common==species)&(treeinfo.borough==borough)]
    t_pivot = pd.pivot_table(trees, index='steward',values='count_tree_id', columns='health', aggfunc=np.sum)
    t_pivot = t_pivot.fillna(0)
    t_pivot = t_pivot.reset_index()
    cols = list(t_pivot.columns[1:])
    t_prop_wide = pd.concat([t_pivot['steward'],t_pivot.iloc[:, 1:].apply(lambda x: 100 * x / float(x.sum()),axis=1)],
                          axis=1)
    t_prop_long = pd.melt(t_prop_wide, var_name='health', value_name='proportion', value_vars=cols,id_vars='steward')
    t_prop_long.steward = pd.Categorical(t_prop_long.steward, categories=["None", "1or2", "3or4","4orMore"],ordered=True)
    t_prop_long.health = pd.Categorical(t_prop_long.health, categories=["Poor", "Fair", "Good"],ordered=True)
    t_prop_long = t_prop_long.sort_values(['steward','health'], axis=0)

    fig = px.bar(t_prop_long, x="steward", y='proportion',
                 color='health', barmode="group", text='proportion',
                 hover_data={'proportion':':.1f'},
                 color_discrete_map={'Poor': 'rgb(199,233,192)','Fair': 'rgb(116,196,118)', 'Good': 'rgb(35,139,69)'})
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='auto')
    fig.update_layout(plot_bgcolor='rgb(255,255,255)',
                        title_text='Steward Impact',
                        title_x=0.5,
                        bargap=0.15,  # gap between bars of adjacent location coordinates.
                        bargroupgap=0.1,  # gap between bars of the same location coordinate.
                        uniformtext_minsize = 10, uniformtext_mode = 'hide'
                      )
    fig.update_yaxes(visible=False, showticklabels=False)
    fig.update_xaxes(visible=True, showticklabels=True)

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
