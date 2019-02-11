import csv
import os
import sys


class MappingInterfaceCtrl:
    def __init__(self, filename = "routing.csv"):
        self.filename = filename
        if not os.path.isfile(self.filename):
            with open(self.filename, 'w', newline='') as csvfile:
                filewriter = csv.writer(csvfile, delimiter=',',
                                        quoting=csv.QUOTE_MINIMAL)
                if "routing" in filename:
                    filewriter.writerow(["Source_Ip_Address", "Source_Mac_Address",
                    "Dest_Ip_Address", "Dest_Mac_Address"])
                elif "action" in filename:
                    filewriter.writerow(["Source_Ip_Address", "Source_Action",
                    "Dest_Ip_Address", "Dest_Action"])

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

    # Can optimize this to use following command to check last edit time for file
    # file_epoch_time = os.path.getmtime(file)
    # time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(file_epoch_time))
    # def get_mapped_addresses(self, source_ip):
    #     mapped_addresses = []
    #     contents = self.get_file_contents()
    #     for mapping in contents:
    #         if source_ip in mapping:
    #             mapped_addresses.append(mapping[2])
    #     return mapped_addresses

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
        fileName = "./dist/routing.csv" if ("map" in sys.argv[2]) else "./dist/action.csv"
        mapCont = MappingInterfaceCtrl(fileName)

        if function_code == 'save_mappings':
            # Save the mapping data to file
            contents = sys.argv[3]
            rows = contents.split('|')
            rows.pop()
            item = [["Source_Ip_Address", "Source_Mac_Address", "Dest_Ip_Address", "Dest_Mac_Address"]]

            for row in rows:
                s_ip, s_mac, d_ip, d_mac = row.split(',')
                item.append([s_ip, s_mac, d_ip, d_mac])

            mappings = mapCont.write_to_file(item)
        elif function_code == 'get_mappings':
            mappings = mapCont.get_file_contents()

            # We want to remove the headers so we dont accidentally display it on the web
            mappings.pop(0)

            for line in mappings:
                for item in line:
                    print(item)
main()
