import sys
import getopt
import socket
from time import sleep
import threading
import math

class Stat:
    def __init__(self):
        self.data = {}
        stats = threading.Thread(target=self.printing)
        stats.start()

    def printing(self):
        while True:
            sleep(1)
            if len(self.data.keys()) == 0:
                continue

            print('------------')
            for router in self.data:
                print(f"{router}\t|\t{round(self.data[router]['current'] / 1000 / 1000, 3)}\tMbps - total: {math.ceil(self.data[router]['total'] / 1000 / 1000 / 8)} MB")
                self.data[router]['current'] = 0
            print('************')

    def add_router(self, router):
        self.data[router] = {
            'total': 0,
            'current': 0
        }

    def add_data(self, router, data_len):
        self.data[router]['total'] += data_len
        self.data[router]['current'] += data_len

def rcv_data(conn, address, stat):
    router_ip = address[0]
    print("Listening packets from addres", router_ip)
    stat.add_router(router_ip)

    while True:
        data = conn.recv(10240)
        if (not data):
            break

        stat.add_data(router_ip, len(data) * 8)

    conn.close()
    print("Connection closed", address[0])
    return

def record(cfg):
    """ Record BMP messages by listening on port and writing to file

        :param cfg:     Config dictionary
    """

    try:
        sock =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', cfg['port']))
        sock.listen(100)

        stat = Stat()

        while True:
            (conn, address) = sock.accept()
            t = threading.Thread(target=rcv_data, args=(conn, address, stat))
            t.start()

    except socket.error as msg:
        print("ERROR: failed to record: %r", msg)

def parseCmdArgs(argv):
    """ Parse commandline arguments

        Usage is printed and program is terminated if there is an error.

        :param argv:   ARGV as provided by sys.argv.  Arg 0 is the program name

        :returns:  dictionary defined as::
                {
                    mode:       <mode 'record'>,
                    port:       <int port number>,
                }
    """
    REQUIRED_ARGS = 2
    found_req_args = 0
    cmd_args = { 'mode': None,
                 'port': None }

    if (len(argv) < 3):
        print("ERROR: Missing required args")
        usage(argv[0])
        sys.exit(1)

    try:
        (opts, args) = getopt.getopt(argv[1:], "hm:p:f:r:d:",
                                       ["help", "mode=", "port="])

        for o, a in opts:
            if o in ("-h", "--help"):
                usage(argv[0])
                sys.exit(0)

            elif o in ("-m", "--mode"):
                found_req_args += 1
                if (a in ['record']):
                    cmd_args['mode'] = a
                else:
                    print("ERROR: Invalid mode of '%s", a)
                    usage(argv[0])
                    sys.exit(1)

            elif o in ("-p", "--port"):
                found_req_args += 1
                cmd_args['port'] = int(a)

            else:
                usage(argv[0])
                sys.exit(1)

        if (found_req_args < REQUIRED_ARGS):
            print("ERROR: Missing required args, found %d required %d", found_req_args, REQUIRED_ARGS)
            usage(argv[0])
            sys.exit(1)

        return cmd_args

    except (getopt.GetoptError, TypeError) as err:
        print("%s", str(err)) # will print something like "option -a not recognized"
        usage(argv[0])
        sys.exit(2)


def usage(prog):
    """ Usage - Prints the usage for this program.

        :param prog:  Program name
    """
    print("")
    print("Usage: %s [OPTIONS]", prog)
    print("")

    print("REQUIRED OPTIONS:")
    print("  -m, --mode".ljust(30) + "'record'")
    print("  -p, --port".ljust(30) + "TCP Port to listen on or to send to")
    print("")

    print("OPTIONAL OPTIONS:")
    print("  -h, --help".ljust(30) + "Print this help menu")


def main():
    """
        Start of program from shell
    """
    cfg = parseCmdArgs(sys.argv)

    if (cfg['mode'] == 'record'):
        print("Listening for connection...")
        record(cfg)


if __name__ == '__main__':
    main()
