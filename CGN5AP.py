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
    time.sleep(5)
    data=term.wait('mainMenu>',60)[-1]
    print('[%s]%s'%(time.ctime(),data))
    if 'mainMenu>' in data:
        return term
    raise Exception('Telnet login Failure')

def main():
    logdir = os.path.join(os.getcwd(),"CGN5AP-log\\")
    if not os.path.isdir(logdir):
        os.system("mkdir %s"%logdir)
    iface = displayAvailableIface()
    disconnect(iface)
    gateway = gatewayip()
    term=lLogin(gateway,'msoadmin','kbro-TFM')
    a = lWaitCmdTerm(term,"do/ven",'Menu>',5)
    mac = [i for i in a.splitlines() if 'RF MAC' in i][0].split(' ')[-1].replace(':','-')
    sn = [i for i in a.splitlines() if 'Serial Number' in i][0].split(' ')[-1].replace(':','-')
    fname = logdir + mac + '.CGN5AP-' + time.strftime("%Y%m%d%H%M%S", time.localtime())
    try:
        log = RedirectStdout(open(fname,"w",encoding='UTF-8')) 
        print(mac, time.ctime())
        print(lWaitCmdTerm(term,"do/ven",'Menu>',8))
        print(lWaitCmdTerm(term,"top",'Menu>',8))
        print(lWaitCmdTerm(term,"do/dir",'Menu>',8))
        print(lWaitCmdTerm(term,"do/vendor",'Menu>',15))
        print(lWaitCmdTerm(term,"do/De/uss",'Menu>',15))
        print(lWaitCmdTerm(term,"do/De/dss",'Menu>',15))
        print(lWaitCmdTerm(term,"do/cm",'Menu>',8))
        print(lWaitCmdTerm(term,"do/configfile",'Menu>',8))
        print(lWaitCmdTerm(term,"system/network",'Menu>',30))
        print(lWaitCmdTerm(term,"system/ipPrint",'Menu>',15))
        print(lWaitCmdTerm(term,"system/memory",'Menu>',15))
        print(lWaitCmdTerm(term,"resetCountersPerAllPorts",'Menu>',8))
        print(lWaitCmdTerm(term,"system/l2sw/extswitch StatisticsPerPort 1",'Menu>',10))
        print(lWaitCmdTerm(term,"system/l2sw/extswitch StatisticsPerPort 2",'Menu>',10))
        print(lWaitCmdTerm(term,"system/l2sw/extswitch StatisticsPerPort 3",'Menu>',10))
        print(lWaitCmdTerm(term,"system/l2sw/extswitch StatisticsPerPort 4",'Menu>',10))
        print(lWaitCmdTerm(term,"system/pp/brief",'Menu>',15))
        print(lWaitCmdTerm(term,"system/pp/ddhStats",'Menu>',15))
        print(lWaitCmdTerm(term,"system/pp/devs",'Menu>',15))
        print(lWaitCmdTerm(term,"system/pp/session",'Menu>',15))
        print(lWaitCmdTerm(term,"system/pp/stats",'Menu>',15))
        print(lWaitCmdTerm(term,"shell",':',5))
        print(lWaitCmdTerm(term,"kbro-TFM",'#',5))
        # d = lWaitCmdTerm(term,'''echo "iw dev" | nc 192.168.254.254 54321''','#',5)
        # for i,c in enumerate(d.splitlines()):
        #     if 'wlan2' in c: 
        #         ssid5g = d.splitlines()[i+4].split(' ')[-1]
        #     if 'wlan0' in c: 
        #         ssid2g = d.splitlines()[i+4].split(' ')[-1]
        print(lWaitCmdTerm(term,'''cat ./proc/uptime''','#',15))
        print(lWaitCmdTerm(term,'''arp -n''','#',15))
        print(lWaitCmdTerm(term,'''cat /var/run/landhcps0.leases''','#',15))
        print(lWaitCmdTerm(term,'''dmesg''','#',15))
        print(lWaitCmdTerm(term,'''/fss/gw/usr/sbin/iptables -nvL''','#',15))
        time.sleep(1)
        print(lWaitCmdTerm(term,'''/fss/gw/usr/sbin/iptables -nvL -t nat''','#',15))
        time.sleep(1)
        print(lWaitCmdTerm(term,'''/fss/gw/usr/sbin/iptables -nvL -t mangle''','#',15))
        time.sleep(1)
        print(lWaitCmdTerm(term,'''echo "uptime" | nc 192.168.254.254 54321''','#',15))
        print(lWaitCmdTerm(term,'''echo "echo 7 > /proc/sys/kernel/printk" | nc 192.168.254.254 54321''','#',15))
        print(lWaitCmdTerm(term,'''echo "echo 8 cdebug=0 > /proc/net/mtlk_log/debug" | nc 192.168.254.254 54321''','#',15))
        print(lWaitCmdTerm(term,'''echo "iwconfig |grep wlan0.0" | nc 192.168.254.254 54321''','#',15))
        print(lWaitCmdTerm(term,'''echo "iwconfig |grep wlan0" | nc 192.168.254.254 54321''','#',15))
        print(lWaitCmdTerm(term,'''echo "iwconfig |grep wlan2.0" | nc 192.168.254.254 54321''','#',15))
        print(lWaitCmdTerm(term,'''echo "iwconfig |grep wlan2" | nc 192.168.254.254 54321''','#',15))
        print(lWaitCmdTerm(term,'''echo "iwlist wlan0.0 channel" | nc 192.168.254.254 54321''','#',15))
        print(lWaitCmdTerm(term,'''echo "iwlist wlan0 channel" | nc 192.168.254.254 54321''','#',15))
        print(lWaitCmdTerm(term,'''echo "iwlist wlan2.0 channel" | nc 192.168.254.254 54321''','#',15))
        print(lWaitCmdTerm(term,'''echo "iwlist wlan2 channel" | nc 192.168.254.254 54321''','#',15))
        print(lWaitCmdTerm(term,"cat /nvram/router.cfg",'#',15))
        print(lWaitCmdTerm(term,'''echo "ps" | nc 192.168.254.254 54321''','#',15))
        print(lWaitCmdTerm(term,'''echo "dmesg" | nc 192.168.254.254 54321''','#',15))
        print(lWaitCmdTerm(term,'''echo "ls /var/run/acs_* -l" | nc 192.168.254.254 54321''','#',15))
        print(lWaitCmdTerm(term,'''echo "cat /var/run/acs_history_wlan0.txt" | nc 192.168.254.254 54321''','#',15))
        print(lWaitCmdTerm(term,'''echo "cat /var/run/acs_history_wlan2.txt" | nc 192.168.254.254 54321''','#',15))
        print(lWaitCmdTerm(term,'''echo "cat /var/run/acs_smart_info_wlan0.txt" | nc 192.168.254.254 54321''','#',15))
        print(lWaitCmdTerm(term,'''echo "cat /var/run/acs_smart_info_wlan2.txt" | nc 192.168.254.254 54321''','#',15))
        print(lWaitCmdTerm(term,'''echo "ls -la /var/run/" | nc 192.168.254.254 54321''','#',15))
        print(lWaitCmdTerm(term,'''echo "ls /sys/class/ieee80211/" | nc 192.168.254.254 54321''','#',15))
        print(lWaitCmdTerm(term,'''mtdump wlan0.0 Peerlist''','#',15))
        print(lWaitCmdTerm(term,'''mtdump wlan2.0 Peerlist''','#',15))
        print(lWaitCmdTerm(term,'''mtdump wlan0 Peerlist''','#',15))
        print(lWaitCmdTerm(term,'''mtdump wlan2 Peerlist''','#',15))
        print(lWaitCmdTerm(term,'''iw dev wlan0.0 station dump''','#',15))
        print(lWaitCmdTerm(term,'''iw dev wlan0 station dump''','#',15))
        print(lWaitCmdTerm(term,'''iw dev wlan2.0 station dump''','#',15))
        print(lWaitCmdTerm(term,'''iw dev wlan2 station dump''','#',15))
        print(lWaitCmdTerm(term,'''echo "thermal -r" | nc 192.168.254.254 54321''','#',15))
        print(lWaitCmdTerm(term,'''iwpriv wlan0 gTemperature''','#',15))
        print(lWaitCmdTerm(term,'''iwpriv wlan0.0 gTemperature''','#',15))
        print(lWaitCmdTerm(term,'''iwpriv wlan2 gTemperature''','#',15))
        print(lWaitCmdTerm(term,'''iwpriv wlan2.0 gTemperature''','#',15))
        print(lWaitCmdTerm(term,'''mtdump wlan2.0 RecoveryStats''','#',15))
        print(lWaitCmdTerm(term,'''mtdump wlan0.0 RecoveryStats''','#',15))
        print(lWaitCmdTerm(term,'''mtdump wlan2 RecoveryStats''','#',15))
        print(lWaitCmdTerm(term,'''mtdump wlan0 RecoveryStats''','#',15))
        print(lWaitCmdTerm(term,'''cat /nvram/wifi_2g_recovery_count''','#',15))
        print(lWaitCmdTerm(term,'''cat /nvram/wifi_5g_recovery_count''','#',15))
        print(lWaitCmdTerm(term,'''echo "lspci -k" | nc 192.168.254.254 54321''','#',15))
        term.get()
        print(lWaitCmdTerm(term,'''echo "uci show" | nc 192.168.254.254 54321''','#',15))
        term.get()
        time.sleep(2)
        # phy2g = lWaitCmdTerm(term,'''echo "cat ./run/hostapd-phy0.conf" | nc 192.168.254.254 54321''','#',15)
        # if 'wpa_passphrase' not in phy2g:
        #     phy2g = lWaitCmdTerm(term,'''echo "cat ./tmp/wlan_wave/hostapd_wlan0.conf" | nc 192.168.254.254 54321''','#',15)
        # time.sleep(2)
        # pwd2g = [i for i in phy2g.splitlines() if 'wpa_passphrase' in i][0].split('=')[-1]
        # time.sleep(2)
        # phy5g = lWaitCmdTerm(term,'''echo "cat ./run/hostapd-phy2.conf" | nc 192.168.254.254 54321''','#',15)
        # if 'wpa_passphrase' not in phy5g:
        #     phy5g = lWaitCmdTerm(term,'''echo "cat ./tmp/wlan_wave/hostapd_wlan2.conf" | nc 192.168.254.254 54321''','#',15)
        # time.sleep(2)
        # pwd5g = [i for i in phy5g.splitlines() if 'wpa_passphrase' in i][0].split('=')[-1]
        term << '''echo "cat ./run/hostapd-phy0.conf" | nc 192.168.254.254 54321'''
        time.sleep(3)
        a=term.get()
        term << '''echo "cat ./run/hostapd-phy2.conf" | nc 192.168.254.254 54321'''
        time.sleep(3)
        b=term.get()
        term << '''echo "cat ./tmp/wlan_wave/hostapd_wlan0.conf" | nc 192.168.254.254 54321'''
        time.sleep(3)
        c=term.get()
        time.sleep(3)
        term << '''echo "cat ./tmp/wlan_wave/hostapd_wlan2.conf" | nc 192.168.254.254 54321'''
        time.sleep(3)
        d=term.get()
        if 'ssid' in a:
            print(a)
            ssid2g = [i for i in a.splitlines() if 'ssid'==i.split('=')[0]][-1].split('=')[-1]
            pwd2g = [i for i in a.splitlines() if 'wpa_passphrase'==i.split('=')[0]][-1].split('=')[-1]

        if 'ssid' in b:
            print(b)
            ssid5g = [i for i in b.splitlines() if 'ssid'==i.split('=')[0]][-1].split('=')[-1]
            pwd5g = [i for i in b.splitlines() if 'wpa_passphrase'==i.split('=')[0]][-1].split('=')[-1]

        if 'ssid' in c:
            print(c)
            ssid2g = [i for i in c.splitlines() if 'ssid'==i.split('=')[0]][0].split('=')[-1]
            pwd2g = [i for i in c.splitlines() if 'wpa_passphrase'==i.split('=')[0]][0].split('=')[-1]

        if 'ssid' in d:
            print(d)
            ssid5g = [i for i in d.splitlines() if 'ssid'==i.split('=')[0]][0].split('=')[-1]
            pwd5g = [i for i in d.splitlines() if 'wpa_passphrase'==i.split('=')[0]][0].split('=')[-1] 

        print(lWaitCmdTerm(term,'''echo "cat /proc/net/mtlk/wlan0/channel" | nc 192.168.254.254 54321''','#',15))
        print(lWaitCmdTerm(term,'''echo "cat /proc/net/mtlk/wlan2/channel" | nc 192.168.254.254 54321''','#',15))
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