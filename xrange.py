from ipaddress import IPv4Network, IPv4Address
import getopt
import sys
import json

if __name__ == "__main__":

    opts, args = getopt.getopt(sys.argv[1:], "n:s:e:o:", ["net=", "start=", "end=", "output="])

    my_network = None
    my_start = None
    my_end = None
    my_output = None
    my_addresses = []

    for opt, arg in opts:
        if opt == "-n":
            my_network = IPv4Network(arg)
        elif opt == "-s":
            my_start = IPv4Address(arg)
        elif opt == "-e":
            my_end = IPv4Address(arg)
        elif opt == "-o":
            my_output = arg
        else:
            print("Unhandled option %s" % opt, file=sys.stderr)
            exit(1)

    print("Network: %s" % my_network)
    print("Start: %s" % my_start)
    print("End: %s" % my_end)
    print("Output: %s" % my_output)

    for address in my_network.hosts():
        if my_start <= address <= my_end:
            str_address = str(address)
            my_addresses.append(str_address)

    with open(my_output, "w") as out:
        data = { 'addresses': my_addresses }
        json.dump(data, out, indent=4)

