import requests
from bs4 import BeautifulSoup
import urllib3
import argparse
import sys

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

OUTPUT_FILE = f"./pfsense_backups/{ip}_config_backup.xml"

ip = ip +":"+port



#LOGIN PFSENSE

html = session.get(f"https://{ip}/index.php",verify=False,timeout=session.timeout)

soup = BeautifulSoup(html.text, "html.parser")

csrf_token = soup.find("input", {"name":"__csrf_magic"})["value"]

headers = {
'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:99.0) Gecko/20100101 Firefox/99.0',
'Content-Type': 'application/x-www-form-urlencoded'

}

data = {
'__csrf_magic': csrf_token,
'usernamefld': user,
'passwordfld': passw,
'login':'Sign+In'

}
login_req = session.post(f"https://{ip}/index.php",data=data,headers=headers,verify=False,timeout=session.timeout)

#SAVE BACKUP CONFIG

url = f"https://{ip}/diag_backup.php"

b1 = session.get(url, verify=False,timeout=session.timeout)
b1.raise_for_status()

b1_soup = BeautifulSoup(b1.text, "html.parser")

b1_csrf_token = b1_soup.find("input", {"name": "__csrf_magic"})["value"]


form_data = {
    "__csrf_magic":          b1_csrf_token,
    "backuparea":            "",                   # all areas = empty
    "donotbackuprrd":        "yes",                # skip RRD graphs → smaller file
    "backupdata":            "yes",                # include data (certificates, etc.)
    "encrypt_password":      "",                   # leave empty = no encryption
    "encrypt_password_confirm": "",
    "download":              "Download configuration as XML",
    "restorearea":           "",                   # not used here
    "conffile":              ("", b"", "application/octet-stream"),  # empty file field
    "decrypt_password":      "",
}


r_download = session.post(
    f"https://{ip}/diag_backup.php",
    data=form_data,               # requests will turn this into multipart
    timeout=session.timeout,
    verify=False,
)

# Step 5: Save the response
if r_download.status_code == 200 and "xml" in r_download.text and len(r_download.content) > 100:
    with open(OUTPUT_FILE, "wb") as f:
        f.write(r_download.content)
    print(f"Success! Config saved to: {OUTPUT_FILE}")
    print(f"Size: {len(r_download.content):,} bytes")
else:
    print(f"Download failed – status: {r_download.status_code}")
    print(r_download.text)
    sys.exit(1)   # first part of error page

#SSH DATA

url = f"https://{ip}/system_advanced_admin.php"
    
    
r = session.get(url, verify=False,timeout=session.timeout)
r.raise_for_status()
soup = BeautifulSoup(r.text, "html.parser")

    
csrf_token = soup.find("input", {"name": "__csrf_magic"})["value"]


ssh_checkbox = soup.find("input", {"name": "enablesshd"})
if ssh_checkbox.get("checked") == "checked":
        print("[+] SSH ALREADY ENABLED.")
        sys.exit(0)
    
def val(name):
    el = soup.find(attrs={"name": name})
    if el is None:
        return ""
    if el.name == "input":
        if el.get("type") in ["checkbox", "radio"]:
            return "yes" if el.get("checked") == "checked" else ""
        return el.get("value", "")
    if el.name == "select":
        selected = el.find("option", selected=True)
        return selected["value"] if selected else ""
    return ""

    
current_config = {
        '__csrf_magic': csrf_token,
        'webguiproto': 'https',           # http or https
        'ssl-certref': val("ssl-certref"),           # certificate ref
        'webguiport': val("webguiport") or "",       # custom port or empty = default
        'max_procs': val("max_procs") or "2",
        'webgui-redirect': val("webgui-redirect"),
        'webgui-hsts': val("webgui-hsts"),
        'ocsp-staple': val("ocsp-staple"),
        'loginautocomplete': val("loginautocomplete"),
        'webgui-login-messages': val("webgui-login-messages"),
        'noantilockout': val("noantilockout"),
        'nodnsrebindcheck': val("nodnsrebindcheck"),
        'althostnames': val("althostnames") or "",
        'nohttpreferercheck': val("nohttpreferercheck"),
        'pagenamefirst': val("pagenamefirst"),
        'enablesshd': "yes",
        'sshdkeyonly': val("sshdkeyonly"),          
        'sshdagentforwarding': val("sshdagentforwarding"),
        'sshport': val("sshport") or "",
        'sshguard_threshold': val("sshguard_threshold") or "",
        'sshguard_blocktime': val("sshguard_blocktime") or "",
        'sshguard_detection_time': val("sshguard_detection_time") or "",
        'enableserial': val("enableserial"),
        'serialspeed': val("serialspeed"),
        'primaryconsole': val("primaryconsole"),
        'disableconsolemenu': val("disableconsolemenu"),
        'save': 'Save'
}

#SEND SSH DATA REQUEST
ssh_req = session.post(f"https://{ip}/system_advanced_admin.php",data=current_config,verify=False,timeout=session.timeout)


url = f"https://{ip}/system_advanced_admin.php"
    
    
check_req = session.get(url, verify=False,timeout=session.timeout)
check_req.raise_for_status()
check_soup = BeautifulSoup(check_req.text, "html.parser")

ssh_checkbox = check_soup.find("input", {"name": "enablesshd"})
if ssh_checkbox.get("checked") == "checked":
        print("[+] SSH IS ENABLED.")
else:
     print("[!] Something went wrong.")