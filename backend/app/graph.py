import networkx as nx

def build_graph(rows):
    graph=nx.Graph()
    for row in rows:
        t=row['transaction_id']; graph.add_node(t,type='transaction')
        for key,kind in [('customer_id','customer'),('device_id','device'),('ip_address','ip'),('payment_method','payment_instrument'),('merchant_id','merchant')]:
            if row.get(key): graph.add_node(row[key],type=kind); graph.add_edge(t,row[key])
    return graph

def component_score(graph, component):
    customers=sum(graph.nodes[n].get('type')=='customer' for n in component)
    return min(100, customers*6 + max(0, len(component)-customers)*2)
