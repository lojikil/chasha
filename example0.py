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


@app.default()
def default():
    d = Directory("/")
    d.add_child([0, "Foo bar industries", "/foo", "127.0.0.1", "7070"])
    d.add_child("Some test info here...")
    d.add_child("Some more test info...")
    d.add_child(Directory("/bar", port=7070, name="FooBar Testing"))
    return d

app.run()
