
import gtirb
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout
import matplotlib.pyplot as plt

ir = gtirb.IR.load_protobuf('test.gtirb')
G = ir.cfg.nx()
#nx.draw(g)

plt.title('draw_networkx')
# TODO - figure out prog https://graphviz.org/docs/layouts/
pos=graphviz_layout(G, prog='dot')
for n, p in pos.items():
    G.nodes[n]['pos'] = p

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

#nx.draw(G, pos, with_labels=True, arrows=True)
#nx.draw(G, pos, arrows=True)

#plt.show()
