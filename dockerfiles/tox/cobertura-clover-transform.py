#!/usr/bin/env python3
"""
https://github.com/cwacek/cobertura-clover-transform

Copyright (c) 2014 Chris W

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


import lxml.etree as ET
import argparse
import os


def convert(inxml):
    dom = ET.parse(inxml)
    xslt = ET.parse(os.path.join(os.path.dirname(__file__),
                                 'cobertura-clover-transform.xslt'))

    transform = ET.XSLT(xslt)
    newdom = transform(dom)
    return ET.tostring(newdom, pretty_print=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('coverage_xml')
    parser.add_argument('-o', '--output', required=False)
    args = parser.parse_args()

    converted = convert(args.coverage_xml)

    if args.output:
        with open(args.output, 'w') as out:
            out.write(converted.decode())
    else:
        print(converted)


if __name__ == '__main__':
    main()
