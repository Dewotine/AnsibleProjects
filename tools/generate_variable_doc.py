#!/usr/bin/python
# -*- coding: utf-8 -*-

import getopt
import sys
import yaml
import six


def usage():
    print("Usage: generate_variable_doc.py -r <rolename>")
    sys.exit(0)

if __name__ == '__main__':
    rolename = None
    opts, args = getopt.getopt(sys.argv[1:], "r:h")
    for o, a in opts:
        if o == "-r":
            rolename = a
        elif o == "-h":
            usage()

    if rolename is None:
        usage()

    role_defaults = {}
    metas = {}
    defaults_file = "roles/%s/defaults/main.yml" % rolename
    meta_file = "roles/%s/meta/main.yml" % rolename
    try:
        with open(defaults_file, 'r') as stream:
            role_defaults = yaml.load(stream)

    except IOError as e:
        print("Unable to read file %s" % defaults_file)
        sys.exit(1)

    print("""# Role: %s

## Parameters
""" % rolename)

    if role_defaults is not None:
        print ("""| Variable | Type | Description | Default |
| --- | --- | --- | --- |""")
        for k, v in six.iteritems(role_defaults):
            vp = v
            # Lower case v when it's a bool
            if type(v).__name__ == "bool":
                vp = str(v).lower()

            print("| __%s__ | %s | | %s |" % (k.replace("_", "\_"), type(v).__name__, vp))
    else:
        print ("This role doesn't use any parameter.")

    try:
        with open(meta_file, 'r') as stream:
            metas = yaml.load(stream)
    except IOError as e:
        pass

    if "dependencies" in metas:
        print("\n## Dependencies\n")
        for d in metas["dependencies"]:
            print("  * %s" % d)

    print("\n## Examples")


