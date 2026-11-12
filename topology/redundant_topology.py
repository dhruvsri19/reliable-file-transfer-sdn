"""Mininet topology: h1-s1-(s2 primary|s3 backup)-s4-h2."""
from mininet.topo import Topo
class RedundantTransferTopo(Topo):
    def build(self):
        h1, h2 = self.addHost("h1", ip="10.0.0.1/24"), self.addHost("h2", ip="10.0.0.2/24")
        s1, s2, s3, s4 = (self.addSwitch(f"s{i}", protocols="OpenFlow13") for i in range(1,5))
        self.addLink(h1,s1); self.addLink(s1,s2); self.addLink(s2,s4); self.addLink(s1,s3); self.addLink(s3,s4); self.addLink(s4,h2)
topos = {"redundanttransfer": RedundantTransferTopo}
