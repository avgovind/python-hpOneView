import json
import hpOneView.connection
import hpOneView.networking


def Add_Networks(json_file):

    input_config_file = open(json_file, 'r')
    # Set appliance IP address and User login credentials
    host = "15.215.17.33"
    cred = {'userName': 'Administrator', 'password': "Welcome123"}

    input_config_json = json.load(input_config_file)

    # read the IP, username and password from the input json file
    host = input_config_json['Appliance']['IP']
    cred['userName'] = input_config_json['Appliance']['Username']
    cred['password'] = input_config_json['Appliance']['Password']

#     session = HPCIManager.login(host, cred)
    conn = hpOneView.connection(host)
    session = conn.login(cred, False)

    # Creating Ethernet network
    # Creating an Ethernet network using REST APIs
    # Select a connection template.
    # GET /rest/connection-templates
    # Create the network.
    # POST rest/ethernet-networks
    net = hpOneView.networking(conn)

    #now load the inputs for Ethernet network configuration
    for net_cfg in input_config_json['EthernetNetwork']:

        enet_list = []
        count_items = net_cfg['count']
        base_vlanid = net_cfg['vlanid_start']
        if count_items > 0:
            # to configure for multiple network configurations using a range
            for i in range(count_items):
                vlanid = base_vlanid + i
                bandDict = hpOneView.common.make_bw_dict(
                                maxbw=net_cfg['maximumBandwidth'],
                                minbw=net_cfg['preferredBandwidth']
                                )
                enet = net.create_enet_network(net_cfg['prefix'] + str(vlanid),
                                vlanid,
                                smartLink=net_cfg['smartLink'],
                                privateNetwork=net_cfg['privateNetwork'],
                                bw=bandDict)
                enet_list.append(enet['uri'])
            # end of     for i in range( count_items):
            net.create_networkset(net_cfg['networkset'], enet_list, bandDict)
#                 HPCIManager.New_HPCIEthNetwork(host, session, net)
        else:
        # if not range then it must be individual item
            bandDict = hpOneView.common.make_bw_dict(
                                maxbw=net_cfg['maximumBandwidth'],
                                minbw=net_cfg['preferredBandwidth']
                                )

            enet = net.create_enet_network(net_cfg['name'],
                                net_cfg['vlanid'],
                                smartLink=net_cfg['smartLink'],
                                privateNetwork=net_cfg['privateNetwork'],
                                bw=bandDict)
            enet_list.append(enet['uri'])
            net.create_networkset(net_cfg['networkset'], enet_list, bandDict)

    #now load the inputs for FC network configuration
    for fcnet_cfg in input_config_json['FCNetwork']:
        count_items = fcnet_cfg['count']
        if count_items > 1:
            # Configure for multiple network configurations using a range
            for i in range(count_items):
                bandDict = hpOneView.common.make_bw_dict(
                                        maxbw=fcnet_cfg['maximumBandwidth'],
                                        minbw=fcnet_cfg['preferredBandwidth']
                                        )
                fcnet = net.create_fc_network(
                                        fcnet_cfg['prefix'] + str(i),
                                        attach=fcnet_cfg['fabricType'],
                                        bw=bandDict
                                        )
        else:
        # if not range then it must be individual item
            bandDict = hpOneView.common.make_bw_dict(
                                        maxbw=fcnet_cfg['maximumBandwidth'],
                                        minbw=fcnet_cfg['preferredBandwidth']
                                        )
            fcnet = net.create_fc_network(
                        fcnet_cfg['name'],
                        attach=fcnet_cfg['fabricType'],
                        bw=bandDict)

#             HPCIManager.New_HPCIFCNetwork(host, session, net)

    #for net_cfg in input_config_json['EthernetNetwork']:


def Delete_EthernetNetworks(json_file):
    input_config_file = open(json_file, 'r')
    # Set appliance IP address and User login credentials
    host = "15.215.17.33"
    cred = {'userName': 'Administrator', 'password': "Welcome123"}

    input_config_json = json.load(input_config_file)
    # read the IP, username and password from the input json file
    host = input_config_json['Appliance']['IP']
    cred['userName'] = input_config_json['Appliance']['Username']
    cred['password'] = input_config_json['Appliance']['Password']

