from chasha import Chasha, Directory

app = Chasha()


@app.route('/foo')
def foo():
    return """Test\r
Data\r
Check if multiline...\r
Works\r\n"""


@app.route('/bar')
def bar():
    d = Directory("/bar")
    d.add_child("This is an empty directory")
    d.add_child("it exists simply to illustrate & test nested directories")
    d.add_child("and further, it is just neat")
    return d


@app.route('/blah/<bar:int>')
def blah(bar):
    ret = """
bar is {0}\r
descriptor is {1}\r
search is {2}\r\n""".format(bar, app.request.descriptor, app.request.search)
    return ret


@app.default()
def default():
    d = Directory("/")
    d.add_child("Dynamic routing example; /blah/ accepts an integer")
    d.add_child([0, "Foo bar industries", "/foo", "127.0.0.1", "7070"])
    d.add_child("Some test info here...")
    d.add_child("Some more test info...")
    d.add_directory("FooBar Testing","/bar")
    d.add_child([0, "Test blah 10", "/blah/10", "127.0.0.1", "7070"])
    d.add_child([0, "Test blah 20", "/blah/20", "127.0.0.1", "7070"])
    d.add_text("Test blab 30", "/blah/30")
    return d

app.run()
