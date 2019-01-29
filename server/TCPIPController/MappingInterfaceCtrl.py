import csv
import os

class MappingInterfaceCtrl:
    def __init__(self, filename = "routing.csv"):
        self.filename = filename
        if not os.path.isfile(self.filename):
            with open(self.filename, 'w', newline='') as csvfile:
                filewriter = csv.writer(csvfile, delimiter=',',
                                        quoting=csv.QUOTE_MINIMAL)
                filewriter.writerow(["Source_Ip_Address", "Source_Mac_Address",
                                    "Dest_Ip_Address", "Dest_Mac_Address"])

    def add_entry(self, routing_entry):
        with open(self.filename, 'a', newline='') as csvfile:
            filewriter = csv.writer(csvfile, delimiter=',',
                                    quoting=csv.QUOTE_MINIMAL)
            filewriter.writerows(routing_entry)

    def modify_entry(self, new_ip_address, mac_address):
        file_contents = self.get_file_contents()

        for mapping in file_contents:
            if mac_address in mapping[1]:
                mapping[0] = new_ip_address
            elif mac_address in mapping[3]:
                mapping[2] = new_ip_address

        self.__write_to_file(file_contents)

    def delete_entry(self, index):
        if index == 0:
            print("[Errror] - Cannot delete the header!\n")
            return 0
        file_contents = self.get_file_contents()
        file_contents.pop(int(index))
        self.__write_to_file(file_contents)

    def get_mapped_addresses(self, source_ip):
        mapped_addresses = []
        contents = self.get_file_contents()
        for mapping in contents:
            if source_ip in mapping:
                mapped_addresses.append(mapping[2])
        return mapped_addresses

    def get_file_contents(self):
        file_contents = []
        with open(self.filename, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            for line in reader:
                file_contents.append(line)
        return file_contents

    # Private functions
    def __write_to_file(self, file_contents):
        with open(self.filename, 'w', newline='') as csvfile:
            filewriter = csv.writer(csvfile, delimiter=',',
                                    quoting=csv.QUOTE_MINIMAL)
            filewriter.writerows(file_contents)
