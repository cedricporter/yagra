#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Hua Liang[Stupid ET] <et@everet.org>
#
import MySQLdb

db = MySQLdb.connect(host="localhost",
                     user="yagra",
                     passwd="yagra_p@$$w0rd",
                     db="yagra",
                     charset="utf8")


def random_string(length=10):
    import random
    import string

    return "".join(random.choice(string.letters) for i in xrange(length))


def test_insert():
    import pprint
    import time

    c = db.cursor()
    c.execute("""
    INSERT INTO `yagra`.`yagra_user`
    (
    `user_login`,
    `user_passwd`,
    `display_name`,
    `user_email`,
    `user_register`,
    `user_status`)
    VALUES
    (%s, %s, %s, %s, %s, %s)
    """, (random_string(), "p@$$w0rd", "Cedric Porter",
          random_string() + "@gmail.com",
           time.strftime('%Y-%m-%d %H:%M:%S'), str(1)))
    db.commit()
    c.execute("SELECT * FROM yagra_user")
    pprint.pprint(c.fetchall())

    c.close()
    db.close()


def main():
    test_insert()

if __name__ == '__main__':
    main()
