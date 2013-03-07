#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Hua Liang[Stupid ET] <et@everet.org>
#

"""
这是一个神奇的模板引擎，我叫它Lion，使用了Python的黑魔法，模仿Lisp的html生成。

你没看错，Lion就是那么短！

为什么有这个呢？因为作业不能用其他库，所以只能自己写，要不然就用jinja了。

穷则思变，就变出了Lion。
"""

from string import Template
from util import flatten


t = Template("""
def $tag(*args, **kwargs):

    prefix = "<$tag "
    for k, v in kwargs.iteritems():
        prefix += '%s="%s" ' % (k, str(v))
    prefix += ">"

    string = prefix + "".join(flatten(args)) + "</$tag>"

    return string
""")

for tag in ["html", "head", "body", "title",
            "script", "form", "input", "div",
            "img", "p", "strong", "br", "ul",
            "li", "dd", "dt", "dl", "a",
            ] + ["h%d" % i for i in xrange(6)]:
    func = t.substitute(tag=tag)
    exec(func)


def test():
    string = html(
        head(title("Lion"),
            ),
        body(h1("Welcome"),
             [a("Link %d" % i, href="/") for i in xrange(10)],
            ))

    print string


if __name__ == '__main__':
    test()
