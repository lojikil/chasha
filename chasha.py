import socket
import re
import os
import traceback

text_types = [".txt", ".ps", ".text", ".lst", ".dat",
              ".py", ".c", ".c++", ".cpp", ".md", ".rst",
              ".css", ".js", ".java", ".scm", ".ss", ".cfm"]


def cget(obj, idx, default=None):
    try:
        return obj[idx]
    except IndexError:
        return default


class GopherError(Exception):
    pass


class Information(object):
    def __init__(self, body):
        self.body = body

    def __str__(self):
        return self.body

    def __bytes__(self):
        return bytes(self.body, encoding="utf8")

    def to_gemini(self):
        # NOTE we actually probably want to apply some sort
        # of grouping algorithm to remove newlines or the like
        # from `self#body`, but for now just return the same
        return self.body


class Search(object):
    # XXX I suspect what we actually want is to make
    # a decorator that can mark something as a search,
    # and then use that to instantiate a Search object.
    # this can then return the wrapped call? I may need
    # to think about this more
    #
    # actually, thinking about it more, since we will
    # still need to mount a route, we may not care about
    # having this as a wrapper, but rather just to help
    # the Directory system; it *may not* be needed much
    # herein

    def __init__(self, prompt):
        self.prompt = prompt


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

    #### start refactorable zone
    # really, the although the below is at least _somewhat_ clean
    # I suspect it could be made cleaner still.

    def add_common(self, dtype, description, descriptor, host=None, port=None):

        if host is None:
            host = self.host

        if port is None:
            port = self.port

        self.add_child([dtype, description, descriptor, host, port])

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

                res.append(tmpl.format(child[0],
                                       child[1],
                                       cget(child, 2, "FAKE"),
                                       cget(child, 3, "NULL"),
                                       cget(child, 4, "0"),
                                       cget(child, 5, "+")))
            elif isinstance(child, Directory):
                res.append(child.listing())
            elif isinstance(child, Information):
                res.append(str(child))
            elif isinstance(child, Search):
                res.append(child.listing())
            elif isinstance(child, str):
                # should probably handle multiline strings here...
                res.append("i{0}\tFAKE\tNULL\t0\t+".format(child))
        res.append(".\r\n")
        return '\r\n'.join(res)

    def __bytes__(self):
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
            elif isinstance(child, Information):
                res.append(str(child))
            elif isinstance(child, Search):
                res.append(child.listing())
            elif isinstance(child, str):
                # should probably handle multiline strings here...
                res.append("i{0}\tFAKE\tNULL\t0\t+".format(child))
        res.append(".\r\n")
        return bytes('\r\n'.join(res), "utf-8")

    def to_gemini(self):
        res = []
        for child in self.children:
            if isinstance(child, (list, tuple)):
                dtype = child[0]
                match dtype
                    case 'i':
                        res.append(child[1])
                    case '2':
                        res.append(f"=> ccso://{child[2]} {child[1]}")
                    case ['8', 'T']:
                        res.append(f"=> telnet://{child[2]} {child[1]}")
                    case 'h':
                        next_url = child[2].replace("URL:", "")
                        res.append(f"=> {next_url} {child[1]}")
                    case _:
                        # FIXME we can actually do a bit better here by detecting if the
                        # host for the next URL is actually the same as this server...
                        next_url = None
                        if child[4] != 1965:
                            next_url = f"gemini://{child[3]}:{child[4]}/{child[2]}"
                        else:
                            next_url = f"gemini://{child[3]}/{child[2]}"
                        res.append(f"=> {next_url} {child[1]}")

            elif isinstance(child, Directory):
                tmpl = f"=> {child.descriptor} {child.name}"
                res.append(tmpl)
            elif isinstance(child, Information):
                res.append(child.to_gemini())
            elif isinstance(child, Search):
                res.append(child.to_gemini())
            elif isinstance(child, str):
                res.append(child)
        return bytes('\r\n'.join(res), "utf-8")


class Request(object):

    def __init__(self, descriptor=None, search=None, body=None, rtype=None):
        self.descriptor = descriptor
        self.search = search
        self.body = body
        self.rtype = rtype


