import os, time
 
# function to establish a new connection
def createNewConnection(name, SSID, password, iface):
    config = """<?xml version=\"1.0\"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>"""+name+"""</name>
    <SSIDConfig>
        <SSID>
            <name>"""+SSID+"""</name>
        </SSID>
    </SSIDConfig>
    <connectionType>ESS</connectionType>
    <connectionMode>auto</connectionMode>
    <MSM>
        <security>
            <authEncryption>
                <authentication>WPA2PSK</authentication>
                <encryption>AES</encryption>
                <useOneX>false</useOneX>
            </authEncryption>
            <sharedKey>
                <keyType>passPhrase</keyType>
                <protected>false</protected>
                <keyMaterial>"""+password+"""</keyMaterial>
            </sharedKey>
        </security>
    </MSM>
</WLANProfile>"""
    command = '''netsh wlan add profile filename="{}.xml"  interface="{}"'''.format(name, iface)
    with open(name+".xml", 'w') as file:
        file.write(config)
    os.system(command)
 
def disconnect(iface):
    os.popen('''netsh wlan disconnect interface="{}"'''.format(iface)).read()

# function to connect to a network   
def connect(name, SSID, iface):
    time.sleep(2)
    command = '''netsh wlan connect name="{}" ssid="{}" interface="{}"'''.format(name,SSID,iface)    
    a = os.popen(command).read()
    time.sleep(3)
    return a

# function to display avavilabe Wifi networks   
# def displayAvailableNetworks():
#     command = "netsh wlan show networks interface=Wi-Fi"
#     os.system(command)
 
def displayAvailableIface():
    command = "netsh wlan show interfaces"
    a = os.popen(command).read()
    return [i for i in a.splitlines() if ' :' in i][0].split(': ')[-1]
 
# display available netwroks
# displayAvailableNetworks()
 
# input wifi name and password
# name = input("Name of Wi-Fi: ")
# password = input("Password: ")
 
# establish new connection
# createNewConnection(name, name, password)
 
# connect to the wifi network
# connect(name, name)
# print("If you aren't connected to this network, try connecting with the correct password!")