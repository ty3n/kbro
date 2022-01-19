from term_3 import *
import os
import time, traceback, subprocess
from WLAN import *
from netifaces import interfaces, ifaddresses, AF_INET

backup_sys_stdout = sys.stdout

def getips():
    a = []
    r = os.popen('ipconfig').read()
    for i,c in enumerate(r.splitlines()):
        if 'IPv4' in c:
            if 'hitronhub.home' in r.splitlines()[i-1] or 'hitronhub.home' in r.splitlines()[i-2]:
                a.append(c.split(': ')[-1])
    return a

def gatewayip():
    a = []
    r = os.popen('ipconfig').read()
    for i,c in enumerate(r.splitlines()):
        if '預設閘道' in c or 'Gateway' in c:
            if 'hitronhub.home' in r.splitlines()[i-2] or 'hitronhub.home' in r.splitlines()[i-3]:
                return c.split(': ')[-1]
    raise Exception('Get GetwayIP FAIL')

def getLanIface():
    a = []
    r = os.popen('ipconfig').read()
    for i,c in enumerate(r.splitlines()):
        if 'IPv4' in c:
            if 'hitronhub.home' in r.splitlines()[i-1] or 'hitronhub.home' in r.splitlines()[i-2]:
                if 'Ethernet adapter'in r.splitlines()[i-3]:
                    return r.splitlines()[i-3].split('Ethernet adapter ')[-1][:-1]
                elif 'Ethernet adapter'in r.splitlines()[i-4]:
                    return r.splitlines()[i-4].split('Ethernet adapter ')[-1][:-1]
                elif '乙太網路卡' in r.splitlines()[i-3]:
                    return r.splitlines()[i-3].split('乙太網路卡 ')[-1][:-1]
                elif '乙太網路卡' in r.splitlines()[i-4]:
                    return r.splitlines()[i-4].split('乙太網路卡 ')[-1][:-1]
    raise Exception("GET LAN INTERFACE FAIL")

# loss = fping('192.168.0.1',1024,20,1000)
def fping(ip,length,count,interval):
    result = os.popen("Fping %s -s %d -t %d -n %d"%(ip,length,interval,count)).read()
    # return float(result[result.rfind("(")+1:result.rfind("%")])
    return result

def ploss(src,dst):
    return os.popen("ping %s -S %s -n 20"%(dst,src)).read()

class RedirectStdout(object):
    def __init__(self,fileobj=None):
        if not fileobj:
            self.fileobj = open(DEFAULT_LOG_FILE,"a",encoding='UTF-8')
            sys.stdout = self
        elif type(fileobj) == type(sys.stdout):
            self.fileobj = fileobj
            sys.stdout = self
    def write(self,s):
        backup_sys_stdout.write(s)
        self.fileobj.write(s)
    def close(self):
        if not self.fileobj.closed:
            sys.stdout = backup_sys_stdout
            self.fileobj.close()
    def __del__(self):
        self.close()

def lLogin(dstip,username,password):
    #term.host -- dst ip
    #term.port -- dst port
    print('Telnet login Start')
    for k in range(5):
        if isPortConnect(dstip,23):
           print('Waiting telnet.....')
           break
        else:
           time.sleep(1)
           if k==4:raise Exception('No connection')
    term = Telnet(dstip)
    data = term.wait("login:",15)[-1]
    term << username
    time.sleep(1)
    term << password
    time.sleep(1)
    data=term.wait('~#',15)[-1]
    print('[%s]%s'%(time.ctime(),data))
    if '~#' in data:
        return term
    raise Exception('Telnet login Failure')

