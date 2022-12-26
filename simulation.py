#import all mininet classes
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel, info
from mininet.node import Controller, RemoteController, OVSSwitch
from mininet.cli import CLI
from mininet.util import pmonitor
from mininet.link import TCLink
from functools import partial

import time
import subprocess
import os
import re
import sys
from pprint import pprint

import simple_colors

from topo import create_topology
from util import print_subtitle, print_subtitle_l2
from run_traffic import run_measurement_min_traffic, run_two_way_measurement_test, run_triple_congestion_measurement_test

class Simulation:

    def __init__(self, coeff=0.6):
        print(simple_colors.blue("STARTING THE SIMULATION:\n", ['bold', 'underlined']))
        self.net = Mininet(controller=RemoteController, switch=OVSSwitch, link=TCLink) # Create network
        self.cli = CLI(self.net, script='null_script') # Add CLI for this network
        self.congestion_coefficient = coeff
        self.congestion_mitigation_state = None
        self.ratio_to_revert = 0.5

    def create_topology(self):
        """
        Add hosts, switches and links
        """
        create_topology(self.net)
        print_subtitle("Network connections:") #PRINT NETWORK THAT WAS CREATED
        self.cli.do_net(self.net)

    def add_initial_flow_table_entries(self):
        """ s1 - s3 (default route) forwards packets"""
        print_subtitle("Adding initial flow table entries")
        default_route = ["s1", "s3",]  
        self._assign_l2_switch_behavior(default_route)
        remove_switches = ["s2", "s4"]
        self._delete_all_flows_in(remove_switches)
        self.congestion_mitigation_state = 1

    def generate_minimal_crit_traffic(self):
        run_measurement_min_traffic(self.net, "h1", "h3")

    def _assign_l2_switch_behavior(self, switches: list):
        for switch in switches:
            self.cli.do_sh(f'ovs-ofctl del-flows {switch}')
            self.cli.do_sh(f'ovs-ofctl add-flow {switch} table=0,priority=200,actions=normal')

    def _delete_all_flows_in(self, switches: list):
        for switch in switches:
            self.cli.do_sh(f'ovs-ofctl del-flows {switch}')

    def congestion_mitigation(self):
        self.create_second_path()
        self.congestion_mitigation_state = 2

    def create_second_path(self):
        # when traffic is given to s2, it forwards it!
        self._assign_l2_switch_behavior(["s2"]) 
        # make s1 route half the traffic to s2
        self._set_s1_second_path_flows()
        self._set_s3_second_path_flows()

    def _set_s1_second_path_flows(self):
        self.cli.do_sh(f'ovs-ofctl del-flows s1') 
        # add flows for background traffic
        self.cli.do_sh('ovs-ofctl add-flow s1 priority=400,dl_type=0x0800,nw_dst=10.0.0.2,actions=output:2')
        self.cli.do_sh('ovs-ofctl add-flow s1 priority=400,dl_type=0x0800,nw_dst=10.0.0.4,actions=output:4')
        #for host 5 <3
        self.cli.do_sh('ovs-ofctl add-flow s1 priority=400,dl_type=0x0800,nw_dst=10.0.0.5,actions=output:6')
        # # priority traffic
        self.cli.do_sh('ovs-ofctl add-flow s1 priority=400,dl_type=0x0800,nw_dst=10.0.0.1,actions=output:1')
        #self.cli.do_sh('ovs-ofctl add-flow s1 priority=400,dl_type=0x0800,nw_dst=10.0.0.3,actions=output:3')
        # self.cli.do_sh('ovs-ofctl add-flow s1 priority=0,in_port=1,actions=output:4') # catch all case
        # create group flow table
        create_group = "ovs-ofctl add-group s1 group_id=1,type=select,selection_method=dp_hash,bucket=weight:5,output:3,bucket=weight:1,output:4"
        self.cli.do_sh(create_group)
        add_group_flow = "ovs-ofctl add-flow s1 priority=800,dl_type=0x0800,nw_dst=10.0.0.3,actions=group:1"
        self.cli.do_sh(add_group_flow)

    def _set_s3_second_path_flows(self):
        """
            p1->s2, p2->s1, p3->h3, p4->h4
        """
        self.cli.do_sh(f'ovs-ofctl del-flows s3') 
        # add flows for background traffic
        self.cli.do_sh('ovs-ofctl add-flow s3 priority=400,dl_type=0x0800,nw_dst=10.0.0.2,actions=output:2')
        self.cli.do_sh('ovs-ofctl add-flow s3 priority=400,dl_type=0x0800,nw_dst=10.0.0.4,actions=output:4')
        # priority traffic
        # self.cli.do_sh('ovs-ofctl add-flow s3 priority=400,dl_type=0x0800,nw_dst=10.0.0.1,actions=output:1') # p1 -> s2
        self.cli.do_sh('ovs-ofctl add-flow s3 priority=400,dl_type=0x0800,nw_dst=10.0.0.3,actions=output:3') # p2 -> s1
        # create group flow table
        create_group = "ovs-ofctl add-group s3 group_id=1,type=select,selection_method=dp_hash,bucket=output:1,bucket=output:2"
        self.cli.do_sh(create_group)
        #add group flow
        self.cli.do_sh("ovs-ofctl add-flow s3 priority=800,dl_type=0x0800,nw_dst=10.0.0.1,actions=group:1")
        # add return path for h5
        self.cli.do_sh("ovs-ofctl add-flow s3 priority=800,dl_type=0x0800,nw_dst=10.0.0.5,actions=group:1")

    def create_third_path(self):
        self._assign_l2_switch_behavior(["s2", "s4"])
        self._set_s1_third_path_flows()
        self._set_s3_third_path_flows()
        self.congestion_mitigation_state = 3

    def _set_s1_third_path_flows(self):
        self.cli.do_sh(f'ovs-ofctl del-flows s1') 
        # add flows for background traffic
        self.cli.do_sh('ovs-ofctl add-flow s1 priority=400,dl_type=0x0800,nw_dst=10.0.0.2,actions=output:2')
        self.cli.do_sh('ovs-ofctl add-flow s1 priority=400,dl_type=0x0800,nw_dst=10.0.0.4,actions=output:4')
        self.cli.do_sh('ovs-ofctl add-flow s1 priority=400,dl_type=0x0800,nw_dst=10.0.0.5,actions=output:6')
        # # priority traffic
        self.cli.do_sh('ovs-ofctl add-flow s1 priority=400,dl_type=0x0800,nw_dst=10.0.0.1,actions=output:1')
        # create group flow table
        # create_group = "ovs-ofctl add-group s1 group_id=1,type=select,selection_method=dp_hash,bucket=output:3,bucket=output:4,bucket=output:5"
        create_group = "ovs-ofctl add-group s1 group_id=1,type=select,selection_method=dp_hash,bucket=weight:5,actions=output:3,bucket=weight:1,actions=output:4,bucket=weight:7,actions=output:5"
        self.cli.do_sh(create_group)
        add_group_flow = "ovs-ofctl add-flow s1 priority=800,dl_type=0x0800,nw_dst=10.0.0.3,actions=group:1"
        self.cli.do_sh(add_group_flow)
    
    def _set_s3_third_path_flows(self):
        """
            p1->s2, p2->s1, p3->h3, p4->h4
        """
        self.cli.do_sh(f'ovs-ofctl del-flows s3') 
        # add flows for background traffic
        self.cli.do_sh('ovs-ofctl add-flow s3 priority=400,dl_type=0x0800,nw_dst=10.0.0.2,actions=output:2')
        self.cli.do_sh('ovs-ofctl add-flow s3 priority=400,dl_type=0x0800,nw_dst=10.0.0.4,actions=output:4')
        # priority traffic
        # self.cli.do_sh('ovs-ofctl add-flow s3 priority=400,dl_type=0x0800,nw_dst=10.0.0.1,actions=output:1') # p1 -> s2
        self.cli.do_sh('ovs-ofctl add-flow s3 priority=400,dl_type=0x0800,nw_dst=10.0.0.3,actions=output:3') # p2 -> s1
        # create group flow table
        create_group = "ovs-ofctl add-group s3 group_id=1,type=select,selection_method=dp_hash,bucket=output:1,bucket=output:2,bucket=output:5"
        self.cli.do_sh(create_group)
        # add_group_flow 
        self.cli.do_sh("ovs-ofctl add-flow s3 priority=800,dl_type=0x0800,nw_dst=10.0.0.1,actions=group:1")
        self.cli.do_sh("ovs-ofctl add-flow s3 priority=800,dl_type=0x0800,nw_dst=10.0.0.5,actions=group:1")

    def print_all_flow_tables(self, context: str):
        """ Print flow table entries for the whole network """
        print("__________________________________________________________")
        print_subtitle(f"printing flow tables {context}")
        all_nodes = self.net.keys()
        for node in all_nodes:
            if node[0] == "h":
                continue
            else:
                print_subtitle_l2(f"printing flow table for {node}:")
                self.cli.do_sh(f'ovs-ofctl dump-flows {node}')
                self.cli.do_sh(f'ovs-ofctl queue-stats {node}')
                self.cli.do_sh(f"ovs-ofctl dump-group-stats {node}")
        print("__________________________________________________________")

    def ping_all(self):
        print_subtitle("Attempt ping all:") 
        self.net.pingAll()

    def run_double_traffic_measurement_test(self, context="", parallel1=None, parallel2=None):
        """ use iperf to generate constant traffic """
        print_subtitle (f"Running Measurement Test: {context}")
        return run_two_way_measurement_test(self.net, parallel1, parallel2)
    
    def run_triple_traffic_congestion_measurement_test(self, context="", parallel1=None, parallel2=None, parallel3=None):
        """ use iperf to generate constant traffic """
        print_subtitle (f"Running h1->h3, h2->h4, h5->h3 Measurement Test: {context}") 
        return run_triple_congestion_measurement_test(self.net, parallel1, parallel2, parallel3)
