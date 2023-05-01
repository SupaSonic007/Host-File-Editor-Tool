from hostFileEditor import Hosts


class CustomHosts(Hosts):

    def __init__(self) -> None:
        print("What's the location of your host file?")
        location = input("> ")
        super().__init__(location)
