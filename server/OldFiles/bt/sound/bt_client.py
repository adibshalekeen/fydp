import pdb
import bt_ctl as bt

s = bt.Bluetoothctl()
s.get_output("disconnect")
s.get_output("connect 00:0C:8A:FE:85:72", 2)

pdb.set_trace()
