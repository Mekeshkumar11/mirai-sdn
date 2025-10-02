from ryu.ofproto import ofproto_v1_3

def block_ip(datapath, src_ip, idle_timeout=60, hard_timeout=0):
    """
    Install a high-priority drop flow matching IPv4 source address.
    idle_timeout: seconds after which flow is removed if idle
    hard_timeout: absolute time after which flow is removed (0 = permanent)
    """
    ofproto = datapath.ofproto
    parser = datapath.ofproto_parser
    match = parser.OFPMatch(eth_type=0x0800, ipv4_src=src_ip)
    # no actions = drop
    inst = []
    mod = parser.OFPFlowMod(
        datapath=datapath,
        priority=50000,
        match=match,
        instructions=inst,
        idle_timeout=idle_timeout,
        hard_timeout=hard_timeout
    )
    datapath.send_msg(mod)

def unblock_ip(datapath, src_ip):
    """
    Remove any flow matching this src_ip by sending a flow mod with command DELETE.
    """
    ofproto = datapath.ofproto
    parser = datapath.ofproto_parser
    match = parser.OFPMatch(eth_type=0x0800, ipv4_src=src_ip)
    mod = parser.OFPFlowMod(datapath=datapath, command=ofproto.OFPFC_DELETE,
                            out_port=ofproto.OFPP_ANY, out_group=ofproto.OFPG_ANY,
                            match=match, priority=50000)
    datapath.send_msg(mod)
