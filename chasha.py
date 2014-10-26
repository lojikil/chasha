import socket


# TODO: add Directory/Info classes to more easily format the various types
# of structured data that Gopher systems can handle.
# directory could just have a simple "add_child"
# XXX: have a sane default of just dumping all routes?
# would have to associate a name with all routes too...

def cget(obj, idx, default=None):
    try:
        return obj[idx]
    except IndexError:
        return default


class Directory(object):

    def __init__(self, children=None):
        if children is not None:
            self.children = children
        else:
            self.children = []

    def add_child(self, child):
        self.children.append(child)

    def __str__(self):
        res = []
        for child in self.children:
            if isinstance(child, (list, tuple)):
                tmpl = "{0}{1}\t{2}\t{3}\t{4}\t{5}"
                if isinstance(child, tuple):
                    child = list(child)

                print "[!] child: ", child
                res.append(tmpl.format(cget(child, 0),
                                       cget(child, 1),
                                       cget(child, 2, "FAKE"),
                                       cget(child, 3, "NULL"),
                                       cget(child, 4, "0"),
                                       cget(child, 5, "+")))
            elif isinstance(child, Directory):
                res.append(child.listing())
            #elif isinstance(child, Information):
            #    res.append(str(child))
            elif isinstance(child, str):
                # should probably handle multiline strings here...
                res.append("i{0}\tFAKE\tNULL\t0\t+".format(child))
        res.append(".\r\n")
        print "[!] returning: ", res
        return '\r\n'.join(res)


class Chasha(object):

    def __init__(self):
        self.routes = {}

    def add_route(self, descriptor, callback):
        self.routes[descriptor] = callback

    def route(self, descriptor, **kwargs):
        def wrapper(handler):
            self.add_route(descriptor, handler)
            return handler
        return wrapper

    def default(self):
        return self.route("/")

    def default_directory(self):
        pass

    def router(self, descriptor):
        idx = 0
        print "[!] In router; descriptor: {0}".format(descriptor)
        if descriptor == "":
            if "/" in self.routes:
                return self.routes["/"]
            else:
                return self.default_directory()
        # NOTE: just for intial testing
        # actual processing has to go on here in the real deal...
        # TODO: look at processing the routes with subs & regex...
        # e.g. foo/bar<blah:int> could become foo/bar<blah:[0-9]+
        return self.routes[descriptor]

    def run(self, **kwargs):

        self.port = kwargs.get('port', 7070)
        self.host = kwargs.get('host', '0.0.0.0')

        self.loop_flag = True

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.host, self.port))
        sock.listen(1)
        while self.loop_flag:
            try:
                print "[!] waiting for accept..."
                conn, addr = sock.accept()
                print "[+] client connected from {0}".format(addr)
                desc = conn.recv(2048)
                desc = desc.strip()
                print "[!] client sent data..."
                handler = self.router(desc)
                print "[!] router matched said data..."
                data = handler()
                print "[!] handler returned data..."
                # NOTE: should process return type here...
                conn.send(str(data))
                conn.close()
            except KeyboardInterrupt:
                self.loop_flag = False
            except Exception as e:
                print e
                # NOTE: Should check if socket accidentally closed here
                # and, if so, reopen
                pass
        sock.close()
