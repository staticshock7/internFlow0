from time import sleep
from paramiko import SSHClient, AutoAddPolicy
from socket import gaierror
from concurrent.futures import ThreadPoolExecutor, as_completed
from re import findall
# Terminal color codes
CYN = "\033[31m"
GRN = "\033[32m"
YEL = "\033[33m"
MAG = "\033[35m"
CYN = "\033[36m"
RST = "\033[0m"
logged = False

# prints the menu for the user
def menus():
    print(f"\n{MAG}{'='*30}  {'='*30}{RST}")
    print(f"""

""")

# dev_list function recieves the list of devices to be searched; or it receives theh path to the file containing a similar list
def dev_list():
    arr1 = []
    while True:
        var1 = input(f"{CYN}>>>{RST} Enter devices (e.g. {CYN}LBEPOL4400 LBEPOL4401{RST}) or a file path with one device per line:\n\n{YEL}>{RST} ")
        try:
            if path.exists(var1):
                print(f"\n\n{"="*25} Path exists — Continuing... {"="*25}\n")
                with open(var1, "r") as file:
                    arr1 = [line.strip() for line in file if line.strip()]
                    break
        except Exception:
            print(f"\nIn valid path! Do not enclose the path in {CYN}quotes!{RST}")
            continue
        else:
            try:
                arr1 = var1.strip().split() # removes the carriage returns, and adds each to a list
                break
            except Exception:
                print(f"{CYN}>>>{RST} Invalid input! {CYN}Use spaces between devices{RST} Try again.\n")
                continue
    print(f"\nDevices to be queried: {GRN}{arr1}{RST}")
        
    return arr1

def ssh1(dev, key1, cmd):
    ssh = SSHClient()
    ssh.set_missing_host_key1_policy(AutoAddPolicy())

    try:       
        ssh.connect(f"{dev}.mgmt", username='admin', password=key1)
        shell = ssh.invoke_shell()
        sleep(2)
        output = ""
        recv = ""
        shell.send(f"{cmd}\n")
        sleep(1)
        
        global logged
        logged = True
        while True:
            if shell.recv_ready:
                recv = shell.recv(1024).decode()
                output += recv
                if '--MORE--' in recv or '--More--' in recv:
                    shell.send(' ')
                    sleep(0.5)
            if recv.strip().endswith('>') or recv.strip().endswith('#'):
                break

    except gaierror as e:
        print(f"\n{CYN}Invalid Host:{RST} {dev}. Resolution failed: {e}")
        return f"[ERR] {dev}: {e}"
    except Exception as e:
        print(f"\n{CYN}General connection failure:{RST} {e}")
        return f"[ERR] {dev}: {e}"
    finally:
        ssh.close()

    return output

def flipflop(dev, key1, state, int_num):
    ssh = SSHClient()
    ssh.set_missing_host_key1_policy(AutoAddPolicy())

    try:       
        ssh.connect(f"{dev}.mgmt", username='admin', password=key1)
        shell = ssh.invoke_shell()
        sleep(2)
        output = ""
        recv = ""

        if state == "up":
            shell.send("config t\n")
            sleep(1)
            shell.send(f"interface {int_num}\n")
            sleep(0.5)
            shell.send("disable")
            sleep(1)
        elif state == "down":
            shell.send("config t\n")
            sleep(1)
            shell.send(f"interface {int_num}\n")
            sleep(0.5)
            shell.send("enable")
            sleep(1)
        else:
            print("Unable to change interface")

        if shell.recv_ready:
            recv = shell.recv(1024).decode()

        return recv

    except gaierror as e:
        print(f"\n{CYN}Invalid Host:{RST} {dev}. Resolution failed: {e}")
        return f"[ERR] {dev}: {e}"
    except Exception as e:
        print(f"\n{CYN}General connection failure:{RST} {e}")
        return f"[ERR] {dev}: {e}"
    finally:
        ssh.close()

def rtrShow(dev, key2, cableObj, lb="", fw=""):
    ssh = SSHClient()
    ssh.set_missing_host_key1_policy(AutoAddPolicy())

    try:
        ssh.connect(f"{dev}.mgmt", username='admin', password=key2)
        shell = ssh.invoke_shell()
        sleep(2)

        # checks if lb place was filled to determine which show cmd
        if lb:
            shell.send(f"show interface e{lb}") # show specific interface range for lb
            sleep(1)
            if shell.recv_ready:
                recv = shell.recv(1024).decode()
                recv.splitlines
                line1 = findall(r"\bnotconnect\b", recv)
                cableObj.store_rtr_port(findall(r"\bEth\d\b", line1)) # store disconnected router


    except gaierror as e:
        print(f"\n{CYN}Invalid Host:{RST} {dev}. Resolution failed: {e}")
        return f"[ERR] {dev}: {e}"
    except Exception as e:
        print(f"\n{CYN}General connection failure:{RST} {e}")
        return f"[ERR] {dev}: {e}"
    finally:
        ssh.close()


class cable:
    def __init__(self):
        self.lb_state = None
        self.fw_state = None
        self.rtr_state = None
        self.lb_port = None
        self.fw_port = None
        self.rtr_port = None

    def store_lb_state(self, updown):
        self.lb_state = updown
    def store_fw_state(self, updown):
        self.fw_state = updown
    def store_rtr_state(self, conn_stat):
        self.store_rtr_state = conn_stat
    def store_lb_port(self, port):
        self.store_lb_port = port
    def store_fw_port(self, port):
        self.store_lb_port = port
    def store_rtr_port(self, port):
        self.store_lb_port = port

    def get_lb_state(self):
        return self.lb_state
    def get_fw_state(self):
        return self.fw_state
    def get_rtr_state(self):
        return self.rtr_state
    def get_lb_port(self):
        return self.lb_port
    def get_fw_port(self):
        return self.fw_port
    def get_rtr_port(self):
        return self.rtr_port


def cable1(devs, key1):
    devs = dev_list()
    key1 = getpass(f"{CYN}>>>{RST} Enter the SSH pass: ")
    cmd1 = "show interface eth 25"
    with ThreadPoolExecutor(max_workers=8) as exe:
            futures = {exe.submit(ssh1, i, key1, cmd1): i for i in devs}

            for future in as_completed(futures):
                dev = futures[future]
                output = future.result()
                cable1 = cable()
                cable1.store_lb_state(findall(r"\bup|down\b", output))
                print(f"LB {dev} state: ", cable1.get_lb_state())

                out = flipflop(dev, key1, cable.get_lb_state(), cable.get_lb_port)

                cable1.store_lb_state(findall(r"\bup|down\b", out))
                print(f"LB {dev} state: ", cable1.get_lb_state())


def main():
    while True:
        menus()
        choice1 = input(f"{YEL}>{RST} ")

        # comparing the stored last choice to the present choice to prevent the set_func from
        # triggering the first if statement in each of the functions (occurred when the function had been called
        # at least once before)
        if repeats.get_lastChoice() == choice1:
            repeats.set_func(None)
        else:
            repeats.set_lastChoice(choice1)

        if choice1 == '0':
            sleep(2)
        elif choice1.lower() == 'q':
            print(f"\n\n {CYN}Exiting...{RST}")
            sleep(1)
            break
        else:
            print(f"\nChoose a an option or use {CYN}Q{RST} to exit.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nkey1board Interupt — Exiting")