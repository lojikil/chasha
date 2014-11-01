from chasha import Chasha, Directory

app = Chasha()


@app.route('/foo')
def foo():
    return """Test\r
Data\r
Check if multiline...\r
Works\r\n"""


@app.default()
def default():
    d = Directory("/")
    d.add_child([0, "Foo bar industries", "/foo", "127.0.0.1", "7070"])
    d.add_child("Some test info here...")
    d.add_child("Some more test info...")
    return d

app.run()
