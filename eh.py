from hostFileEditor import Hosts


host = Hosts()

print("Disclaimer: DO NOT USE THIS MALICIOUSLY\nThis was created as a tool, not for malicious intent.")

print("Which mode would you like?")
print("1. Auto fill-in IP from URL")
print("2. Manually ser URLs ")
mode = input("> ")
while not mode.strip() in ['1','2']:
    print("1. Auto fill-in IP from URL")
    print("2. Manually ser URLs ")
    mode = input("> ")

print("What would you like to add?")
match mode:
    case '1':
        while True:
            url = input("> ")
            host.add(url)
    
    case '2':
        while True:
            print("Url:")
            url = input("> ")

            print("\n IP:")
            ip = input("> ")

            host.add(url, ip)