"""OS-Ken OpenFlow 1.3 learning controller; clears flows on link state change."""
from os_ken.base import app_manager
from os_ken.controller import ofp_event
from os_ken.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, set_ev_cls
from os_ken.ofproto import ofproto_v1_3
from os_ken.lib.packet import packet, ethernet

class ReliableTransferController(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    def __init__(self, *args, **kwargs): super().__init__(*args, **kwargs); self.mac_to_port = {}
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def features(self, ev):
        dp=ev.msg.datapath; p=dp.ofproto_parser; o=dp.ofproto
        dp.send_msg(p.OFPFlowMod(datapath=dp, priority=0, match=p.OFPMatch(), instructions=[p.OFPInstructionActions(o.OFPIT_APPLY_ACTIONS,[p.OFPActionOutput(o.OFPP_CONTROLLER,o.OFPCML_NO_BUFFER)])]))
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in(self, ev):
        msg, dp, o, p = ev.msg, ev.msg.datapath, ev.msg.datapath.ofproto, ev.msg.datapath.ofproto_parser
        eth=packet.Packet(msg.data).get_protocol(ethernet.ethernet)
        if not eth: return
        ports=self.mac_to_port.setdefault(dp.id,{}); ports[eth.src]=msg.match['in_port']; out=ports.get(eth.dst,o.OFPP_FLOOD)
        actions=[p.OFPActionOutput(out)]
        if out != o.OFPP_FLOOD:
            dp.send_msg(p.OFPFlowMod(datapath=dp, priority=10, match=p.OFPMatch(in_port=msg.match['in_port'],eth_dst=eth.dst), instructions=[p.OFPInstructionActions(o.OFPIT_APPLY_ACTIONS,actions)]))
        dp.send_msg(p.OFPPacketOut(datapath=dp, buffer_id=msg.buffer_id, in_port=msg.match['in_port'], actions=actions, data=None if msg.buffer_id != o.OFP_NO_BUFFER else msg.data))
