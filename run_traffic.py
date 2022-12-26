from iperf import run_measurement, run_measurement2, run_measurement3
from util import get_mbits_as_float

import re
import subprocess

def run_measurement_min_traffic(net, client_name, server_name):
    """ 
    run_measurement() will capture the average bandwidth between the hosts
    """

    iperf_proc = generate_minimal_crit_traffic(net, client_name, server_name)

    out, _ = iperf_proc.communicate()
    out = out.decode('utf-8')
    print(out)
    res = re.findall(r"[0-9]*\.[0-9]+\sMbits/sec", out)
    print(res)
        
    return res

def generate_minimal_crit_traffic(net, client, server):
    print (f"Testing bandwidth between {client} and {server}")

    h2 = net.getNodeByName(server)      
    h1 = net.getNodeByName(client)        

    print (f"Starting iperf server on {server}")        
    server = h2.popen(f"iperf -s")        
    print (f"Starting iperf client on {client}")
    
    iperf_client_command = f"iperf -f m -c {h2.IP()} -u -t 20 -b 100000 -l 1000"
    print(iperf_client_command)
    return h1.popen(iperf_client_command ,stdout=subprocess.PIPE)

def run_triple_congestion_measurement_test(net, parallel1, parallel2, parallel3):
    # run individual traffic h1-h3
    t_h1h3, t_h2h4, t_h5h3 = "", "", ""

    try:
        t_h1h3 = run_measurement(net, "h1", "h3", parallel1)
        print (t_h1h3, " between h1 and h3")
    except IndexError:
        print("Traffic could not be sent across 1 and h3")

    # run individual traffic h2-h4
    try:
        t_h2h4 = run_measurement(net, "h2", "h4", parallel2)
        print (t_h2h4, " between h2 and h4")
    except IndexError:
        print("Traffic could not be sent across h2 and h4")
    
    # run individual traffic h5-h3
    try:
        t_h5h3 = run_measurement(net, "h5", "h3", parallel3)
        print (t_h5h3, " between h5 and h3")
    except IndexError:
        print("Traffic could not be sent across h5 and h3")
    
    # run congested traffic
    try:
        t_triple = run_measurement3(net, parallel1=parallel1, parallel2=parallel2, parallel3=parallel3) #use default params
        print(t_triple)
        print (f"H1-H3 Bandwidth: {t_triple[0]}")
        print (f"H2-H4 Bandwidth: {t_triple[1]}")
        print (f"H5-H3 Bandwidth: {t_triple[2]}")
    except IndexError:
        print("Traffic could not be sent across either h1-h3 or h2-h4")

    return {
        "individual": {
            "h1-h3": get_mbits_as_float(t_h1h3),
            "h5-h3": get_mbits_as_float(t_h5h3),
            "h2-h4": get_mbits_as_float(t_h2h4),
        },
        "combined": {
            "h1-h3": get_mbits_as_float(t_triple[0]),
            "h2-h4": get_mbits_as_float(t_triple[1]),
            "h5-h3": get_mbits_as_float(t_triple[2]),
        }
    }

def run_two_way_measurement_test(net, parallel1, parallel2):
    # run individual traffic h1-h3
    try:
        t_h1h3 = run_measurement(net, "h1", "h3", parallel1)
        print (t_h1h3, " between h1 and h3")
    except IndexError:
        print("Traffic could not be sent across 1 and h3")

    # run individual traffic h2-h4
    try:
        t_h2h4 = run_measurement(net, "h2", "h4", parallel2)
        print (t_h2h4, " between h2 and h4")
    except IndexError:
        print("Traffic could not be sent across h2 and h4")
    
    # run congested traffic
    try:
        t_both = run_measurement2(net, "h1", "h3", "h2", "h4", parallel1, parallel2)
        print (f"H1-H3 Bandwidth: {t_both[0]}")
        print (f"H2-H4 Bandwidth: {t_both[1]}")
    except IndexError:
        print("Traffic could not be sent across either h1-h3 or h2-h4")

    return {
        "individual": {
            "h1-h3": get_mbits_as_float(t_h1h3),
            "h2-h4": get_mbits_as_float(t_h2h4),
        },
        "combined": {
            "h1-h3": get_mbits_as_float(t_both[0]),
            "h2-h4": get_mbits_as_float(t_both[1]),
        }
    }

def run_measurement_wrapper(net, function, node1, node2, parallel=1): 
    try:
        bandwidth = function(net, node1, node2, parallel)
        print (bandwidth, " between {node1} and {node2}")
    except IndexError:
        print(f"Traffic could not be sent across {node1} and {node2}") 
        bandwidth = None
    
    return bandwidth