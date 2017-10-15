import socket
import uos
import network
import websocket
import websocket_helper
import time
import dht_sensor
import ir


sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
# set IP address
sta_if.ifconfig(('192.168.0.6', '255.255.255.0', '192.168.0.1', '8.8.8.8'))
# connect to WIFI
sta_if.connect('SSID', 'PASSWORD')


class websocketServer:
    def __init__(self, port):
        listen_s = socket.socket()
        listen_s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        ai = socket.getaddrinfo("0.0.0.0", port)
        addr = ai[0][4]

        listen_s.bind(addr)
        listen_s.listen(1)
        listen_s.setsockopt(socket.SOL_SOCKET, 20, self.accept_conn)

        for i in (network.AP_IF, network.STA_IF):
            iface = network.WLAN(i)
            if iface.active():
                print("WebREPL daemon started on ws://%s:%d" % (iface.ifconfig()[0], port))

        self.listen_s = listen_s
        self.buf = bytearray(10)
        self.buf_view = memoryview(self.buf)
        self.connected = False

    def accept_conn(self, listen_sock):
        cl, remote_addr = listen_sock.accept()
        print("\nWebSocket connection from:", remote_addr)
        websocket_helper.server_handshake(cl)
        self.ws = websocket.websocket(cl, True)
        self.ws.ioctl(9, 2) # change to data frame
        cl.setblocking(False)
        self.client_s = cl
        self.connected = True

    def serve(self):
        while True:
            if self.connected:
                try:
                    data = self.ws.read(64)
                    if data is not None:
                        print(data)
                        if len(data) == 1 and data[0] == 100:
                            temp, humid = dht_sensor.read()
                            self.buf[0] = data[0]
                            self.buf[1] = 0
                            self.buf[2] = temp >> 8
                            self.buf[3] = temp & 0xff
                            self.buf[4] = humid >> 8
                            self.buf[5] = humid & 0xff
                            self.ws.write(self.buf_view[:6])
                        elif len(data) == 2 and data[0] == 200:
                            ir.send_ir_command(data[1])
                            self.buf[0] = data[0]
                            self.buf[1] = data[1]
                            self.ws.write(self.buf_view[:2])
                except OSError:
                    self.connected = False
            time.sleep(0.01)


server = websocketServer(6578)
server.serve()