import re
import subprocess


def run_measurement(net, client_name, server_name, parallel=None):
    """ 
    run_measurement() will capture the average bandwidth between the hosts
    """

    iperf_proc = start_iperf_between(net, client_name, server_name, parallel)

    out, _ = iperf_proc.communicate()
    out = out.decode('utf-8')
    print(out)
    res = re.findall(r"[0-9]*\.[0-9]+\sMbits/sec", out)
        
    return res[-1]


def run_measurement2(
    net, 
    client_name1, 
    server_name1, 
    client_name2,
    server_name2, 
    parallel1, 
    parallel2
    ):

    iperf_proc1 = start_iperf_between(net, client_name1, server_name1, parallel1)    
    iperf_proc2 = start_iperf_between(net, client_name2, server_name2, parallel2)
    
    out1, _ = iperf_proc1.communicate()    
    out2, _ = iperf_proc2.communicate()    
    
    out1 = out1.decode('utf-8')
    print(out1)
    res1 = re.findall(r"[0-9]*\.[0-9]+\sMbits/sec", out1)
    
    out2 = out2.decode('utf-8')
    print(out2)
    res2 = re.findall(r"[0-9]*\.[0-9]+\sMbits/sec", out2)
    
    return res1[-1], res2[-1]

def run_measurement3(net, c1="h1", c2="h2", c3="h5", s1="h3", s2="h4", s3="h3", parallel1=None, parallel2=None, parallel3=None): 
    iperf_proc1 = start_iperf_between(net, c1, s1, parallel1)    
    iperf_proc2 = start_iperf_between(net, c2, s2, parallel2)
    iperf_proc3 = start_iperf_between(net, c3, s3, parallel3)
    
    out1, _ = iperf_proc1.communicate()    
    out2, _ = iperf_proc2.communicate()    
    out3, _ = iperf_proc3.communicate()
    
    out1 = out1.decode('utf-8')
    # print(out1)
    res1 = re.findall(r"[0-9]*\.[0-9]+\sMbits/sec", out1)
    
    out2 = out2.decode('utf-8')
    # print(out2)
    res2 = re.findall(r"[0-9]*\.[0-9]+\sMbits/sec", out2)

    out3 = out3.decode('utf-8')
    # print(out3)
    res3 = re.findall(r"[0-9]*\.[0-9]+\sMbits/sec", out3)
    
    return [res1[-1], res2[-1], res3[-1]]

def start_iperf_between(net, client, server, parallel=None):

    print (f"Testing bandwidth between {client} and {server}")

    h2 = net.getNodeByName(server)      
    h1 = net.getNodeByName(client)        

    print (f"Starting iperf server on {server}")        
    server = h2.popen(f"iperf -s")        
    print (f"Starting iperf client on {client}")
    
    parallel_flag = ""
    if parallel: parallel_flag = f" -P {parallel}"
    
    iperf_client_command = f"iperf -f m -c {h2.IP()} -u -t 20{parallel_flag}"
    print(iperf_client_command)
    return h1.popen(iperf_client_command ,stdout=subprocess.PIPE)