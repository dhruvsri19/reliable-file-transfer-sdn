"""Deterministic OpenFlow 1.3 primary/backup forwarding for the lab topology."""
from os_ken.base import app_manager
from os_ken.controller import ofp_event
from os_ken.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, set_ev_cls
from os_ken.ofproto import ofproto_v1_3

H1, H2 = "00:00:00:00:00:01", "00:00:00:00:00:02"
class ReliableTransferController(app_manager.OSKenApp):
    OFP_VERSIONS=[ofproto_v1_3.OFP_VERSION]
    def __init__(self,*a,**kw): super().__init__(*a,**kw); self.dps={}; self.backup=False
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def features(self,ev):
        dp=ev.msg.datapath; self.dps[dp.id]=dp; self.install_if_ready()
    def flow(self,dp,dst,port):
        p,o=dp.ofproto_parser,dp.ofproto
        match=p.OFPMatch(eth_dst=dst); inst=[p.OFPInstructionActions(o.OFPIT_APPLY_ACTIONS,[p.OFPActionOutput(port)])]
        dp.send_msg(p.OFPFlowMod(datapath=dp,command=o.OFPFC_DELETE,out_port=o.OFPP_ANY,out_group=o.OFPG_ANY,match=match))
        dp.send_msg(p.OFPFlowMod(datapath=dp,priority=100,match=match,instructions=inst))
    def install_if_ready(self):
        if set(self.dps) != {1,2,3,4}: return
        routes=({1:(2,1),2:(2,1),3:(2,1),4:(3,1)} if not self.backup else {1:(3,1),2:(2,1),3:(2,1),4:(3,2)})
        for dpid,(to_h2,to_h1) in routes.items(): self.flow(self.dps[dpid],H2,to_h2); self.flow(self.dps[dpid],H1,to_h1)
        self.logger.info("ROUTE=%s", "backup(s3)" if self.backup else "primary(s2)")
    @set_ev_cls(ofp_event.EventOFPPortStatus, MAIN_DISPATCHER)
    def port_status(self,ev):
        msg=ev.msg
        if msg.reason in (msg.datapath.ofproto.OFPPR_DELETE,msg.datapath.ofproto.OFPPR_MODIFY) and not self.backup:
            if (msg.datapath.id==1 and msg.desc.port_no==2) or msg.datapath.id==2:
                self.backup=True; self.logger.warning("PRIMARY LINK FAILURE: activating s3 backup"); self.install_if_ready()
