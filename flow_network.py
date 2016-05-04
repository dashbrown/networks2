class Edge(object):
    def __init__(self, u, v, w):
        self.source = u
        self.sink = v  
        self.capacity = w
    def __repr__(self):
        return "%s->%s:%s" % (self.source, self.sink, self.capacity)

class FlowNetwork(object):
    def __init__(self):
        self.adj = {}
        self.flow = {}
 
    def add_vertex(self, vertex):
        self.adj[vertex] = []
 
    def get_edges(self, v):
        return self.adj[v]
 
    def add_edge(self, u, v, w=0):
        if u == v:
            raise ValueError(str(u) + " == " + str(v))
        edge = Edge(u,v,w)
        redge = Edge(v,u,0)
        edge.redge = redge
        redge.redge = edge
        self.adj[u].append(edge)
        self.adj[v].append(redge)
        self.flow[edge] = 0
        self.flow[redge] = 0
        return edge
 
    def find_path(self, source, sink, path):
        if source == sink:
            return path
        for edge in self.get_edges(source):
            residual = edge.capacity - self.flow[edge]
            if residual > 0 and edge not in path:
                result = self.find_path( edge.sink, sink, path + [edge]) 
                if result != None:
                    return result
 
    def max_flow(self, source, sink):
        path = self.find_path(source, sink, [])
        while path != None:
            residuals = [edge.capacity - self.flow[edge] for edge in path]
            flow = min(residuals)
            for edge in path:
                self.flow[edge] += flow
                self.flow[edge.redge] -= flow
            path = self.find_path(source, sink, [])
        # for edge in self.flow:
        #     if self.flow[edge] == 1:
        #         print edge, self.flow[edge]
        return sum(self.flow[edge] for edge in self.get_edges(source))


if __name__ == '__main__':
    g = FlowNetwork()
    [g.add_vertex(v) for v in "x12345tjmasy"]
    g.add_edge('x','1',1)
    g.add_edge('x','2',1)
    g.add_edge('x','3',1)
    g.add_edge('x','4',1)
    g.add_edge('x','5',1)
    g.add_edge('1','t',1)
    g.add_edge('1','m',1)
    g.add_edge('2','t',1)
    g.add_edge('2','j',1)
    g.add_edge('3','j',1)
    g.add_edge('3','m',1)
    g.add_edge('4','a',1)
    g.add_edge('4','s',1)
    g.add_edge('5','s',1)
    g.add_edge('5','a',1)
    g.add_edge('t','y',1)
    g.add_edge('j','y',1)
    g.add_edge('m','y',1)
    g.add_edge('a','y',1)
    g.add_edge('s','y',1)
    print g.max_flow('x','y')
    for edge in g.flow:
        if g.flow[edge] == 1 and edge.source.isdigit():
            print edge



















