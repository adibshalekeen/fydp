import sys
import MappingInterfaceCtrl as mapIfaceCtrl

if( len(sys.argv) != 1):
    # The node server may confuse its server.js path with this module so we specify
    mapCont = mapIfaceCtrl.MappingInterfaceCtrl("./dist/routing.csv")
    function_code = sys.argv[1]

    if function_code == '1':
        # Save the mapping data to file
        contents = sys.argv[2]
        rows = contents.split('|')
        rows.pop()
        item = []

        for row in rows:
            s_ip, s_mac, d_ip, d_mac = row.split(',')
            item.append([s_ip, s_mac, d_ip, d_mac])

        mappings = mapCont.write_to_file(item)
    elif function_code == '2':
        mappings = mapCont.get_file_contents()

        # We want to remove the headers so we dont accidentally display it on the web
        mappings.pop(0)

        for line in mappings:
            for item in line:
                print(item)
