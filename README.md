# SDN_Congestion_Detection_Algorithm
SDN Congestion Detection &amp; Mitigation Algorithm

#Background
The widespread use of 5G and the Internet of Things (IoT) has resulted in greater network congestion. While IoT devices may consume minimal bandwidth, the sheer quantity of devices will necessitate an increase in bandwidth and capacity needs. Future applications will demand more bandwidth, putting existing network infrastructures under strain. Some examples of applications requiring high rates and low latency include self-driving cars and virtual reality.

Congestion in a network may have several detrimental effects on data transmission and associated applications. Reduced Quality of Service (QoS), increased latency, connection blockages, and data loss are some of the consequences. Overloading traffic would be resolved by network congestion control and mitigation. SDN (software-defined networks) would enable flexible and dynamic network design. This would be advantageous for maintaining dependable and efficient network connections.

SDN is a networking method that employs software-based controllers or application programming interfaces (APIs) to connect with underlying hardware infrastructure and guide network traffic. While network virtualization enables organisations to segment different virtual networks within a single physical network or to connect devices on different physical networks to form a single virtual network, software-defined networking enables a new method of controlling data packet routing through a centralised server.

#Prior Work Completed
An algorithm is created using a comprehensive SDN testbed,such as Mininet and OpenFlow, to detect congestion-related performance decreases and provide mitigation techniques.Using a Mininet topology as a base, it aimed to simulate congestion by running a controlled amount of traffic over the virtual network.The algorithm would then be able to identify the resulting throughput degradations caused by congestion and make modifications to the network to mitigate negative impacts. In this project, to expand the network a new path has been added to further decongest priority traffic and addingstate-basedmitigation to track the level of mitigation currently employed and roll back to the default if the current traffic is low enough.

The objective of the algorithm designed is to  automated software unit tests using Python to validate the functionality of a Software Defined Network (SDN) solution. And as a result of it, network traffic flow and performance has been improved by 50% through the use of OpenFlow and OVSDB protocols in an SDN environment.
