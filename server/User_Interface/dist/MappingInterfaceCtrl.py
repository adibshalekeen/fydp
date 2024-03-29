import csv
import os
import sys


class MappingInterfaceCtrl:
    def __init__(self, filename = "devices.csv"):
        self.filename = filename
        if not os.path.isfile(self.filename):
            with open(self.filename, 'w', newline='') as csvfile:
                filewriter = csv.writer(csvfile, delimiter=',',
                                        quoting=csv.QUOTE_MINIMAL)
                if "devices" in filename:
                    filewriter.writerow(["Friendly_Name", "Ip_Address", "Mac_Address"])
                elif "action" in filename:
                    filewriter.writerow(["Source_Name", "Source_Action", "Dest_Name", "Dest_Action"])

    # def add_entry(self, routing_entry):
    #     with open(self.filename, 'a', newline='') as csvfile:
    #         filewriter = csv.writer(csvfile, delimiter=',',
    #                                 quoting=csv.QUOTE_MINIMAL)
    #         filewriter.writerows(routing_entry)
    #
    # def modify_entry(self, new_ip_address, mac_address):
    #     file_contents = self.get_file_contents()
    #
    #     for mapping in file_contents:
    #         if mac_address in mapping[1]:
    #             mapping[0] = new_ip_address
    #         elif mac_address in mapping[3]:
    #             mapping[2] = new_ip_address
    #
    #     self.write_to_file(file_contents)
    #
    # def delete_entry(self, index):
    #     if index == 0:
    #         print("[Errror] - Cannot delete the header!\n")
    #         return 0
    #     file_contents = self.get_file_contents()
    #     file_contents.pop(int(index))
    #     self.write_to_file(file_contents)

    def get_mapped_address(self, ip_addr):
        contents = self.get_file_contents()
        if ip_addr:
            for mapping in contents:
                if mapping[1] == ip_addr:
                    return mapping[0] + "|" + ip_addr

    def get_mapped_actions(self, source_name, action = None):
        mapped_addresses = []
        contents = self.get_file_contents()
        if action:
            name, ip = source_name.split("|")
            # this reads the action mappings
            for mapping in contents:
                if name == mapping[0] or ip == mapping[0]:
                    if action == mapping[1]:
                        msg = mapping[2] + "|" + mapping[3]
                        mapped_addresses.append(msg)
        else:
            dest_name = source_name
            # this finds what output signals to send
            # source_name is dest_name here
            for mapping in contents:
                for dest in dest_name:
                    old_name, action = dest.split("|")
                    if old_name in mapping and not old_name == '.' :
                        if(mapping[1] == "BLUETOOTH"):
                            map = mapping[0] + "|" + "BLUETOOTH" + "|" + mapping[2] + "|" + action
                        elif(mapping[1] == "ZIGBEE"):
                            map = mapping[2] + "|" + "ZIGBEE" + "|" + action
                        else:
                            map = mapping[1] + "|" + action
                        mapped_addresses.append(map)
        return mapped_addresses

    def get_file_contents(self):
        file_contents = []
        with open(self.filename, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            for line in reader:
                file_contents.append(line)
        return file_contents

    def write_to_file(self, file_contents):
        with open(self.filename, 'w', newline='') as csvfile:
            filewriter = csv.writer(csvfile, delimiter=',',
                                    quoting=csv.QUOTE_MINIMAL)
            filewriter.writerows(file_contents)

def main():
    if( len(sys.argv) != 1):
        # The node server may confuse its server.js path with this module so we specify
        function_code = sys.argv[1]
        fileName = "./dist/devices.csv" if ("map" in sys.argv[2]) else "./dist/action.csv"
        mapCont = MappingInterfaceCtrl(fileName)

        if function_code == 'save_mappings':
            # Save the mapping data to file
            contents = sys.argv[3]
            rows = contents.split('|')
            rows.pop()

            if "devices" in fileName:
                item = [["Friendly_Name", "Ip_Address", "Mac_Address"]]
                for row in rows:
                    name, ip, mac = row.split(',')
                    item.append([name, ip, mac])

                    mapCont.write_to_file(item)
            elif "action" in fileName:
                item = [["Source_Name", "Source_Action", "Dest_Name", "Dest_Action"]]
                for row in rows:
                    s_name, s_act, d_name, d_act = row.split(',')
                    item.append([s_name, s_act, d_name, d_act])

                    mapCont.write_to_file(item)
        elif function_code == 'get_mappings':
            mappings = mapCont.get_file_contents()

            # We want to remove the headers so we dont accidentally display it on the web
            mappings.pop(0)

            for line in mappings:
                for item in line:
                    print(item)
        elif function_code == 'send_message':
            mapDevices = MappingInterfaceCtrl("./dist/devices.csv")
            # We defaulted to create the mapping reader, must make an action reader here
            contents = sys.argv[3]
            s_ip, s_gest, s_action = contents.split("|")
            s_act = s_gest.upper() + "-" + s_action.upper()
            s_name = mapDevices.get_mapped_address(s_ip)
            if(s_name):
                dest_addrs = mapCont.get_mapped_actions(s_name, s_act)
                if(dest_addrs):
                    resp = mapDevices.get_mapped_actions(dest_addrs)
                    for line in resp:
                        print(line)

main()
