import socket
import re


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

    def __init__(self, descriptor, name=None, children=None, port=7070,
                 host='127.0.0.1'):

        self.descriptor = descriptor
        self.port = port
        self.host = host
        if children is not None:
            self.children = children
        else:
            self.children = []

        self.name = name

    def add_child(self, child):
        self.children.append(child)

    #### start refactorable zeon
    # really, the although the below is at least _somewhat_ clean
    # I suspect it could be made cleaner still.

    def add_common(self, dtype, description, descriptor, host=None, port=None):

        if host is None:
            host = self.host

        if port is None:
            port = self.port

        self.add_child([ dtype, description, descriptor, host, port])

    def add_link(self, description, descriptor, host=None, port=None):

        self.add_common('h',
                        description,
                        "URL:{0}".format(descriptor),
                        host,
                        port)

    def add_image(self, description, descriptor, host=None, port=None):

        self.add_common('I',
                        description,
                        descriptor,
                        host,
                        port)

    def add_binary(self, description, descriptor, host=None, port=None):

        self.add_common('9',
                        description,
                        descriptor,
                        host,
                        port)

    def add_telnet(self, description, descriptor, host=None, port=None):

        self.add_common('8',
                        description,
                        descriptor,
                        host,
                        port)

    def add_search(self, description, descriptor, host=None, port=None):

        self.add_common('7',
                        description,
                        descriptor,
                        host,
                        port)

    def add_uue(self, description, descriptor, host=None, port=None):

        self.add_common('6',
                        description,
                        descriptor,
                        host,
                        port)

    def add_binarchive(self, description, descriptor, host=None, port=None):

        self.add_common('5',
                        description,
                        descriptor,
                        host,
                        port)

    def add_binhex(self, description, descriptor, host=None, port=None):

        self.add_common('4',
                        description,
                        descriptor,
                        host,
                        port)

    def add_error(self, description, descriptor, host=None, port=None):

        self.add_common('3',
                        description,
                        descriptor,
                        host="error.nohost",
                        port="0")

    def add_ccso(self, description, descriptor, host=None, port=None):

        self.add_common('2',
                        description,
                        descriptor,
                        host,
                        port)

    def add_directory(self, description, descriptor, host=None, port=None):

        self.add_common('1',
                        description,
                        descriptor,
                        host,
                        port)

    def add_text(self, description, descriptor, host=None, port=None):

        self.add_common('0',
                        description,
                        descriptor,
                        host,
                        port)

    def add_audio(self, description, descriptor, host=None, port=None):

        self.add_common('s',
                        description,
                        descriptor,
                        host,
                        port)

    def add_html(self, description, descriptor, host=None, port=None):

        self.add_common('h',
                        description,
                        descriptor,
                        host,
                        port)

    #### end refactorable zone

    def listing(self):
        tmpl = "1{0}\t{1}\t{2}\t{3}\t+"
        return tmpl.format(self.name,
                           self.descriptor,
                           self.host,
                           self.port)

    def __str__(self):
        res = []
        for child in self.children:
            if isinstance(child, (list, tuple)):
                tmpl = "{0}{1}\t{2}\t{3}\t{4}\t{5}"
                if isinstance(child, tuple):
                    child = list(child)

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
        return '\r\n'.join(res)


class Request(object):

    def __init__(self, descriptor=None, search=None):
        self.descriptor = descriptor
        self.search = search


class Chasha(object):

    def __init__(self):
        self.routes = {}
        self.dyn_routes = {}
        self.typepats = {'int': '[0-9]+',
                         'float': '[0-9]+\.[0-9]+',
                         'path': '[A-Za-z0-9/\.\-\s]+',
                         'alnum': '[A-Za-z0-9]',
                         'alpha': '[A-Za-z]+'}
        # really more for inspection than anything
        # else. Probalby *could* use these as the
        # defaults down below...
        self.debug = False
        self.port = 7070
        self.host = '0.0.0.0'
        self.request = None

    def add_route(self, descriptor, callback):
        if ':' in descriptor:
            desc = self.compile_route(descriptor)
            self.dyn_routes[re.compile(desc)] = callback
        else:
            self.routes[descriptor] = callback

    def route(self, descriptor, **kwargs):
        def wrapper(handler):
            self.add_route(descriptor, handler)
            return handler
        return wrapper

    def default(self):
        return self.route("/")

    def compile_route(self, descriptor):
        parts = descriptor.split('/')

        res = []

        # could probably do this in a few replace calls,
        # but being explicit & breaking things apart seems nicer to me
        for part in parts:

            if ':' in part:
                chasti = part[1:-1].split(':')
                if chasti[1] not in self.typepats:
                    pat = ".*"
                else:
                    pat = self.typepats[chasti[1]]
                res.append("(?P<{0}>{1})".format(chasti[0], pat))
            else:
                res.append(part)

        return '/'.join(res)

    def router(self, descriptor):
        idx = 0
        if self.debug:
            print "[!] In router;descriptor: {0}".format(descriptor)
        if descriptor == "":
            return self.routes.get("/")
        # NOTE: just for intial testing
        # actual processing has to go on here in the real deal...
        # TODO: look at processing the routes with subs & regex...
        # e.g. foo/bar<blah:int> could become foo/bar<blah:[0-9]+
        if descriptor in self.routes:
            # do we have a static descriptor that matches?
            # if yes, just return it
            if self.debug:
                print "[!] in self.routes?"
            return self.routes[descriptor]
        else:
            if self.debug:
                print "[!] in self.dyn_routes?"
            descriptors = self.dyn_routes.keys()
            for desc in descriptors:
                mat = desc.match(descriptor)

                if mat:
                    if self.debug:
                        print "[!] in dyn return?"
                    return (mat, self.dyn_routes[desc])

        if self.debug:
            print "[!] in None return"
        return None

    def run(self, **kwargs):

        self.port = kwargs.get('port', 7070)
        self.host = kwargs.get('host', '0.0.0.0')

        self.loop_flag = True

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.host, self.port))
        sock.listen(1)
        while self.loop_flag:
            try:
                if self.debug:
                    print "[!] waiting for accept..."
                conn, addr = sock.accept()
                print "[+] client connected from {0}".format(addr),
                desc = conn.recv(2048)
                desc = desc.strip()
                print " and requested: ", desc
                if self.debug:
                    print "[!] client sent data..."
                try:
                    descparts = desc.split('\t')
                    self.request = Request(cget(descparts, 0),
                                           cget(descparts, 1))
                    handler = self.router(descparts[0])
                    if self.debug:
                        print "[!] router matched said data..."
                        print "[!] type of handler: ", type(handler)
                    if isinstance(handler, tuple):
                        mat = handler[0]
                        if self.debug:
                            print "[!] mat.groupdict:", mat.groupdict()
                            print "[!] handler: ", handler[1]
                        handler = handler[1]
                        data = handler(**mat.groupdict())
                    else:
                        data = handler()
                    if self.debug:
                        print "[!] handler returned data..."
                except Exception as e:
                    print "[!] exception: ", e
                    data = "3nosuchdroute\tdoes not exist\terror.host\t1\r\n"
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


#class ChashaAsync(Chasha, asyncore.dispatcher)
