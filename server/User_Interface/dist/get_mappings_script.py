import MappingInterfaceCtrl as mapIfaceCtrl

# The node server may confuse its server.js path with this module so we specify
mapCont = mapIfaceCtrl.MappingInterfaceCtrl("./dist/routing.csv")
mappings = mapCont.get_file_contents()

# We want to remove the headers so we dont accidentally display it on the web
mappings.pop(0)

for line in mappings:
    for item in line:
        print(item)
