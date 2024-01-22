#!/usr/bin/python
import selectors, socket, types
import ledconfig, ledconn

class Ledclient:
    def __init__(self):
        self.host = None
        self.port = None
        self.inbound = ""
        self.outbound = b""
        self.is_outbound_empty = True
        self.ready = False

        #self.DEBUG = True
        self.DEBUG = False

        self.sel = selectors.DefaultSelector()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setblocking(False)

    def connect(
      self,
      host=ledconfig.CONNECT_HOST,
      port=ledconfig.CONNECT_PORT
    ):
        self.host = host
        self.port = port
        self.socket.connect_ex((host, port))
        data = types.SimpleNamespace(
            inbound="",
            outbound=b""
        )
        self.DEBUG and print(f"[ledclient.py connect] Connected to {host}:{port}.")

        self.sel.register(
            self.socket,
            selectors.EVENT_READ | selectors.EVENT_WRITE,
            data=data
        )

        return self

    def loop_once(self):
        events = self.sel.select(timeout=None)
        for key, mask in events:
            self.handle_connection(key, mask)
        return self

    def handle_connection(self, key, mask):
        data = key.data
        if mask & selectors.EVENT_READ:
            inbound = self.socket.recv(1024)
            if inbound:
                data.inbound += inbound.decode()
                while "\n" in data.inbound or "\r" in data.inbound:
                    eol = data.inbound.find("\n")
                    eol = eol if eol != -1 else data.inbound.find("\r")
                    line = data.inbound[0:eol].strip()
                    if line:
                        data.inbound = data.inbound[eol+1:]
                        self.handle_message(ledconn.MessageParser().parse(line))

            else:
                self.socket.close()
                self.on_disconnect()
                raise Exception("Connection closed")

        if mask & selectors.EVENT_WRITE:
            if self.outbound:
                if self.DEBUG:
                    dots = "" if self.is_outbound_empty else "..."
                    print(f"{dots}> {self.outbound!r}")
                sent = self.socket.send(self.outbound)
                self.outbound = self.outbound[sent:]
                self.is_outbound_empty = len(self.outbound) == 0

    def handle_message(self, message):
        msg_type = message.type()[1:]
        msg_subtype = message.subtype()[1:]
        handlers = filter(len, [
            f"on_{msg_type}_{msg_subtype}_message" if msg_subtype else "",
            f"on_{msg_type}_message",
            f"on_message",
        ])

        if message.prefixes() == ":hi:welcome":
            self.ready = True

        for h in handlers:
            if hasattr(self, h) and callable(getattr(self, h)):
                getattr(self, h)(message)
                break

    def on_connect(self):
        print(f"[ledclient.py] Connected to {self.host} {self.port}.")

    def on_connection_failed(self, e):
            print(f"[ledclient.py] Connected failed to {self.host} {self.port}: {e}.")

    def on_disconnect(self):
        pass


    def on_message(self, message):
        print(f"[ledclient.py] Unhandled message:")
        print(message.report())

    def send_message(self, message):
        self.outbound += bytes(str(message).encode("utf-8"))
        self.loop_once()