#     session = HPCIManager.login(host, cred)
    conn = hpOneView.connection(host)
    session = conn.login(cred, False)
    net = hpOneView.networking(conn)

    # First get all networks
    # TODO: This code may give problems if there are too many network items.
    # Need to deal with the size using pagination and compression
    enets = net.get_enet_networks()

    for netcfg in input_config_json['EthernetNetwork']:
        # stringpattern is array of list of all ethernet network names
        # deduced from netcfg
        stringpattern = []
        if netcfg['count'] > 1:
        # This configuration has range of items so a string match pattern
        # should be created
            for i in range(netcfg['count']):
                suffix = netcfg['vlanid_start'] + i
                stringpattern.append(netcfg['prefix'] + str(suffix))
        else:
            # in this case there will be only one name but still
            # storing in array for code consistency
            stringpattern.append(netcfg['name'])
        for enet in enets:
            if enet['name'] in stringpattern:
            # found matching eth network configuration to delete
                net.delete_network(enet, blocking=False)
                print("Deleting the Ethernet network: " + enet['name'])


def Delete_FCNetworks(json_file):
    input_config_file = open(json_file, 'r')
    # Set appliance IP address and User login credentials
    host = "15.215.17.33"
    cred = {'userName': 'Administrator', 'password': "Welcome123"}
    input_config_json = json.load(input_config_file)

    # read the IP, username and password from the input json file
    host = input_config_json['Appliance']['IP']
    cred['userName'] = input_config_json['Appliance']['Username']
    cred['password'] = input_config_json['Appliance']['Password']

#     session = HPCIManager.login(host, cred)
    conn = hpOneView.connection(host)
    session = conn.login(cred, False)

    net = hpOneView.networking(conn)

    #
    # First get all networks
    # TODO: This code may give problems if there are too many number of network
    # Need to deal with the size using pagination and compression

    fcnets = net.get_fc_networks()

    for netcfg in input_config_json['FCNetwork']:

        # stringpattern is array of list of all ethernet network names
        # deduced from netcfg
        stringpattern = []
        if netcfg['count'] > 1:
        # This configuration has range of items so a string match pattern
        # should be created
            for i in range(netcfg['count']):
                suffix = i
                stringpattern.append(netcfg['prefix'] + str(suffix))
        else:
            # in this case there will be only one name but still storing in
            # array for code consistency
            stringpattern.append(netcfg['name'])

        # TODO: optimize this code
        for fcnet in fcnets:
            if fcnet['name'] in stringpattern:
                # found matching eth network configuration, so delete it
                net.delete_network(fcnet, blocking=False)
                print("Deleting the fc network: " + fcnet['name'])

#####def Delete_FCNetworks(json_file): - END


def Create_LogicalLogicalInterconnectGroup(json_file):
    input_config_file = open(json_file, 'r')
    # Set appliance IP address and User login credentials
    host = "15.215.17.33"
    cred = {'userName': 'Administrator', 'password': "Welcome123"}

    input_config_json = json.load(input_config_file)
    # read the IP, username and password from the input json file
    host = input_config_json['Appliance']['IP']
    cred['userName'] = input_config_json['Appliance']['Username']
    cred['password'] = input_config_json['Appliance']['Password']

