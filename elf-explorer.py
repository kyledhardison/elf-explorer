import dash
from dash import dcc
import dash_bootstrap_components as dbc
from dash import html
import gtirb
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout
import plotly.graph_objs as go
import sys
from textwrap import dedent
import json
import argparse

p = argparse.ArgumentParser()
p.add_argument('infile')
args = p.parse_args()

ir = gtirb.IR.load_protobuf(args.infile)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "ELF Explorer"

symdb = {}
sectiondb = {}
with open('./symdb/symdb.json', 'r') as f:
    symdb = json.load(f)

with open('./symdb/sectiondb.json', 'r') as f:
    sectiondb = json.load(f)

G_orig = ir.cfg.nx()

relabel = {}
count = 0
for n in G_orig.nodes:
    name = "undef_"
    refs = list(n.references)
    if refs:
        if len(refs) != 1:
            print("TODO: Multiple references, address this")
        name = refs[0].name
    else:
        name = name + str(count)
        count += 1
    relabel[n] = name

revd = dict([reversed(i) for i in relabel.items()])

# Rename all nodes from their data to their symbol name, if possible
G = nx.relabel_nodes(G_orig, relabel, copy=True)
# TODO find a way to add arrows https://networkx.org/documentation/stable/reference/drawing.html

# TODO - prog can be set to different values: https://graphviz.org/docs/layouts/
# Also see this for options https://networkx.org/documentation/stable/reference/drawing.html
# Decent graph formats - dot, fdp, sfdp, patchwork, random (last 2 are more fun)
pos = graphviz_layout(G, prog='sfdp')
#pos = nx.random_layout(G)

# Attach position values and referent values to each node
for n, p in pos.items():
    G.nodes[n]['pos'] = p
    G.nodes[n]['referent'] = revd[n]

##################################################
# Create Edge Trace
##################################################
edge_trace = go.Scatter(
    x=[],
    y=[],
    line=dict(width=2, color='#888'),
    hoverinfo='none',
    mode='lines')
for edge in G.edges():
    x0, y0 = G.nodes[edge[0]]['pos']
    x1, y1 = G.nodes[edge[1]]['pos']
    edge_trace['x'] += tuple([x0, x1, None])
    edge_trace['y'] += tuple([y0, y1, None])

##################################################
# Create Node Trace
##################################################
node_trace = go.Scatter(
    x=[],
    y=[],
    text=[],
    mode='markers+text',
    hoverinfo='text',
    marker=dict(
        # TODO this is the legend scale, probably not necessary outside of a proper legend
        showscale=False,
        colorscale='pinkyl',  # TODO better color scale?
        reversescale=False,
        color=[],
        size=37,
        colorbar=dict(
            thickness=1,
            title='Node Connections',
            xanchor='left',
            titleside='right'
        ),
        line=dict(width=0)))

for node in G.nodes():
    x, y = G.nodes[node]['pos']
    node_trace['x'] += tuple([x])
    node_trace['y'] += tuple([y])


def getNodeColor(node):
    t = type(revd[node]).__name__
    if node == "main":
        return 2
    elif t == "CodeBlock":
        return 1
    elif t == "ProxyBlock":
        return 3
    else:
        print("TODO: Unexpected Block Type")
        return 100


for node in G.nodes():
    node_trace['marker']['color'] += tuple([getNodeColor(node)])
    # if not node.startswith("undef"):
    node_trace['text'] += tuple([node])
    # else:
    #    node_trace['text'] += tuple([""])

################################################################################
# Create html page
################################################################################
fig = go.Figure(data=[edge_trace, node_trace],
                layout=go.Layout(
                showlegend=False,
                hovermode='closest',
                margin=dict(b=21, l=5, r=5, t=40),  # plot margins
                annotations=[dict(
                    ax=(G.nodes[edge[0]]['pos'][0] + G.nodes[edge[1]]['pos'][0]) / 2,
                    ay=(G.nodes[edge[0]]['pos'][1] + G.nodes[edge[1]]['pos'][1]) / 2, axref='x', ayref='y',
                    x=(G.nodes[edge[1]]['pos'][0] * 3 + G.nodes[edge[0]]['pos'][0]) / 4,
                    y=(G.nodes[edge[1]]['pos'][1] * 3 + G.nodes[edge[0]]['pos'][1]) / 4, xref='x', yref='y',
                    showarrow=True,
                    arrowhead=2,
                    arrowsize=2,
                    arrowwidth=1,
                    opacity=1
                    ) for edge in G.edges],
                xaxis=dict(showgrid=False, zeroline=False,
                           showticklabels=False, mirror=True),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, mirror=True)))

################################################################################
# Create html page
################################################################################

app.layout = dbc.Container(fluid=True,
                           children=[
                               dbc.Row(
                                   html.Div([
                                       html.H1("ELF Explorer")],
                                       style={'textAlign': "center"})),
                               dbc.Row([
                                   dcc.Graph(
                                       id='example-graph',
                                       figure=fig,
                                       style={'height': '60vh'}
                                   )
                               ]),
                               dbc.Row([
                                   dbc.Col(
                                       html.Div(
                                           # "TEST1",
                                           children=[
                                               html.H2("Symbol Definition"),
                                               dcc.Markdown(id='click-data')
                                           ]
                                       ),
                                       width=6,
                                       style={'textAlign': 'center'}
                                   ),

                                   dbc.Col(
                                       html.Div(
                                           children=[
                                               html.H2("Symbol Section"),
                                               dcc.Markdown(id='symbol-data')
                                           ]
                                       ),
                                       width=6,
                                       style={'textAlign': 'center'}
                                   )
                               ])
                           ])


# Node Click callback
@app.callback(
    dash.dependencies.Output('click-data', 'children'),
    [dash.dependencies.Input('example-graph', 'clickData')])
def display_sym_def(clickData):
    node = ""
    if not clickData:
        return ""
    try:
        node = clickData["points"][0]["text"]
        details = symdb[node]
    except KeyError:
        if not node:
            return "Symbol Not Found"
        else:
            return f"{node} Not Found"
    return f"""**{node}**: \n
{details[0]}

`{details[1]}`

{details[2]}"""

@app.callback(
    dash.dependencies.Output('symbol-data', 'children'),
    [dash.dependencies.Input('example-graph', 'clickData')])
def display_sym_data(clickData):
    ref = None
    section = ""
    sectiondata = ""
    datatype = ""
    node = ""

    if not clickData:
        return ""
    try:
        node = clickData["points"][0]["text"]
        ref = revd[node]
        datatype = type(ref).__name__
        if datatype == "CodeBlock" or datatype == "DataBlock":
            section = ref.section.name
            sectiondata = sectiondb.get(section)
        else:
            sectiondata = "This is an external symbol. External symbols exist in another library, and their exact location is resolved at runtime by the linker."
    except KeyError:
        return "Symbol Info Not Found"
    if not section:
        section = "External Symbol"
    return f"**{section}** \n\n {sectiondata}"

if __name__ == '__main__':
    app.run_server()

