import time
from datetime import datetime
import paramiko, getpass

ssh = paramiko.SSHClient()

ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
dev = input("Enter the device: ")
welp = getpass.getpass('Enter the password: ')
ssh.connect((dev+'.mgmt'), username='admin', password=welp)


shell = ssh.invoke_shell()
time.sleep(0.5)
shell.send("\n")
time.sleep(0.5)

time_limit = 2

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

def pull_config():
    
    output = ""
    recv = ""
    shell.send("show config\n")
    time.sleep(1)
    while True:
        if shell.recv_ready():
            recv = shell.recv(1024).decode('utf-8',errors="ignore")
            output += recv
            # print(recv, end='')
            if '--MORE--' in recv:
                shell.send(' ')
                time.sleep(0.5)
        if recv.strip().endswith('>'):
            break
    return output

def save_config():
    time.sleep(0.5)
    choice = input("\n\n***\n\nWould you like to COPY the configs locally? [y/N]?:\n")
    if choice.lower() == 'y':
        result = pull_config()
        with open(f"{dev}_{timestamp}_cfg.txt", "a") as outFile:
            outFile.write(result)
        print(f"\n=========== || Configs Copied to {dev}_{timestamp}_cfg.txt ! \n")
    else:
        print("\n Not saving! Exiting!\n")


def snmp_or_banner():
    
    while True:
        choice = input("Choose B to check for the banner; choose S to check for the SNMP host configs; Q to exit: ")
        if choice == "B":
            shell.send("show config banner\n")
            time.sleep(0.5)
            if shell.recv_ready():
                result = shell.recv(2048).decode()
                if "866 bytes" in result:
                    print("\n\n\n==========\n\nBanner is PRESENT\n\n==========\n")
                    choice2 = input("Would you like to see the banner [y/N]?:\n")
                    if choice2.lower() == 'y':
                        print(result)
                else:
                    print("\n///== Banner NOT present ==//\n\nContinuing")
                    #ssh.close()
                    continue
        elif choice.lower() == 's':
            shell.send("show config snmp-server host\n")
            time.sleep(0.5)
            if shell.recv_ready():
                result = shell.recv(2048).decode()
                if '626 bytes' in result:
                    print("\n\n\n==========\n\nSNMP Server Host Configs are PRESENT\n\n==========\n")
                    time.sleep(0.5)
                    print("\nDisplaying SNMP-Server-Host configs for verification:\n\n", result, "\n\n")
                else:
                    print("\n///== SNMP NOT present ==//\n\nContinuing")
        elif choice.lower() == 'q':
            print("\n\n*** Exiting!")
            break
        else:
            print("\n\nInvalid choice!")

    save_config()

snmp_or_banner()

ssh.close()
