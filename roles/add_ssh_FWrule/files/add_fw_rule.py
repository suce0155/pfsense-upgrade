import requests
from bs4 import BeautifulSoup
import urllib3
import argparse
import sys
import re
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
'passwordfld':passw,
'login':'Sign+In'

}
login_req = session.post(f"https://{ip}/index.php",data=data,headers=headers,verify=False,timeout=session.timeout)




#CHECK IF ALREADY EXISTS
check_allias = session.get(f"https://{ip}/firewall_rules.php",verify=False,timeout=session.timeout)

check_allias.raise_for_status()

check_allias_soup = BeautifulSoup(check_allias.text,"html.parser")


alias_names = [
    td.get_text(strip=True).lower()
    for td in check_allias_soup.select("table tbody tr td:first-child")
]

if ("eclit_terminals".lower() in alias_names):
    print("[+] ALIAS is ADDED.")
else:
    print("[!] Something went wrong with Alias")


check_fw = session.get(f"https://{ip}/firewall_aliases.php",verify=False,timeout=session.timeout)

check_fw.raise_for_status()

check_fw_soup = BeautifulSoup(check_fw.text, "html.parser")
pattern = re.compile(r"\ballow_ssh\b", re.IGNORECASE)



# Look for tags that appear to represent firewall blocks
firewalls = check_fw_soup.find_all(class_=re.compile(r"firewall", re.IGNORECASE))

for fw in firewalls:
    # Look for a child element that contains a description
    desc = fw.find(class_=re.compile(r"desc", re.IGNORECASE))
    if desc and pattern.search(desc.get_text(strip=True)):
        print("[+] FW RULE is ADDED.")
        break
    else:
        print("[!] Something went wrong with FW RULE")





## CREATE ALIAS

r2 = session.get(f"https://{ip}/firewall_aliases_edit.php?tab=ip",verify=False,timeout=session.timeout)

r2.raise_for_status()

r2_soup = BeautifulSoup(r2.text,"html.parser")

r2_csrf_token = r2_soup.find("input", {"name":"__csrf_magic"})["value"]

alias_data = {
    '__csrf_magic': r2_csrf_token,
    'name':'eclit_terminals',
    'descr':'',
    'type':'host',
    'address0':'1.2.3.4',
    'detail0':'',
    'address1':'5.6.7.8',
    'detail1':'',
    'tab':'ip',
    'origname':'',
    'save':'Save',
    'apply':'Apply+Changes'
}

alias_req = session.post(f"https://{ip}/firewall_aliases_edit.php?tab=ip",data=alias_data,verify=False,timeout=session.timeout)
alias_req.raise_for_status()

#APPLY ALIAS

alias_apply = session.post(f"https://{ip}/firewall_aliases.php",data={'__csrf_magic': r2_csrf_token,'apply':'Apply Changes'},verify=False,timeout=session.timeout)
alias_apply.raise_for_status()


## ADD SSH FW RULE

r3 = session.get(f"https://{ip}/firewall_rules_edit.php?if=wan",verify=False,timeout=session.timeout)

r3.raise_for_status()

r3_soup = BeautifulSoup(r3.text,"html.parser")

r3_csrf_token = r3_soup.find("input", {"name":"__csrf_magic"})["value"]

rules_data = {
    '__csrf_magic': r3_csrf_token,
    'type': 'pass',
    'interface': 'wan',
    'ipprotocol': 'inet',
    'proto': 'tcp',
    'icmptype[]': 'any',
    'srctype': 'single',
    'src': 'eclit_terminals',
    'srcbeginport': '',
    'srcendport': '',
    'dsttype': '(self)',
    'dst': '',
    'dstbeginport': '',
    'dstendport': '',
    'dstbeginport_cust': '22',
    'dstendport_cust': '22',
    'descr': 'allow_ssh_pf_upgrade',
    'os': '',
    'dscp': '',
    'tag': '',
    'tagged': '',
    'max': '',
    'max-src-nodes': '',
    'max-src-conn': '',
    'max-src-states': '',
    'max-src-conn-rate': '',
    'max-src-conn-rates': '',
    'statetimeout': '',
    'statetype': 'keep state',
    'vlanprio': '',
    'vlanprioset': '',
    'sched': '',
    'gateway': '',
    'dnpipe': '',
    'pdnpipe': '',
    'ackqueue': '',
    'defaultqueue': '',
    'after': '',
    'ruleid': '',
    'save': 'Save',
    'apply':'Apply+Changes'
}

rules_req = session.post(f"https://{ip}/firewall_rules_edit.php?if=wan",data=rules_data,verify=False,timeout=session.timeout)
rules_req.raise_for_status()

#APPLY FIREWALL

firewall_apply = session.post(f"https://{ip}/firewall_rules.php",data={'__csrf_magic': r2_csrf_token,'apply':'Apply Changes'},verify=False,timeout=session.timeout)
firewall_apply.raise_for_status()

time.sleep(5)

#CHECK IF ALIAS EXISTS
check_allias = session.get(f"https://{ip}/firewall_rules.php",verify=False,timeout=session.timeout)

check_allias.raise_for_status()

check_allias_soup = BeautifulSoup(check_allias.text,"html.parser")


alias_names = [
    td.get_text(strip=True).lower()
    for td in check_allias_soup.select("table tbody tr td:first-child")
]

if ("eclit_terminals".lower() in alias_names):
    print("[+] ALIAS is ADDED.")
else:
    print("[!] Something went wrong with Alias")

# CHECK IF FIREWALL EXISTS
check_fw = session.get(f"https://{ip}/firewall_aliases.php",verify=False,timeout=session.timeout)

check_fw.raise_for_status()

check_fw_soup = BeautifulSoup(check_fw.text, "html.parser")
pattern = re.compile(r"\ballow_ssh\b", re.IGNORECASE)



# Look for tags that appear to represent firewall blocks
firewalls = check_fw_soup.find_all(class_=re.compile(r"firewall", re.IGNORECASE))

for fw in firewalls:
    # Look for a child element that contains a description
    desc = fw.find(class_=re.compile(r"desc", re.IGNORECASE))
    if desc and pattern.search(desc.get_text(strip=True)):
        print("[+] FW RULE is ADDED.")
        break
    else:
        print("[!] Something went wrong with FW RULE")