#     session = HPCIManager.login(host, cred)
    conn = hpOneView.connection(host)
    session = conn.login(cred, False)
    net = hpOneView.networking(conn)

    # Get list of all the valid interconnect types
    # Interconnect type is name of the interconnect with product number
    switchtypes = net.get_interconnect_types()
    print(switchtypes)

    lig = hpOneView.common.make_lig_dict(
                input_config_json['LogicalSwitchTemplate']['Name'])

    for switchcfg in input_config_json['LogicalSwitchTemplate']['switches']:
        print(switchcfg)
        for switchtype in switchtypes:
            if switchcfg['PermittedSwitchType'] == switchtype['name']:
                # Assign the switch URI to the bay
                #TODO: Got to improve this line
                bay_numbers = []
                bay_numbers.append(switchcfg['Bay'])
                # # Set IO bay occupancy
                # lig['interconnectMapTemplate']
                # - this is the switch map
                hpOneView.common.set_iobay_occupancy(
                       lig['interconnectMapTemplate'],
                       bay_numbers, switchtype['uri']
                       )
                break

    # Get the mapping for switch port name and port number for each supported
    # interconnect type array to convert Uplink Port number to port name
    # like X1
    # Typically the mapping is like this {X1 = 17;X2 = 18;X3 = 19;X4 = 20;
    # X5 = 21;X6 = 22;X7 = 23;X8 = 24}
    # But the below script gets this mapping based on the switchtypes data
    # for a given Interconnect type so takes care of any changes in switch
    # port numbers
    # Table providing mapping between switch port name and number
    switchPortTable = {}
    switchTypesTable = {}
    switchTypesURITable = {}
    for switchtype in switchtypes:
        switchPortTable = {}
        for portinfo in switchtype['portInfos']:
            switchPortTable[portinfo['portName']] = portinfo['portNumber']
        # mapping of switchtype model name and switchPortTable
        # because I assume that switch ports and their numbers are different
        # for different switch types
        print(switchtype)
        print(switchPortTable)
        switchTypesTable[switchtype['name']] = switchtype['uri']
        # now map switchtype model name and URI
        # because I assume that switch ports and their numbers are different
        # for different switch types
        switchTypesURITable[switchtype['uri']] = switchPortTable

    ports = []
    networkuris = []
    logicaluplink = None
    listLogicalUplinks = []

    # Create the logical uplinks and assign the switch ports
    # as per the configuration
    for uplink in input_config_json['LogicalSwitchTemplate']['uplinks']:
        for network_name in uplink['Networks']:
            if uplink['Type'] == "Ethernet":
                network_item = net.get_enet_network_by_name(network_name)
            elif uplink['Type'] == "FibreChannel":
                network_item = net.get_fc_network_by_name(network_name)

            networkuris.append(network_item['uri'])

        for uplinkport in uplink['UplinkPorts']:
            # Bays are identified using 1 based index, but the objects in
            # Python arrays are using 0 based index
            # so need to subtract 1 from the bay number to get
            # its object from the array
            a = lig['interconnectMapTemplate']
            b = a['interconnectMapEntryTemplates']
            interconnect_map1 = b[uplinkport['Bay'] - 1]

            ic_uri = interconnect_map1['permittedInterconnectTypeUri']
            switchporttable1 = switchTypesURITable[ic_uri]

            print(switchporttable1)
            port1 = switchporttable1[uplinkport['Port']]
            bay1 = uplinkport['Bay']

            locSwitch1 = {"locationEntries": [
                                {"type":'Port', "relativeValue":port1},
                                {"type":'Bay', "relativeValue":bay1},
                                {"type":'Enclosure', "relativeValue":1}
                                ]
                          }
            p = {"desiredSpeed": "Auto", "logicalLocation": locSwitch1}
            ports.append(p)

        logicaluplink = {
#                 "logicalUplinkName": uplink['UplinkName'],
                "name": uplink['UplinkName'],
                "mode": uplink['ConnectionMode'],
                "networkUris": networkuris,
                "networkType": uplink['Type'],
                "logicalPortConfigInfos": ports,
                "primaryPort": None,
                "nativeNetworkUri": None,
                "reachability": None
        }
        listLogicalUplinks.append(logicaluplink)
        networkuris = []
        ports = []
        logicaluplink = None

    #assign the switchmap entries to the logical switch template
    # Now create the actual logical switch template
    lig['uplinkSets'] = listLogicalUplinks
    print(lig)
#     newlst = HPCIManager.New_HPCILogicalSwitchTemplate(host, session, lst)
    newlig = net.create_lig(lig)
    print(newlig)

#### def Create_LogicalSwitchTemplate(json_file): -- END


