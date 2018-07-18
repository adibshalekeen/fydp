import sys
from gesture_httpservice import http_service

print(sys.argv)
ip = sys.argv[1]

http = http_service(ip)
http.get('//r//OldSchoolCool//')
print(http.response.read().decode())