class Chasha(object):

    def __init__(self):
        self.routes = {}
        self.dyn_routes = {}
        self.dyn_search = {}
        self.search_routes = {}
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

    def add_route(self, descriptor, callback, cfg):
        # XXX I suspect we can clean this up more
        # with the Information & Search classes from
        # above: we can just have one _route_ table
        # and then wrap the callback in whatever
        # class from above, and allow the class to
        # handle actually calling the callback
        #
        # this would in someways make the Search handling
        # easier
        if ':' in descriptor:
            desc = self.compile_route(descriptor)
            if "search" in cfg:
                self.dyn_search[re.compile(desc)] = callback
            else:
                self.dyn_routes[re.compile(desc)] = callback
        elif "search" in cfg:
            self.search_routes[descriptor] = callback
        else:
            self.routes[descriptor] = callback

    def route(self, descriptor, **kwargs):
        def wrapper(handler):
            self.add_route(descriptor, handler, kwargs)
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
            print("[!] In router;descriptor: {0}".format(descriptor))
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
                print("[!] in self.routes?")
            return self.routes[descriptor]
        elif descriptor in self.search_routes:
            return self.search_routes[descriptor]
        else:
            if self.debug:
                print("[!] in self.dyn_routes?")
            descriptors = list(self.dyn_routes.keys())
            for desc in descriptors:
                mat = desc.match(descriptor)

                if mat:
                    if self.debug:
                        print("[!] in dyn return?")
                    return (mat, self.dyn_routes[desc])

        if self.debug:
            print("[!] in None return")
        return None

    def run(self, **kwargs):

        self.port = kwargs.get('port', 7070)
        self.host = kwargs.get('host', '0.0.0.0')

        self.server_type = kwargs.get("server_type", "gopher")

        if self.server_type not in ["gopher", "gemini", "spartan"]:
            self.server_type = "gopher"

        self.loop_flag = True

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.host, self.port))
        sock.listen(1)
        while self.loop_flag:
            try:
                if self.debug:
                    print("[!] waiting for accept...")
                conn, addr = sock.accept()
                print("[+] client connected from {0}".format(addr), end=' ')
                # FIXME we need to actually read more here...
                desc = conn.recv(2048)
                desc = desc.strip()
                # XXX this is also likely needing a review:
                desc = desc.decode("utf-8")
                print(" and requested: ", desc)
                if self.debug:
                    print("[!] client sent data...")
                try:
                    descparts = desc.split('\t')
                    self.request = Request(cget(descparts, 0),
                                           cget(descparts, 1))
                    handler = self.router(descparts[0])
                    if self.debug:
                        print("[!] router matched said data...")
                        print("[!] type of handler: ", type(handler))
                    if isinstance(handler, tuple):
                        mat = handler[0]
                        if self.debug:
                            print("[!] mat.groupdict:", mat.groupdict())
                            print("[!] handler: ", handler[1])
                        handler = handler[1]
                        data = handler(**mat.groupdict())
                    else:
                        data = handler()
                    if self.debug:
                        print("[!] handler returned data...")
                except GopherError as ge:
                    data = "3gophererror\t{0}\terror.host\t1\r\n".format(ge.message)
                except Exception as e:
                    print("[!] exception: ", e)
                    traceback.print_exception(e)
                    data = "3nosuchdroute\tdoes not exist\terror.host\t1\r\n"
                # NOTE: should process return type here...
                print("[!] here on 344, data is:", type(data), data)
                if type(data) is str:
                    conn.send(bytes(data, "utf-8"))
                else:
                    conn.send(bytes(data))
                conn.close()
            except KeyboardInterrupt:
                self.loop_flag = False
            except Exception as e:
                print(e)
                traceback.print_exception(e)
                # NOTE: Should check if socket accidentally closed here
                # and, if so, reopen
                pass
        sock.close()


def static_dispatch(portion, descriptor, root="."):
    """Handle static requests from a descriptor
    in a safe fashion (removing '..', canonicalizing,
    &c. Dispatches file reads or directory creation
    based on the type of object pointed to. Use
    `static_file` if you only want serve files.
    """
    portion = portion.replace("../", "")
    tpath = os.path.join(root, portion)
    if os.path.isfile(tpath):
        fh = file(tpath)
        data = fh.read()
        fh.close()
        return data

    return static_directory(portion, os.path.join(descriptor, portion), root)


def static_file(portion, descriptor, root="."):
    """Handle static file request from a descriptor
    in a safe fashion (removing '..', canonicalizing,
    &c. Analogous to Bottle's `static_file`
    """
    portion = portion.replace("../", "")
    tpath = os.path.join(root, portion)
    if os.path.isfile(tpath):
        fh = file(tpath)
        data = fh.read()
        fh.close()
        return data

    raise GopherError("Descriptor is not a file")


def static_directory(directory, descriptor, root='.', unknowns_as='5'):
    """Create a `Directory` object from a file system
    directory; Meant to simplify the process of having
    standard directories to load data from, &c.
    """
    retd = Directory(directory)
    if directory[0] == "/":
        directory = directory[1:]

    directory = directory.replace("../", "")

    rpath = os.path.join(os.path.abspath(root), directory)
    items = os.listdir(os.path.join(os.path.abspath(root), directory))

    for item in items:
        tdesc = os.path.join(descriptor, item)
        tpath = os.path.join(rpath, item)

        if os.path.isfile(tpath):
            tmp = os.path.splitext(item)
            if len(tmp) == 0:
                retd.add_child([unknowns_as,
                                tdesc,
                                item])
            elif tmp[1] in text_types:
                retd.add_text(item, tdesc)
            elif tmp[1] == ".html":
                retd.add_html(item, tdesc)
            else:
                retd.add_binary(item, tdesc)

        else:
            retd.add_directory(item, tdesc)

    return retd

#class ChashaAsync(Chasha, asyncore.dispatcher)
