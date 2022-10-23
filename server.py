import dash
from dash import dcc
from dash import html
import gtirb
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout
import plotly.graph_objs as go

ir = gtirb.IR.load_protobuf('test.gtirb')
G = ir.cfg.nx()
#nx.draw(g)

# TODO - figure out prog https://graphviz.org/docs/layouts/
pos=graphviz_layout(G, prog='dot')
nx.draw(G, pos, with_labels=True, arrows=True)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "ELF Explorer"

ir = gtirb.IR.load_protobuf('test.gtirb')
G = ir.cfg.nx()
#nx.draw(g)

pos=graphviz_layout(G, prog='dot')

for n, p in pos.items():
    G.nodes[n]['pos'] = p

##################################################
# Create Edge Trace
##################################################
edge_trace = go.Scatter(
    x=[],
    y=[],
    line=dict(width=0.5, color='#888'),
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
        showscale=True,
        colorscale='pinkyl',
        reversescale=True,
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
for node, adjacencies in enumerate(G.adjacency()):
    node_trace['marker']['color'] += tuple([len(adjacencies[1])])
    node_info = adjacencies[0]
    node_trace['text'] += tuple([node_info])


title = "Network Graph Demonstration"
fig = go.Figure(data=[edge_trace, node_trace],
                layout=go.Layout(
                title=title,
                titlefont=dict(size=16),
                showlegend=False,
                hovermode='closest',
                margin=dict(b=21, l=5, r=5, t=40),
                annotations=[dict(
                    text="Text Here",
                    showarrow=False,
                    xref="paper", yref="paper")],
                xaxis=dict(showgrid=False, zeroline=False,
                           showticklabels=False, mirror=True),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, mirror=True)))


app.layout = html.Div([
    #########################Title
    html.Div([html.H1("ELF Explorer")],
             className="row",
             style={'textAlign': "center"}),
   dcc.Graph(
      id='example-graph',
      figure=fig
   )

    ])


if __name__ == '__main__':
    app.run_server(debug=True)

