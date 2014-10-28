# Overview

чаша means "cup" in Bulgarian, and is a play on the larger Python Web Frameworks such as Bottle and Flask. However, instead of targetting the WWW, Chasha 
targets the Gopher protocol; it includes simple classes for handling Routes, Directories, Images & the like.

# Rationale

 Why not? We have Lamson for route-oriented SMTP, and Bottle/Flask/... for Web, may as well have one (or more!) for Gopher.

 Addtionally, this allows me to create a non-Digamma reference implementation for some extensions I was thinking of for Gopher+

# Example

 The repository contains several example files, but the simplest example is the following:

    from chasha import Chasha, Document


    app = Chasha()


    @app.route('/test/<bar:int>')
    def test(bar):
        return "bar is {0}".format(bar)


    @app.default()
    def main():
        d = Directory()
        d.add_child("Information lines are simply text in directories")
        d.add_child("atm, multiline must be manually split")
        d.add_child([0, 'Test 10', '/test/10', '127.0.0.1', '7070'])
        d.add_child([0, 'Test 20', '/test/20', '127.0.0.1', '7070'])
        d.add_child("And of course, you can mix info, links, &c.")

    app.run()

# Protocol Support

 Currently support:

- descriptors
- Directories & Info lines naturally, all others manually
- search strings

## Planned Support

- full Gopher RFC
- Gopher+ draft
- Extensions as a "Gopher\*" protocol

# To Do

 The biggest thing I'd like to do is reduce the amount of manual work that has to be done in directories. A helper method
in the `Chasha` object, such as `Chasha#make_link` or even on the `Directory` class, to reduce the need for manual lists.
(Actually, thinking about it, I like it on the `Directory` class more...). `Directory#add_URL`, `#add_image`, `#add_directory`
all make it a bit easier, without having to add multiple classes.
