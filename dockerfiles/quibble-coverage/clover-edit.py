#!/usr/bin/env python3
"""
Edit clover.xml files
Copyright (C) 2017 Kunal Mehta <legoktm@member.fsf.org>

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
    parser.add_argument('clover', help='Path to clover.xml')
    parser.add_argument('--name', help='Set name in <project> element')
    parser.add_argument('--remove-full-info',
                        help='Remove full coverage information, '
                             'leaving cumulative metrics',
                        action='store_true')
    parser.add_argument('--save', help='Location to save to, '
                                       'otherwise will overrite clover.xml')
    args = parser.parse_args()
    tree = etree.parse(args.clover)
    root = tree.getroot()
    project = root.getchildren()[0]
    assert project.tag == 'project'
    if args.remove_full_info:
        for child in project.getchildren():
            # All we want to keep is the final <metrics> tag
            if child.tag != 'metrics':
                project.remove(child)
    if args.name:
        project.set('name', args.name)
    save = args.save or args.clover
    tree.write(save)


if __name__ == '__main__':
    main()
