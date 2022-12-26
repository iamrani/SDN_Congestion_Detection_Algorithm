from mininet.link import TCLink

def create_topology(net):
    """
    Builds the network! 
    """
    # Add hosts and switches

    h1 = net.addHost( 'h1' )
    h2 = net.addHost( 'h2' )
    h3 = net.addHost( 'h3' )
    h4 = net.addHost( 'h4' )
    h5 = net.addHost( 'h5' )

    s1 = net.addSwitch( 's1' )
    s2 = net.addSwitch( 's2' )
    s3 = net.addSwitch( 's3' )
    s4 = net.addSwitch( 's4' ) #New switch created to ease the conjestion 

    # Add links

    net.addLink( h1, s1, cls=TCLink, bw=2 )
    net.addLink( h2, s1, cls=TCLink, bw=2 )
    net.addLink( s1, s2, cls=TCLink, bw=1 )
    net.addLink( s2, s3, cls=TCLink, bw=1 )
    net.addLink( s1, s3, cls=TCLink, bw=1 )
    net.addLink( s3, h3, cls=TCLink, bw=5 )
    net.addLink( s3, h4, cls=TCLink, bw=2 )
    net.addLink( s4, s3, cls=TCLink, bw=1 ) #New Link between Switch 4 and 3
    net.addLink( s1, s4, cls=TCLink, bw=1 ) #New Link between Switch 1 and 4

    net.addLink( h5, s1, cls=TCLink, bw=2 )

    # # Add links
    # net.addLink( h1, s1 )
    # net.addLink( h2, s1 )
    # net.addLink( h3, s3 )
    # net.addLink( h4, s3 )
    # # Default path: S1 - S3 in the middle
    # net.addLink( s1, s3 )
    # # Secondary path: S1 - S2 - S3 bottom path
    # net.addLink( s1, s2 )
    # net.addLink( s2, s3 )
    # # Our new path: S1 - S4 - S3 top path
    # net.addLink( s1, s4 )
    # net.addLink( s4, s3 )

    net.build()
    net.start()
    net.staticArp()