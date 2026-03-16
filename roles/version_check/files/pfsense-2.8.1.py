import requests
from bs4 import BeautifulSoup
import urllib3
import argparse
import sys
import time

session = requests.session()
session.timeout = 20
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


parser = argparse.ArgumentParser()
parser.add_argument("--host", required=True, help="pfSense host IP")
parser.add_argument("--port", required=True, help="pfSense host Port")
parser.add_argument("--user", required=True, help="pfSense host Username")
parser.add_argument("--passw", required=True,help="pfSense host Password")
args = parser.parse_args()

ip = args.host
port = args.port
user = args.user
passw = args.passw

ip = ip +":"+port


#LOGIN PFSENSE

r1 = session.get(f"https://{ip}/index.php",verify=False,timeout=session.timeout)

r1_soup = BeautifulSoup(r1.text, "html.parser")

r1_csrf_token = r1_soup.find("input", {"name":"__csrf_magic"})["value"]

headers = {
'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:99.0) Gecko/20100101 Firefox/99.0',
'Content-Type': 'application/x-www-form-urlencoded'

}

data = {
'__csrf_magic': r1_csrf_token,
'usernamefld': user,
'passwordfld': passw,
'login':'Sign+In'

}
login_req = session.post(f"https://{ip}/index.php",data=data,headers=headers,verify=False,timeout=session.timeout)


## UPDATE BRANCH TO 2.8.1

r2 = session.get(f"https://{ip}/pkg_mgr_install.php?id=firmware",verify=False,timeout=session.timeout)

r2.raise_for_status()

r2_soup = BeautifulSoup(r2.text,"html.parser")


r2_csrf_token = r2_soup.find("input", {"name":"__csrf_magic"})["value"]

branch_data = {
    '__csrf_magic': r2_csrf_token,
    'mode':'',
    'fwbranch':'2_8_1',
    'id':'firmware',
    'confirmed':'false',
    'refrbranch':'true'
}

branch_req = session.post(f"https://{ip}/pkg_mgr_install.php",data=branch_data,verify=False,timeout=session.timeout)
branch_req.raise_for_status()

print("Status Code:",branch_req.status_code)

time.sleep(20)

