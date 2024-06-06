import socket

PORT = 5000
MSG_DELIM = '\0'
BUFFER_SIZE = 1024


class SocketWrapper:
    def __init__(self, sock):
        self.sock = sock
        self.data = ""

    def send_msg(self, msg):
        msg_to_send = msg + MSG_DELIM
        self.sock.send(msg_to_send.encode('utf-8'))

    def get_msg(self):
        parts = self.data.split(MSG_DELIM)

        # we may have more than one message buffered, just get one
        # and keep the rest for a later receive
        self.data = MSG_DELIM.join(parts[1:])
        return parts[0]

    def has_buffered_msg(self):
        return MSG_DELIM in self.data

    def recv_msg(self):
        if self.has_buffered_msg():
            return self.get_msg()

        while True:
            data = self.sock.recv(BUFFER_SIZE)
            if not data:
                break

            decoded_data = data.decode('utf-8')
            self.data += decoded_data
            if MSG_DELIM in self.data:
                break

        if self.has_buffered_msg():
            return self.get_msg()
        return None