def Update_LogicalInterconnectGroup(json_file):
    input_config_file = open(json_file, 'r')
    # Set appliance IP address and User login credentials
    host = "15.215.17.33"
    cred = {'userName': 'Administrator', 'password': "Welcome123"}
    input_config_json = json.load(input_config_file)

    # read the IP, username and password from the input json file
    host = input_config_json['Appliance']['IP']
    cred['userName'] = input_config_json['Appliance']['Username']
    cred['password'] = input_config_json['Appliance']['Password']

#     session = HPCIManager.login(host, cred)
    conn = hpOneView.connection(host)
    session = conn.login(cred, False)

    net = hpOneView.networking(conn)

    lig_name = input_config_json['Update']['LogicalSwitchTemplate']['Name']

    lig = net.get_lig_by_name(lig_name)

    print(lig)
    # Get list of all the valid interconnect types
    # Interconnect type is name of the interconnect with product number
    switchtypes = net.get_interconnect_types()

    # Get the mapping for switch port name and port number for each supported
    # interconnect type array to convert Uplink Port number to port name
    # like X1
    # Typically the mapping is like this {X1 = 17;X2 = 18;X3 = 19;X4 = 20;
    # X5 = 21;X6 = 22;X7 = 23;X8 = 24}
    # But the below script gets this mapping based on the switchtypes data
    # for a given Interconnect type so takes care of any changes in switch
    # port numbers
    # Table providing mapping between switch port name and number
    switchPortTable = {}
    switchTypesTable = {}
    switchTypesURITable = {}
    for switchtype in switchtypes:
        switchPortTable = {}
        for portinfo in switchtype['portInfos']:
            switchPortTable[portinfo['portName']] = portinfo['portNumber']
        # mapping of switchtype model name and switchPortTable
        # because I assume that switch ports and their numbers are different
        # for different switch types
        print(switchtype)
        print(switchPortTable)
        switchTypesTable[switchtype['name']] = switchtype['uri']
        # now map switchtype model name and URI
        # because I assume that switch ports and their numbers are different
        # for different switch types
        switchTypesURITable[switchtype['uri']] = switchPortTable

    # Create the logical uplinks and assign the switch ports
    # as per the configuration
    ports = []
    networkuris = []
    logicaluplink = None
    listLogicalUplinks = []

    updated_lig_config = input_config_json['Update']['LogicalSwitchTemplate']
    for uplink in updated_lig_config['uplinks']:
        for network_name in uplink['Networks']:
            if uplink['Type'] == "Ethernet":
                network_item = net.get_enet_network_by_name(network_name)
            elif uplink['Type'] == "FibreChannel":
                network_item = net.get_fc_network_by_name(network_name)

            networkuris.append(network_item['uri'])

        for uplinkport in uplink['UplinkPorts']:
            # Bays are identified using 1 based index, but the objects in
            # Python arrays are using 0 based index
            # so need to subtract 1 from the bay number to get
            # its object from the array
            interconnectMap = lig['interconnectMapTemplate']
            interconnect_map1 = hpOneView.common.get_iobay_entry(
                                                interconnectMap,
                                                uplinkport['Bay'] - 1)

            ic_uri = interconnect_map1['permittedInterconnectTypeUri']
            switchporttable1 = switchTypesURITable[ic_uri]

            print(switchporttable1)
            port1 = switchporttable1[uplinkport['Port']]
            bay1 = uplinkport['Bay']

            locSwitch1 = {"locationEntries": [
                                {"type":'Port', "relativeValue":port1},
                                {"type":'Bay', "relativeValue":bay1},
                                {"type":'Enclosure', "relativeValue":1}
                                ]
                          }
            p = {"desiredSpeed": "Auto", "logicalLocation": locSwitch1}
            ports.append(p)

    logicaluplink = {
            "name": uplink['UplinkName'],
            "mode": uplink['ConnectionMode'],
            "networkUris": networkuris,
            "networkType": uplink['Type'],
            "logicalPortConfigInfos": ports,
            "primaryPort": None,
            "nativeNetworkUri": None,
            "reachability": None
    }
    listLogicalUplinks.append(logicaluplink)
    networkuris = []
    ports = []
    logicaluplink = None

    desc = input_config_json['Update']['LogicalSwitchTemplate']['Description']
    lig['description'] = desc
    for uplinkitem in listLogicalUplinks:
        lig['uplinkSets'].append(uplinkitem)

    net.update_lig(lig)
    updated_lig = net.get_lig_by_name(lig_name)
    print(updated_lig)