def main():
    logdir = os.path.join(os.getcwd(),"5310-log\\")
    if not os.path.isdir(logdir):
        os.system("mkdir %s"%logdir)
    iface = displayAvailableIface()
    disconnect(iface)
    gateway = gatewayip()
    time.sleep(2)
    term=lLogin(gateway,'cusadmin','password')
    a = lWaitCmdTerm(term,'''ncpu_exec -ep "cli docsis/vendor"''','~#',5)
    mac = [i for i in a.splitlines() if 'RF MAC' in i][0].split(' ')[-1].replace(':','-')
    sn = [i for i in a.splitlines() if 'Serial Number' in i][0].split(' ')[-1].replace(':','-')
    fname = logdir + mac + '.5310-' + time.strftime("%Y%m%d%H%M%S", time.localtime())
    d = lWaitCmdTerm(term,"iw dev",'~#',5)
    for i,c in enumerate(d.splitlines()):
        if 'wlan2.0' in c: 
            ssid2g = d.splitlines()[i+4].split(' ')[-1]
        if 'wlan0.0' in c: 
            ssid5g = d.splitlines()[i+4].split(' ')[-1]
    try:
        log = RedirectStdout(open(fname,"w",encoding='UTF-8'))
        time.sleep(3)
        print(mac, time.ctime())
        print("/* DOCSIS information */")
        print(lWaitCmdTerm(term,'''ncpu_exec -ep "killall cli"''','~#',8))
        print(lWaitCmdTerm(term,'''ncpu_exec -ep "ifconfig"''','~#',8))
        print(lWaitCmdTerm(term,'''ncpu_exec -ep "cat ./proc/uptime"''','~#',8))
        print(lWaitCmdTerm(term,'''ncpu_exec -ep "cli docsis/vendor"''','~#',8))
        print(lWaitCmdTerm(term,'''ncpu_exec -ep "cli docsis/cm"''','~#',8))
        print(lWaitCmdTerm(term,'''ncpu_exec -ep "cli docsis/Debug/uss"''','~#',8))
        print(lWaitCmdTerm(term,'''ncpu_exec -ep "cli docsis/Debug/dss"''','~#',8))
        print(lWaitCmdTerm(term,'''ncpu_exec -ep "route -n"''','~#',8))
        print(lWaitCmdTerm(term,'''ncpu_exec -ep "arp -n"''','~#',8))
        print(lWaitCmdTerm(term,'''ncpu_exec -ep "top -n 1"''','~#',8))
        print(lWaitCmdTerm(term,'''ncpu_exec -ep "top -b -n 1 -m"''','~#',8))
        print(lWaitCmdTerm(term,'''ncpu_exec -ep "dmesg"''','~#',8))
        print(lWaitCmdTerm(term,'''ncpu_exec -ep "iccctl process_tag"''','~#',8))
        print(lWaitCmdTerm(term,'''ncpu_exec -ep "iccctl dest"''','~#',8))
        print(lWaitCmdTerm(term,'''ncpu_exec -ep "cli docsis/Fw/ds_phy/debug/L"''','~#',8))
        print(lWaitCmdTerm(term,'''ncpu_exec -ep "cli docsis/General/hwcounters"''','~#',8))
        print(lWaitCmdTerm(term,'''dmcli eRT getv Device.X_CISCO_COM_CableModem.DocsisLog.''','~#',8))
        print(lWaitCmdTerm(term,'''ncpu_exec -ep "cat /nvram/kbro_debug"''','~#',8))
        print(lWaitCmdTerm(term,'''ncpu_exec -ep "cat /dev/shm/kbro_debug"''','~#',8))
        print(lWaitCmdTerm(term,'''ncpu_exec -ep "cli docsis/reinitMacInfo"''','~#',8))
        print(lWaitCmdTerm(term,'''ncpu_exec -ep "cli docsis/cm"''','~#',8))
        print(lWaitCmdTerm(term,'''ncpu_exec -ep "cli docsis/configfile"''','~#',8))
        print(lWaitCmdTerm(term,'''ncpu_exec -ep "ps"''','~#',8))
        print(lWaitCmdTerm(term,'''ncpu_exec -ep "cat /proc/net/dbrctl/alt"''','~#',8))
        print(lWaitCmdTerm(term,'''ncpu_exec -ep "cat /tmp/htcdm_ipv4"''','~#',8))
        print(lWaitCmdTerm(term,'''ncpu_exec -ep "cat /var/tmp/ht_cdmHostList"''','~#',8))
        print("/* ATOM system informatioin */")
        print(lWaitCmdTerm(term,'''cli system/network''','~#',8))
        print(lWaitCmdTerm(term,'''cli system/ipPrint''','~#',8))
        print(lWaitCmdTerm(term,'''cli system/memory''','~#',8))
        print(lWaitCmdTerm(term,'''uptime''','~#',8))
        print(lWaitCmdTerm(term,'''cat /sys/class/thermal/thermal_zone0/temp''','~#',8))
        print(lWaitCmdTerm(term,'''iw dev wlan0 iwlwav gTemperature''','~#',8))
        print(lWaitCmdTerm(term,'''iw dev wlan2 iwlwav gTemperature''','~#',8))
        print(lWaitCmdTerm(term,'''ps''','~#',8))
        print(lWaitCmdTerm(term,'''dmesg''','~#',8))
        print(lWaitCmdTerm(term,'''free''','~#',8))
        print("/* Check RG status*/")
        print(lWaitCmdTerm(term,'''cat /nvram/bbhm_cur_cfg.xml''','~#',8))
        print(lWaitCmdTerm(term,'''syscfg show''','~#',8))
        print(lWaitCmdTerm(term,'''iptables -nvL''','~#',8))
        print(lWaitCmdTerm(term,'''iptables -nvL -t nat''','~#',8))
        print(lWaitCmdTerm(term,'''iptables -nvL -t mangle''','~#',8))
        print(lWaitCmdTerm(term,'''systemctl status gwprovapp.service''','~#',8))
        print(lWaitCmdTerm(term,'''systemctl status CcspHitronCdm.service''','~#',8))
        print(lWaitCmdTerm(term,'''route -n''','~#',8))
        print(lWaitCmdTerm(term,'''arp -n''','~#',8))
        print(lWaitCmdTerm(term,'''cat /nvram/dnsmasq.leases''','~#',8))
        print(lWaitCmdTerm(term,'''cat /nvram/web_accesslog.txt''','~#',8))
        print("/* Check WiFi status */")
        print(lWaitCmdTerm(term,'''iw dev''','~#',8))
        print(lWaitCmdTerm(term,'''uci show''','~#',8))
        phy5g =lWaitCmdTerm(term,'''cat /var/run/hostapd-phy0.conf''','~#',8)
        pwd5g = [i for i in phy5g.splitlines() if 'wpa_passphrase' in i][0].split('=')[-1]
        print(phy5g)
        phy2g = lWaitCmdTerm(term,'''cat /var/run/hostapd-phy1.conf''','~#',8)
        pwd2g = [i for i in phy2g.splitlines() if 'wpa_passphrase' in i][0].split('=')[-1]
        print(phy2g)
        print(lWaitCmdTerm(term,'''cat /var/run/acs_history_wlan0.txt''','~#',8))
        print(lWaitCmdTerm(term,'''cat /var/run/acs_history_wlan2.txt''','~#',8))
        print(lWaitCmdTerm(term,'''cat /var/run/acs_smart_info_wlan0.txt''','~#',8))
        print(lWaitCmdTerm(term,'''cat /var/run/acs_smart_info_wlan2.txt''','~#',8))
        print(lWaitCmdTerm(term,'''lspci -k''','~#',8))
        print(lWaitCmdTerm(term,'''ls /sys/class/ieee80211/''','~#',8))
        print(lWaitCmdTerm(term,'''dwpal_cli wlan0.0 PeerList''','~#',8))
        print(lWaitCmdTerm(term,'''dwpal_cli wlan2.0 PeerList''','~#',8))
        print(lWaitCmdTerm(term,'''cat /nvram/wifilog_event.txt''','~#',8))
        print(lWaitCmdTerm(term,'''systemctl status systemd-netifd.service''','~#',8))
        print(lWaitCmdTerm(term,'''systemctl status systemd-wlan-restart.timer''','~#',8))
        print(lWaitCmdTerm(term,'''systemctl status ccspwifiagent.service''','~#',8))
        print(lWaitCmdTerm(term,'''systemctl status systemd-wave_init.service''','~#',8))
        print(lWaitCmdTerm(term,'''systemctl status systemd-wifi-proxy.service''','~#',8))
        print(lWaitCmdTerm(term,'''systemctl status wifi-cal-data-recover.service''','~#',8))
        print(lWaitCmdTerm(term,'''systemctl status htx-wifi-temp-monitor.service''','~#',8))
        print(lWaitCmdTerm(term,'''cat /sys/class/leds/R/brightness''','~#',8))
        print(lWaitCmdTerm(term,'''cat /sys/class/leds/G/brightness''','~#',8))
        print(lWaitCmdTerm(term,'''cat /sys/class/leds/B/brightness''','~#',8))
        print(lWaitCmdTerm(term,'''cat /sys/class/leds/W/brightness''','~#',8))
        print("/* Check unknow reboot reason */")
        print(lWaitCmdTerm(term,'''cat /sys/bus/acpi/devices/INT34DB\:00/reset_type''','~#',8))
        print(lWaitCmdTerm(term,'''cat /sys/bus/acpi/devices/INT34DB\:00/reset_cause''','~#',8))
        print(lWaitCmdTerm(term,'''normal: 0x00;0x08;0x4c;0x00''','~#',8))
        print(lWaitCmdTerm(term,'''i2cget -f -y 2 0x6E 0x20''','~#',8))
        print(lWaitCmdTerm(term,'''i2cget -f -y 2 0x6E 0x22''','~#',8))
        print(lWaitCmdTerm(term,'''i2cget -f -y 2 0x6E 0x6F''','~#',8))
        print(lWaitCmdTerm(term,'''i2cget -f -y 2 0x6E 0x70''','~#',8))
        print(lWaitCmdTerm(term,'''ls -l /sys/class/regulator/regulator.1''','~#',8))
        print(lWaitCmdTerm(term,'''i2cget -y 2 0x6D 0x31''','~#',8))
        print("/* Check PP & switch status */")
        print(lWaitCmdTerm(term,'''cli system/pp/global''','~#',8))
        print(lWaitCmdTerm(term,'''cli system/pp/qos/queues''','~#',8))
        print(lWaitCmdTerm(term,'''cli system/pp/qos/txStat''','~#',8))
        print(lWaitCmdTerm(term,'''cli system/pp/qos/clusterVerbose 0''','~#',8))
        print(lWaitCmdTerm(term,'''cli system/pp/devs''','~#',8))
        print(lWaitCmdTerm(term,'''cli system/pp/session''','~#',8))
        print(lWaitCmdTerm(term,'''cli system/pp/brief''','~#',8))
        print(lWaitCmdTerm(term,'''cli system/pp/stats''','~#',8))
        print(lWaitCmdTerm(term,'''cli system/pp/vpids''','~#',8))
        print(lWaitCmdTerm(term,'''cli system/extsw/resetPortStats 0 0''','~#',8))
        print(lWaitCmdTerm(term,'''cli system/extsw/resetPortStats 0 1''','~#',8))
        print(lWaitCmdTerm(term,'''cli system/extsw/resetPortStats 0 2''','~#',8))
        print(lWaitCmdTerm(term,'''sleep 1''','~#',8))
        print(lWaitCmdTerm(term,'''cli system/extsw/getPortStats 0 0''','~#',8))
        print(lWaitCmdTerm(term,'''cli system/extsw/getPortStats 0 1''','~#',8))
        print(lWaitCmdTerm(term,'''cli system/extsw/getPortStats 0 2''','~#',8))
        print(lWaitCmdTerm(term,'''cli system/ethphy/getEthPhyData''','~#',8))
        print(lWaitCmdTerm(term,'''cli system/ethphy/resetStats 0''','~#',8))
        print(lWaitCmdTerm(term,'''sleep 1''','~#',8))
        print(lWaitCmdTerm(term,'''cli system/ethphy/getStats 0''','~#',8))
        print("/* ATOM more debug information */")
        print(lWaitCmdTerm(term,'''cat /nvram/logs/WiFilog.txt.0''','~#',8))
        print(lWaitCmdTerm(term,'''cat /nvram/logs/WiFilog.txt.1''','~#',8))
        print(lWaitCmdTerm(term,'''cat /nvram/logs/CMlog.txt.0''','~#',8))
        print(lWaitCmdTerm(term,'''cat /nvram/logs/CMlog.txt.1''','~#',8))
        print(lWaitCmdTerm(term,'''cat /nvram/logs/Consolelog.txt.0''','~#',8))
        print(lWaitCmdTerm(term,'''cat /nvram/logs/wifi_hal_debug.log''','~#',8))
        print(lWaitCmdTerm(term,'''cat /nvram/logs/wificlientdrop.txt''','~#',8))
        print(lWaitCmdTerm(term,'''cat /nvram/logs/wifihealth.txt''','~#',8))
        print(lWaitCmdTerm(term,'''journalctl''','~#',8))
        print(ssid2g)
        print(ssid5g)
        print(sn)
        term.close()
        print("=========LAN TEST==========")
        for ip in getips():
            print(ploss(ip,gateway))
            print(ploss(ip,'8.8.8.8'))
            p = subprocess.Popen("speedtest.exe -i {}".format(ip), shell=True, stdout=subprocess.PIPE)
            out, err = p.communicate()
            print(out.decode('UTF8'))
        laniface = getLanIface()
        os.popen('''netsh interface set interface "{}" disabled'''.format(laniface))
        createNewConnection(ssid2g, ssid2g, pwd2g, iface)
        createNewConnection(ssid5g, ssid5g, pwd5g, iface)
        # disconnect(iface)
        g24 = connect(ssid2g, ssid2g, iface)
        if 'successfully' not in g24 and '成功' not in g24:
            raise Exception('2g Wi-Fi Link Failure:'+g24)
        print(g24,ssid2g)
        time.sleep(10)
        for i in range(5):
            time.sleep(5)
            ips = getips()
            if len(ips) != 2: 
                continue
            else:
                if i == 4: raise Exception('2g-Connection of Lan or WLan Failure')
                print(os.popen('ipconfig').read())
                break
        print("=========2G4 TEST==========")
        for ip in getips():
            print(ploss(ip,gateway))
            print(ploss(ip,'8.8.8.8'))
            p = subprocess.Popen("speedtest.exe -i {}".format(ip), shell=True, stdout=subprocess.PIPE)
            out, err = p.communicate()
            print(out.decode('UTF8'))
        time.sleep(2)
        disconnect(iface)
        time.sleep(5)
        g5 = connect(ssid5g, ssid5g, iface)
        if 'successfully' not in g5 and '成功' not in g5:
            raise Exception('5g Wi-Fi Link Failure:'+g5)
        print(g5,ssid5g)
        time.sleep(10)
        for i in range(5):
            time.sleep(5)
            ips = getips()
            if len(ips) != 2: 
                continue
            else:
                if i == 4: raise Exception('5g-Connection of Lan or WLan Failure')
                print(os.popen('ipconfig').read())
                break
        print("=========5G TEST==========")
        for ip in getips():
            print(ploss(ip,gateway))
            print(ploss(ip,'8.8.8.8'))
            p = subprocess.Popen("speedtest.exe -i {}".format(ip), shell=True, stdout=subprocess.PIPE)
            out, err = p.communicate()
            print(out.decode('UTF8'))
    except Exception as e:
        error_class = e.__class__.__name__
        detail = e.args[0]
        cl, exc, tb = sys.exc_info()
        CallStack = traceback.extract_tb(tb)
        for c in CallStack:
            fileName = c[0]
            lineNum = c[1]
            funcName = c[2]
            errMsg = "File \"{}\", line {}, in {}: [{}] {}\n".format(fileName, lineNum, funcName, error_class, detail)
        print(errMsg)
    finally:
        os.popen('''netsh interface set interface "{}" enabled'''.format(laniface))
        log.close()
        term.close()

if __name__ == '__main__':
    main()