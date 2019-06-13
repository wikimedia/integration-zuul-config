#!/usr/bin/env python3
"""
Edit MediaWiki's PHPUnit suite.xml file
Copyright (C) 2018 Kunal Mehta <legoktm@member.fsf.org>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""

import argparse
import xml.etree.cElementTree as etree


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('suite', help='Path to suite.xml')
    parser.add_argument('--cover-extension',
                        help='Extension path to set for coverage')

    args = parser.parse_args()
    tree = etree.parse(args.suite)
    root = tree.getroot()
    for child in root.getchildren():
        if child.tag == 'filter':
            whitelist = child.getchildren()[0]
            assert whitelist.tag == 'whitelist'
            # Remove the current directories that are there,
            # we don't want to include any of them
            for wchild in whitelist.getchildren():
                whitelist.remove(wchild)
            # Add the three directories we care about
            for folder in ['src', 'includes', 'maintenance']:
                sub = etree.SubElement(whitelist, 'directory')
                sub.text = '../../extensions/%s/%s' \
                           % (args.cover_extension, folder)
                sub.set('suffix', '.php')

    # This produces a dirty diff, strips comments, ignores newlines,
    # and so on, but no human should ever read it, hopefully.
    tree.write(args.suite)


if __name__ == '__main__':
    main()
