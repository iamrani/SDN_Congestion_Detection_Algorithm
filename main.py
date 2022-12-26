import time
import subprocess
import os
import re
import sys
from pprint import pprint

import simple_colors

from simulation import Simulation
from util import clean_environment, print_subtitle
from iperf import run_measurement, run_measurement3
from run_traffic import run_measurement_min_traffic
from util import get_mbits_as_float

def test_double_traffic_measurement():
    clean_environment()

    sim = Simulation(0.6)
    sim.create_topology()

    sim.add_initial_flow_table_entries()
    sim.print_all_flow_tables("immediately after creating the topology")

    # Run ping test - ensures all paths are connected
    sim.ping_all()
    sim.print_all_flow_tables("after pingall command")

    initial_measurements = sim.run_double_traffic_measurement_test(context="INITIAL")
    
    indiv_h1h3 = initial_measurements["individual"]["h1-h3"]
    combined_h1h3 = initial_measurements["combined"]["h1-h3"]
    
    if indiv_h1h3*sim.congestion_coefficient > combined_h1h3:
        print_subtitle("CONGESTION WAS DETECTED!")

        sim.congestion_mitigation()
        sim.print_all_flow_tables("after congestion mitigation")
        input("continue?")
        sim.ping_all()

        mitigated_measurements = sim.run_double_traffic_measurement_test(context="AFTER APPLYING MITIGATION")
        sim.print_all_flow_tables("after congestion mitigation measurement test")

        print_subtitle("Comparing before and after mitigation:")
        print("Before mitigation: ", combined_h1h3)
        print("After mitigation: ", mitigated_measurements["combined"]["h1-h3"])

def test_parallel_double_traffic_measurement(parallel_flows=None):
    clean_environment()

    sim = Simulation(0.9)
    sim.create_topology()

    sim.add_initial_flow_table_entries()
    sim.print_all_flow_tables("immediately after creating the topology")

    # Run ping test - ensures all paths are connected
    sim.ping_all()

    initial_measurements = sim.run_double_traffic_measurement_test(context="INITIAL", parallel1=parallel_flows)
    
    indiv_h1h3 = initial_measurements["individual"]["h1-h3"]
    combined_h1h3 = initial_measurements["combined"]["h1-h3"]
    
    if indiv_h1h3*sim.congestion_coefficient > combined_h1h3:
        print_subtitle("CONGESTION WAS DETECTED!")

        sim.congestion_mitigation()
        sim.print_all_flow_tables("after congestion mitigation")
        input("continue?")
        sim.ping_all()

        mitigated_measurements = sim.run_double_traffic_measurement_test(context="AFTER APPLYING MITIGATION", parallel1=parallel_flows)
        sim.print_all_flow_tables("after congestion mitigation measurement test")

        print_subtitle("Comparing before and after mitigation:")
        print("Before mitigation: ", combined_h1h3)
        print("After mitigation: ", mitigated_measurements["combined"]["h1-h3"]) 

def test_parallel_triple_traffic_measurement(h1h3_parallel=None, h2h4_parallel=None, h5h3_parallel=None):
    clean_environment()

    sim = Simulation(0.9)
    sim.create_topology()

    sim.add_initial_flow_table_entries()
    sim.print_all_flow_tables("immediately after creating the topology")

    # Run ping test - ensures all paths are connected
    sim.ping_all()

    initial_measurements = sim.run_triple_traffic_congestion_measurement_test(context="INITIAL", parallel1=h1h3_parallel, parallel2=h2h4_parallel, parallel3=h5h3_parallel)
    
    indiv_h1h3 = initial_measurements["individual"]["h1-h3"]
    combined_h1h3 = initial_measurements["combined"]["h1-h3"]
    combined_h5h3 = initial_measurements["combined"]["h5-h3"]
    
    if indiv_h1h3*sim.congestion_coefficient > combined_h1h3:
        print_subtitle("CONGESTION WAS DETECTED!")

        sim.create_third_path()
        sim.print_all_flow_tables("after congestion mitigation")
        input("continue?")
        sim.ping_all()

        mitigated_measurements = sim.run_triple_traffic_congestion_measurement_test(context="AFTER APPLYING MITIGATION", parallel1=h1h3_parallel, parallel2=h2h4_parallel, parallel3=h5h3_parallel)
        sim.print_all_flow_tables("after congestion mitigation measurement test")

        print_subtitle("Comparing before and after mitigation:")
        print("Before h1h3 mitigation: ", combined_h1h3)
        print("After h1h3 mitigation: ", mitigated_measurements["combined"]["h1-h3"]) 


        print("Before h5h3 mitigation: ", combined_h5h3)
        print("After h5h3 mitigation: ", mitigated_measurements["combined"]["h5-h3"]) 

def revert_to_default_path():
    clean_environment()

    sim = Simulation(0.9)
    sim.create_topology()

    sim.create_third_path()
    sim.print_all_flow_tables("with max mitigation")

    crit_traffic = run_measurement_min_traffic(sim.net, "h1", "h3")
    print(f"Traffic between h1 and h3 is {crit_traffic}")
    crit_traffic = get_mbits_as_float(crit_traffic[0])

    boundary = sim.ratio_to_revert*1 # hard coded to 1 Mbit.sec

    if crit_traffic < boundary and sim.congestion_mitigation_state > 1:
        print_subtitle("Traffic sent was below boundary level. Reverting to mitigation state 1")
        sim.add_initial_flow_table_entries()
        sim.print_all_flow_tables("after reverting to default path")

if __name__ == '__main__':
    # CASE 1:
    # test_double_traffic_measurement()

    # CASE 2: bandwidth choked links + parallel clients
    # test_parallel_double_traffic_measurement(7)

    # CASE 3: 
    # test_parallel_triple_traffic_measurement(h1h3_parallel=7, h5h3_parallel=5)

    # CASE 4:
    revert_to_default_path()





    # clean_environment()
    # sim = Simulation(0.9)
    # sim.create_topology()
    # run_measurement3(sim.net, parallel1=7, parallel3=5) #use default params
        
    
 







    # print_subtitle("DEACTIVATING A LINK:")
    # sim.deactivate_link("s1", "s2")
    # sim.ping_all()
    
    # s1 = sim.net.getNodeByName("s1")
    # s2 = sim.net.getNodeByName("s2")
    # print(s1, s2)
    # print("links between: ", sim.net.linksBetween(s1, s2))
    # print("link status: ", sim.net.linksBetween(s1, s2)[0].status())
    # print("link status: ", sim.net.linksBetween(s1, s2)[0].intf1.isUp())

    # sim.monitor_network()