def Delete_LogicalInterconnectGroup(json_file):

    input_config_file = open(json_file, 'r')
    # Set appliance IP address and User login credentials
    host = "15.215.17.33"
    cred = {'userName': 'Administrator', 'password': "Welcome123"}

    input_config_json = json.load(input_config_file)

    # read the IP, username and password from the input json file
    host = input_config_json['Appliance']['IP']
    cred['userName'] = input_config_json['Appliance']['Username']
    cred['password'] = input_config_json['Appliance']['Password']

#     session = HPCIManager.login(host, cred)
    conn = hpOneView.connection(host)
    session = conn.login(cred, False)
    net = hpOneView.networking(conn)
    lig_name = input_config_json['LogicalSwitchTemplate']['Name']
    logical_interconnect_group = net.get_lig_by_name(
                                    lig_name
                                )
    print(logical_interconnect_group)
    net.delete_lig(logical_interconnect_group)


def Import_Enclosure(json_file):

    print("Importing the enclosure")

    input_config_file = open(json_file, 'r')
    # Set appliance IP address and User login credentials
    host = "15.215.17.33"
    cred = {'userName': 'Administrator', 'password': "Welcome123"}

    input_config_json = json.load(input_config_file)

    # read the IP, username and password from the input json file
    host = input_config_json['Appliance']['IP']
    cred['userName'] = input_config_json['Appliance']['Username']
    cred['password'] = input_config_json['Appliance']['Password']

#     session = HPCIManager.login(host, cred)
    conn = hpOneView.connection(host)
    session = conn.login(cred, False)

    net = hpOneView.networking(conn)
    servers = hpOneView.servers(conn)

    enclosure_group_config = input_config_json["EnclosureGroup"]
    lig_name = enclosure_group_config['LogicalSwitchTemplate']

    logical_interconnect_group = net.get_lig_by_name(lig_name)

    egroup = hpOneView.common.make_egroup_dict(
                                    enclosure_group_config["Name"],
                                    logical_interconnect_group["uri"]
                                    )

    egroup1 = servers.create_enclosure_group(egroup)

    enclosure_config = input_config_json["Enclosure"]

    enclosure_dict = hpOneView.common.make_add_enclosure_dict(
                                    enclosure_config["Hostname"],
                                    enclosure_config["Username"],
                                    enclosure_config["Password"],
                                    egroup1["uri"]
                                    )

    servers.add_enclosure(enclosure_dict, blocking=True)


def Interconnects(json_file):
    print("Importing the enclosure")

    input_config_file = open(json_file, 'r')
    # Set appliance IP address and User login credentials
    host = "15.215.17.33"
    cred = {'userName': 'Administrator', 'password': "Welcome123"}

    input_config_json = json.load(input_config_file)

    # read the IP, username and password from the input json file
    host = input_config_json['Appliance']['IP']
    cred['userName'] = input_config_json['Appliance']['Username']
    cred['password'] = input_config_json['Appliance']['Password']

#     session = HPCIManager.login(host, cred)
    conn = hpOneView.connection(host)
    session = conn.login(cred, False)

    net = hpOneView.networking(conn)
    servers = hpOneView.servers(conn)

    logical_interconnects = net.get_lis()

    print(logical_interconnects)
    print(json.dumps(logical_interconnects))

###############################################################################
# Local script

print("Executing HP OneView Sample script!!!")
# C:\D-Drive\workspace\hpOneView_GitHub_govind\
config_file_path = "C:\D-Drive\Govind\GitHub\python-hpOneView\examples\Setup_With_JSON.json"

# Delete_EthernetNetworks(config_file_path)
# Delete_FCNetworks(config_file_path)

# Add_Networks(config_file_path)

# Create_LogicalLogicalInterconnectGroup(config_file_path)

Update_LogicalInterconnectGroup(config_file_path)
# Import_Enclosure(config_file_path)

Interconnects(config_file_path)
# Delete_LogicalSwitchTemplate(config_file_path)
