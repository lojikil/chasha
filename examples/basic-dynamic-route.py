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
    return "bar is {0}".format(bar)


@app.default()
def default():
    d = Directory("/")
    d.add_child("Dynamic routing example; /blah/ accepts an integer")
    d.add_child([0, "Foo bar industries", "/foo", "127.0.0.1", "7070"])
    d.add_child("Some test info here...")
    d.add_child("Some more test info...")
    d.add_child(Directory("/bar", port=7070, name="FooBar Testing"))
    d.add_child([0, "Test blah 10", "/blah/10", "127.0.0.1", "7070"])
    d.add_child([0, "Test blah 20", "/blah/20", "127.0.0.1", "7070"])
    d.add_child([0, "Test blab 30", "/blah/30", "127.0.0.1", "7070"])
    return d

app.run()
