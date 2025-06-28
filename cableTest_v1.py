from time import sleep
from datetime import datetime
from paramiko import SSHClient, AutoAddPolicy
from socket import gaierror
from getpass import getpass
from os import path, makedirs
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
    print(f"\n{MAG}{'='*30} DEVICE QUERY MENU {'='*30}{RST}")
    print(f"""
{GRN}╔═══════════════════════════════════════════════════════════════════════╗{RST}
{GRN}║{RST} 0. 🔍  Run a {YEL}show{RST} command on a single test device[{CYN}Not Repeatable{RST}]\t{GRN}║{RST}
{GRN}║{RST} 1. 🔬  Match {CYN}prefix{RST} followed by an IP using {YEL}regex{RST} (flexible match)\t{GRN}║{RST}
{GRN}║{RST} 2. 🧩  Match IP followed by {CYN}suffix{RST} using {YEL}regex{RST}\t\t\t{GRN}║{RST}
{GRN}║{RST} 3. 🧠  Match {CYN}prefix{RST} + {YEL}regex IP{RST} + suffix{RST} (flexible match)\t\t{GRN}║{RST}
{GRN}║{RST} 4. 🔎  Search for any {CYN}string{RST} in command output (exact match)\t\t{GRN}║{RST}
{GRN}║{RST} 5. 📥  Download full config output to files\t[{CYN}Not Repeatable{RST}]\t{GRN}║{RST}
{GRN}╚═══════════════════════════════════════════════════════════════════════╝{RST}

{YEL}Other Commands:{RST}
  {CYN}R{RST} — 🔁  Repeat the last function
  {CYN}N{RST} — 🔄  Load a new device list
  {CYN}Q{RST} — ❌  Quit the program
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

def rtrShow(dev, key2, cableObj lb="", fw=""):
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
                cableObj.store_rtr_port(findall(r"\bEth\d\b"))
                


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



def opt1(devs, key1):

    print(f"Enter the {CYN}string prefix{RST} to be queried\n\nExample (in yellow): {YEL}100 permit tcp{RST} {GRN}1.1.1.1 0.0.0.0 any eq 443{RST}\n** prefix can also be just one expected word {CYN}directly before{RST} the IP: {YEL}tcp{RST}")
    in1 = input(f"{YEL}>{RST} ")
    repeats.set_string1(in1)
    print(f"\nEnter the {CYN}specific{RST} show command that contains the data you seek.\nExample: {YEL}show config int man{RST}")
    cmd1 = input(f"{YEL}>{RST} ")
    repeats.set_cmd(cmd1)

    
    with ThreadPoolExecutor(max_workers=8) as exe:
        futures = {exe.submit(ssh1, i, key1, cmd1): i for i in devs}

        for future in as_completed(futures):
            dev = futures[future]
            output = future.result()

            print(f"\n{MAG}{'='*25}{RST} {YEL}{dev}{RST} {MAG}{'='*25}{RST}") # banner for each device results printed
            output = output.splitlines()
            matched = False # used for returning a singular NO MATCH if the for j loop returns no match
            for j in output:
                if (findall(fr"\b{in1}\s*((?:\d{{1,3}}\.){{3}}\d{{1,3}})\b", j)): # using a non-capture group combined with the variable to search j
                    print(f"✔️  {GRN}MATCH{RST} → {YEL}{dev}{RST} {CYN}>>>{RST} {j}")
                    matched = True
            if not matched:
                print(f"✖️  {CYN}NO MATCH{RST} → {YEL}{dev}{RST}")
    return devs, key1

# swapped the regex of opt2 around
def opt2(devs, key1):
    # checks the data in repeats instance for any value of string1. Checks if the function being repeated is the one last called
    if repeats.get_string1 and repeats.get_func() == 2:
        in1 = repeats.get_string1()
        cmd1 = repeats.get_cmd()
    else:     
        # gets the string (prefix) for narrowing the search results
        print(f"Enter the {CYN}string suffix{RST} for querying.\n\nExample (in yellow): {GRN}100 permit tcp 1.1.1.1 0.0.0.0{RST} {YEL}any eq 443{RST}\n||suffix can also be just one expected word {CYN}directly after{RST} the IP: {YEL}any{RST}")
        in1 = input(f"{YEL}>{RST} ")
        repeats.set_string1(in1) # stores the inprt in teh repeats instance for repetition later if wanted
        print(f"\nEnter the {CYN}specific{RST} show command that contains the data you seek.\nExample: {YEL}show config int man{RST}")
        cmd1 = input(f"{YEL}>{RST} ")
        repeats.set_cmd(cmd1) # stores the cmd in teh repeats instance for repetition later if wanted

    # limits commands to show commands
    if 'show' not in cmd1:
        print(f"\n\nPlease enter a {CYN}show{RST} command only!\n\n")
        sleep(4)
        main()
    else:
        # uses concurrent futures to run the searches concurrently for speed
        # downside is the output is randomly displayed, not alphabetically
        with ThreadPoolExecutor(max_workers=8) as exe:
            futures = {exe.submit(ssh1, i, key1, cmd1): i for i in devs} # stores each future with a corresponding device hostname (i)

            for future in as_completed(futures): # works on the result of each future as soon as it's completed
                dev = futures[future] # gets the hostname of a future for by calling its index in futures
                output = future.result() # gathers the result of the future and put it in output for later use

                print(f"\n{MAG}{'='*25}{RST} {YEL}{dev}{RST} {MAG}{'='*25}{RST}") # banner for each device results printed

                output = output.splitlines() # make a list of each line for indexing, and easier search
                # regex for IPs

                matched = False # used for returning a singular NO MATCH if the for j loop returns no match
                # searches the array output for the regex IP
                for j in output:
                    if (findall(fr"\b((?:\d{{1,3}}\.){{3}}\d{{1,3}})\s*{in1}\b", j)):
                        print(f"✔️  {GRN}MATCH{RST} → {YEL}{dev}{RST} {CYN}>>>{RST} {j}")
                        matched = True

                if not matched:
                    print(f"✖️  {CYN}NO MATCH{RST} → {YEL}{dev}{RST}")
    return devs, key1
        
# for searching string + REGEX IP + string
def opt3(devs, key1):
    if repeats.get_string1 and repeats.get_func() == 3:
        in1 = repeats.get_string1()
        in2 = repeats.get_string2()
        cmd1 = repeats.get_cmd()
    else: 
        print(f"Enter the {CYN}prefix string{RST} for querying.\n\n \n Example (in yellow): {YEL}permit tcp{RST}{GRN} 0.0.0.0 0.0.0.0 any eq 22{RST} \n || prefix can also be just one expected word {CYN}directly before{RST} the IP")
        in1 = input(f"{YEL}>{RST} ")
        repeats.set_string1(in1)
        print(f"Enter the {CYN}suffix string{RST} for querying.\n\n \n Example (in yellow): {GRN}permit tcp 0.0.0.0 0.0.0.0 {RST}{YEL}any eq 22{RST} \n || suffix can also be just one expected word {CYN}directly after{RST} the IP")
        in2 = input(f"{YEL}>{RST} ")
        repeats.set_string2(in2)
        print(f"Enter the {CYN}specific{RST} show command that contains the data you seek.\nExample: {YEL}show config int man{RST}")
        cmd1 = input(f"{YEL}>{RST} ")
        repeats.set_cmd(cmd1)

    if 'show' not in cmd1:
        print(f"\n\nPlease enter a {CYN}show{RST} command only!\n\n")
        sleep(4)
        main()
    else:
        with ThreadPoolExecutor(max_workers=8) as exe:
            futures = {exe.submit(ssh1, i, key1, cmd1): i for i in devs}

            for future in as_completed(futures):
                
                dev = futures[future]
                output = future.result()

                print(f"\n{MAG}{'='*25}{RST} {YEL}{dev}{RST} {MAG}{'='*25}{RST}") # banner for each device results printed

                output = output.splitlines()
                # regex for IPs

                matched = False

                for j in output:
                    if (findall(fr"{in1}\s*\b((?:\d{{1,3}}\.){{3}}\d{{1,3}})\s*{in2}\b", j)):
                        print(f"✔️  {GRN}MATCH{RST} → {YEL}{dev}{RST} {CYN}>>>{RST} {j}")
                        matched = True
                if not matched:
                    print(f"✖️  {CYN}NO MATCH{RST} → {YEL}{dev}{RST}")
    return devs, key1

# for searching strings
def opt4(devs, key1):
    if repeats.get_string1 and repeats.get_func() == 4:
        in1 = repeats.get_string1()
        cmd1 = repeats.get_cmd()
    else: 
        print(f"Enter the string to be searched across the devices\n Example: {GRN}snmp-server enable service{RST}")
        in1 = input(f"{YEL}>{RST} ")
        repeats.set_string1(in1)
        print(f"Enter the {CYN}specific{RST} show command that contains the data you seek. \nExample ): {GRN}show config banner{RST}")
        cmd1 = input(f"{YEL}>{RST} ")
        repeats.set_cmd(cmd1)

    if 'show' not in cmd1:
        print(f"\n\nPlease enter a {CYN}show{RST} command only!\n\n")
        sleep(4)
        main()
    else:
        with ThreadPoolExecutor(max_workers=8) as exe:
            futures = {exe.submit(ssh1, i, key1, cmd1): i for i in devs}

            for future in as_completed(futures):
                dev = futures[future]
                output = future.result()

                print(f"\n{MAG}{'='*25}{RST} {YEL}{dev}{RST} {MAG}{'='*25}{RST}") # banner for each device results printed
                output = output.splitlines()
                matched = False # used for returning a singular NO MATCH if the for j loop returns no match
                for j in output:
                    if (findall(rf"\b(?:\w*)-*_*\s*{in1}-*_*\s*(?:\w*)\b", j)):
                        print(f"✔️  {GRN}MATCH{RST} → {YEL}{dev}{RST} {CYN}>>>{RST} {j}")
                        matched = True
                if not matched:
                    print(f"✖️  {CYN}NO MATCH{RST} → {YEL}{dev}{RST}") 
    return devs, key1
# downloading the configs
def opt5(devs, key1):
    cmd1 = input(f"Enter the show config command for your system:\n{YEL}>{RST} ")
    with ThreadPoolExecutor(max_workers=8) as exe:
        futures = {exe.submit(ssh1, i, key1, cmd1):i for i in devs}
    print("after threadpool")
    ### Creating a directory
    print(f"Would you like to store them in a new directory? [y/N]: ")
    in1 = input(f"{YEL}>{RST} ")
    if in1.lower() == 'y':
        print(f"Enter the new directory name: ")
        in2 = input(f"{YEL}>{RST} ")
        try:
            makedirs(in2, exist_ok=True)
            print(f"Created {GRN}{in2}{RST}")
        except Exception as e:
            print(f"Unable to create {CYN}{in2}{RST} due to {CYN}{e}{RST}")
    # End of Creating a directory

    for future in as_completed(futures):
        dev = futures[future]
        output = future.result()

        if in1.lower() == 'y':
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            try:
                with open(f"{in2}/{dev}_{timestamp}_conf.txt", "a") as file:
                    file.write(output)
                    print(f"\n{MAG}{'='*25}{RST} Written {YEL}{dev}{RST} {MAG}{'='*25}{RST}") # banner for each device results printed
            except Exception as e:
                print(f"Unable to access {CYN}{file}{RST} due to {CYN}{e}{RST}")
        else:
            try:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                with open(f"{dev}_{timestamp}_conf.txt", "a") as file:
                    file.write(output)
                    print(f"\n{MAG}{'='*25}{RST} Written {YEL}{dev}{RST} {MAG}{'='*25}{RST}") # banner for each device results printed
            except Exception as e:
                print(f"Unable to access {CYN}{file}{RST} due to {CYN}{e}{RST}")

    return devs, key1

# to store and call data from the dev_list() and the getpass()
class cached:
    def __init__(self):
        self.devs = None
        self.key1 = None
    def set_devs(self):
        self.devs = dev_list()
    def set_key1(self):
        self.key1 = getpass(f'{CYN}>>>{RST} Enter the SSH passowrd: \n')
    def get_devs(self):
        return self.devs
    def get_key1(self):
        return self.key1
    
cacheObj = cached() # guess I gotta leave an instance of the cached class out here for now

def cache(optX):
    # for selecting the correct opt function
    dict0 = {
        1: opt1,
        2: opt2,
        3: opt3,
        4: opt4,
        5: opt5,
    }
    if logged == True:
        dict0[optX](cacheObj.get_devs(), cacheObj.get_key1())
    else:
        cacheObj.set_devs()
        cacheObj.set_key1()
        dict0[optX](cacheObj.get_devs(), cacheObj.get_key1())

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
            opt0()
            sleep(2)
        elif choice1 == '1':
            cache(1)
            repeats.set_func(1)
            sleep(2)
        elif choice1 == '2':
            cache(2)
            repeats.set_func(2)
            sleep(2)
        elif choice1 == '3':
            cache(3)
            repeats.set_func(3)
            sleep(2)
        elif choice1 == '4':
            cache(4)
            repeats.set_func(4)
            sleep(2)
        elif choice1 == '5':
            cache(5)
            repeats.set_func(5)
            sleep(2)
        elif choice1.lower() == 'r':
            repeater()
        elif choice1.lower() == 'n':
            print(f"\n\n {CYN}Clearing the Device list!\n{RST}")
            cacheObj.set_devs()
            sleep(1)
        elif choice1.lower() == 'q':
            print(f"\n\n {CYN}Exiting...{RST}")
            sleep(1)
            break
        else:
            print(f"\nChoose a an option or use {CYN}Q{RST} to exit.")

if __name__ == "__main__":
    try:
        main()
    except key1boardInterrupt:
        print("\n\nkey1board Interupt — Exiting")