import CSVController as csvCtrl

cont = csvCtrl.CSV_Controller()

cont.add_entry([["192.168.128.1", "AA:55:AA:55:AA:55", "192.168.128.2", "BB:66:BB:66:BB:66"]])

cont.modify_entry("192.168.128.7", "AA:55:AA:55:AA:55")
cont.modify_entry("192.168.128.53", "BB:66:BB:66:BB:66")