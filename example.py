from chasha import Chasha, Directory

app = Chasha()


@app.route('/foo')
def foo():
    return """Test
Data
Check if multiline...
Works"""


@app.default()
def default():
    d = Directory()
    d.add_child([0, "Foo bar industries", "/foo", "localhost", "7070"])
    d.add_child("Some test info here...")
    d.add_child("Some more test info...")
    return d

app.run()
