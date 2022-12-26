import os
import simple_colors

def clean_environment():
    """
    Delete all pre-existing mininet topologies stored in the environment
    """
    print_subtitle("DELETING ALL PRE-EXISTING NETWORKS:")
    os.popen("sudo mn -c").read() #read makes this command synchronous
    print("\n\n")

def print_subtitle(text):
    print("\n" + simple_colors.green(text, ['bold', 'underlined']))

def print_subtitle_l2(text):
    print("\n" + simple_colors.yellow(text, ["bright"]))

def get_mbits_as_float(reading: str):
    try: 
        ret = float(reading.split()[0])
    except IndexError:
        ret = 0 #"Not a list - probably because the test failed :/("
    return ret