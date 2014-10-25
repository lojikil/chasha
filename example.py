from chasha import Chasha

app = Chasha()

@app.route('foo/')
def foo():
    return """Test
Data
Check if multiline...
Works"""


@app.default()
def default():
    return """0Foo\t/foo/\t{0} {1}\t+\r
iSome test info here...\tfake\tfake\t0\r
iSome more test info...\tfake\tfake\t0\r
"""

app.run()
