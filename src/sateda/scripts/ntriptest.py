import socket, ssl, base64
import struct

import numpy as np

from sateda.io import rtcm

def _form_request(credentials=None):
    request_str = 'GET /{} HTTP/1.0\r\nUser-Agent: NTRIP TEST\r\n'.format(
        'ALIC00AUS0')
    if credentials is not None:
        request_str += 'Authorization: Basic {}\r\n'.format(
            credentials)
    request_str += '\r\n'
    return request_str.encode('utf-8')


def main(args):
    hostname = args.hostname
    port = args.port
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    creds = base64.b64encode('{}:{}'.format(
        args.username, args.password).encode('utf-8')).decode('utf-8')
    # If SSL, wrap the socket
    # if self.ssl:
    #   # Configre the context based on the config
    ssl_context = ssl.create_default_context()
    #   if self.cert:
    #     self._ssl_context.load_cert_chain(self.cert, self.key)
    #   if self.ca_cert:
    ssl_context.load_verify_locations("AmazonRootCA1.pem")

    raw_socket = server_socket
    server_socket = ssl_context.wrap_socket(raw_socket, server_hostname=hostname)

    server_socket.settimeout(5)

    try:
        server_socket.connect((hostname, port))
    except Exception as e:
        print(
            'Unable to connect socket to server at http://{}:{}'.format(hostname, port))
        print('Exception: {}'.format(str(e)))
        return False

    try:
        server_socket.send(_form_request(credentials=creds))
    except Exception as e:
        print('Unable to send request to server')
        print('Exception: {}'.format(str(e)))
        return False

    response = ''
    try:
      response = server_socket.recv(1024).decode('ISO-8859-1')
    except Exception as e:
      print(
        'Unable to read response from server at http://{}:{}'.format(hostname, port))
      print('Exception: {}'.format(str(e)))
      return False
    print(response)

    data_type = []
    for i in range(3600*4):
        data = b''
        while True:
          try:
            chunk = server_socket.recv(1024)
            data += chunk
            if len(chunk) < 1024:
              break
          except Exception as e:
            print('Error while reading {} bytes from socket'.format(1024))
            break
        # print('Read {} bytes'.format(len(data)))
        # print(data.read('uint:8'))
        _RTCM_3_2_PREAMBLE = 0b11010011
        # print(data[0])
        # print(data[0] == _RTCM_3_2_PREAMBLE)

        data_length = ((data[1] & 0b00000011) << 8) | data[2]
        checksum_bytes = data[-3:]
        uint12_1 = int.from_bytes(data[3:5], byteorder='big') >> 4
        data_type.append(uint12_1)
        print(f"RTCM: {uint12_1} length {data_length}")
        datadecoder = rtcm.RTCM(uint12_1)
        print(datadecoder.decode(data))

    #print unique data types
    # print(data_type)
    print(np.unique(np.array(data_type)))
    return True

def parse_args():
    import argparse
    parser = argparse.ArgumentParser(description='Test NTRIP connection')
    parser.add_argument('--hostname', type=str, default='ntrip.data.gnss.ga.gov.au',
                        help='NTRIP server hostname')
    parser.add_argument('--port', type=int, default=443,
                        help='NTRIP server port')
    parser.add_argument('--username', type=str, default='',
                        help='NTRIP server username')
    parser.add_argument('--password', type=str, default='',
                        help='NTRIP server password')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    main(args)

