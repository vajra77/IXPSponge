from ipaddress import IPv4Network, IPv4Address
import getopt
import sys
import json
import requests

if __name__ == "__main__":

    opts, args = getopt.getopt(sys.argv[1:], "a:x:o:", ["api=", "ixp=", "output="])

    my_api = None
    my_ixp = None
    my_output = None
    my_addresses = []

    for opt, arg in opts:
        if opt == "-a":
            my_api = arg
        elif opt == "-x":
            my_ixp = arg
        elif opt == "-o":
            my_output = arg
        else:
            print("Unhandled option %s" % opt, file=sys.stderr)

    response = requests.get(my_api)
    data = response.json()

    members = data["member_list"]
    for member in members:
        connections = member["connection_list"]
        for connection in connections:
            if connection["ixp_id"] == int(my_ixp):
                vlans = connection["vlan_list"]
                for vlan in vlans:
                    my_addresses.append(vlan["ipv4"]["address"])

    with open(my_output, "w") as out:
        data = { 'addresses': my_addresses }
        json.dump(data, out, indent=4)

