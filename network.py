#!/usr/bin/env python
# Mark Janssen, <average@mit.edu> July 7, 2002

"""Network class for flow networks."""

__version__ = "$Revision: 2.2 $"
__author__  = "$Author: average $"
__date__    = "$Date: 2002/08/05 04:09:27 $"

import random
from graph import *

DEFAULT_CAPACITY = 1

class Node(WVertex):
    """Node in a flow network."""
    
    __slots__ = ['_energy', 'energy_out']
    
    def __init__(self, network, id, init={}, capacity=DEFAULT_CAPACITY, collision=ADD):
        super(Node, self).__init__(network, id, init, capacity, collision)
        self.energy_out = 0
        self._energy = [0, 0]
    
    def add(self, sink, capacity=DEFAULT_CAPACITY, collision=ADD):
        """Add connection to sink with given capacity (defaults to 1).
        >>> n = Network()
        >>> n[1].add([2, 3], 5)
        >>> print n[1]
        0 {2: 5, 3: 5}

        If sink already connected, capacity is accumulates.
        >>> n[1].add(2, 2)
        >>> n[1].add(2)     #will use default cap=1
        >>> print n[1]
        0 {2: 8, 3: 5}
        """
        super(Node, self).add(sink, capacity, collision)
    
    def update(self, sinks, capacity=DEFAULT_CAPACITY, collision=ADD):
        super(Node, self).update(sinks, capacity, collision)
    
    def tick(self):
        """Advance node 1 time increment. Returns amount of energy transferred."""
        if not self.energy: #nothing to do
            self.energy_out = 0
            return 0
        paths, self.energy_out, g = [], 0, self._graph
        if self.energy > 0:
            for tail, capacity in self.iteritems():
                paths.extend([tail]*capacity)
            bit = 1
            assert len(paths) == self.sum_out()
        else:
            for head in self.in_vertices():
                paths.extend([head]*g[head][self._id])
            bit = -1
            assert len(paths) == self.sum_in()
        while paths and self.energy:
            path = random.choice(paths)
            paths.remove(path)
            g[path]._newenergy += bit   #move one bit of energy
            self.energy -= bit
            self.energy_out += bit
        #give back left-over energy, if any
        self._newenergy += self.energy
        self.energy = 0
        return self.energy_out
            
    def read(self):
        return self._energy[self._graph._current_state]
    
    def write(self, energy):
        self._energy[self._graph._current_state] = energy
        
    def readnew(self):
        return self._energy[not self._graph._current_state]
        
    def writenew(self, energy):
        self._energy[not self._graph._current_state] = energy
    
    energy = property(read, write, None, "Energy at node.")
    _newenergy = property(readnew, writenew, None, "Energy for next generation.")
        
    def __str__(self):
        """Returns string with energy level and arc info.
        >>> n = Network()
        >>> n.add(1, 2)
        >>> n[1].energy += 5
        >>> print n[1]
        5 {2: 1}
        """
        return str(self.energy) + " " + super(Node, self).__str__("%r: %s")
        
    def validate(self):
        #assert self.energy >= 0, "Invalid energy value %r at node %r" % (self.energy, self._id)
        for node, cap in self.iteritems():
            assert cap >= 0, "Invalid capacity at node %r: %r" % (node, cap)
        super(Node, self).validate()
        

class Network(Graph):
    """Flow network class."""

    __slots__ = ['_current_state']

    def __init__(self, init={}, VertexType=Node):
        super(Network, self).__init__(init, VertexType)
        self._current_state=0

    def add(self, head, tail=[], capacity=DEFAULT_CAPACITY, edge_collision=ADD):
        super(Network, self).add(head, tail, capacity, edge_collision)
                    
    def tick(self, count=1):
        """Advance network count time increments, defaults to 1.
        >>> n = Network()
        >>> n.add(1, 2, 2)
        >>> n.add(2, 3)
        >>> n.add(3, 1)
        >>> n[1].energy += 4
        >>> n.tick()
        >>> print n.nodes()
        {1: 2, 2: 2, 3: 0}
        >>> n.tick()
        >>> print n.nodes()
        {1: 0, 2: 3, 3: 1}
        >>> n[1].energy += 4
        >>> n.tick(2)
        >>> print n.nodes()
        {1: 2, 2: 5, 3: 1}
        >>> n.discard(3, 1)
        >>> n.add(2, 1)
        >>> n.tick(100)
        >>> print n.nodes()
        {1: 0, 2: 0, 3: 8}
        """
        assert count>=0
        for tic in range(count):
            flow = 0
            for node in self.itervalues():
                flow += abs(node.tick())
            self._current_state = not self._current_state
            if flow == 0: break

    def node_energy(self):
        """Returns total amount of energy in nodes."""
        sum = 0
        for n in self.itervalues():
            sum += n.energy
        return sum
        
    energy = property(node_energy, None, None, "Total energy in network.")

    def _flow(self):
        """Returns total amount of energy moved."""
        sum = 0
        for n in self.itervalues():
            sum += n.energy_out
        return sum

    flow = property(_flow, None, None, "Total energy moved on last tick.")
        
    def nodes(self):
        """Return string of node: energy items."""
        if not self: return '{}'    #nothing to sort
        keys = self.keys()
        keys.sort()
        return '{' + ', '.join(["%r: %r" % (k, self[k].energy) for k in keys]) + '}'

    def validate(self):
        for node in self.itervalues():
            node.validate()
        super(Network, self).validate()
        
def _test():
    import doctest, network
    return doctest.testmod(network)
          
if __name__ == '__main__': _test()
               