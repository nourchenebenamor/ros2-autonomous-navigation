#!/usr/bin/env python3

import argparse
import random
from pathlib import Path
from xml.etree import ElementTree as ET

ROOM = 10.0
DOOR = 2.0
HEIGHT = 2.0
THICKNESS = 0.5


def add_wall(model, name, x, y, yaw, length):
    link = ET.SubElement(model, 'link', name=name)
    ET.SubElement(link, 'pose').text = f'{x:.5f} {y:.5f} {HEIGHT/2:.5f} 0 0 {yaw:.9f}'
    for kind in ('visual', 'collision'):
        element = ET.SubElement(link, kind, name=f'{name}_{kind}')
        geom = ET.SubElement(element, 'geometry')
        box = ET.SubElement(geom, 'box')
        ET.SubElement(box, 'size').text = f'{THICKNESS} {length:.5f} {HEIGHT}'
        if kind == 'visual':
            mat = ET.SubElement(element, 'material')
            ET.SubElement(mat, 'ambient').text = '0 0.8 0.8 1'
            ET.SubElement(mat, 'diffuse').text = '0 0.8 0.8 1'


def generate(side, offset, output):
    if side not in ('east', 'west', 'north', 'south'):
        raise ValueError('Invalid side')
    if abs(offset) > 2.5:
        raise ValueError('Offset must be between -2.5 and +2.5 m')

    root = ET.Element('sdf', version='1.9')
    model = ET.SubElement(root, 'model', name='tp3_room')
    ET.SubElement(model, 'static').text = 'true'

    for direction in ('east', 'north', 'west', 'south'):
        # Wall tangent coordinate t increases along Y for E/W, along X for N/S.
        if direction != side:
            intervals = [(-ROOM/2, ROOM/2)]
        else:
            intervals = [(-ROOM/2, offset - DOOR/2),
                         (offset + DOOR/2, ROOM/2)]

        for i, (start, end) in enumerate(intervals):
            mid = (start + end) / 2
            length = end - start
            if direction == 'east':
                x, y, yaw = ROOM/2, mid, 0.0
            elif direction == 'west':
                x, y, yaw = -ROOM/2, mid, 0.0
            elif direction == 'north':
                x, y, yaw = mid, ROOM/2, 1.5707963267948966
            else:
                x, y, yaw = mid, -ROOM/2, 1.5707963267948966
            add_wall(model, f'{direction}_{i}', x, y, yaw, length)

    tree = ET.ElementTree(root)
    ET.indent(tree, space='  ')
    tree.write(output, encoding='utf-8', xml_declaration=True)
    print(f'Created {output}; door={side}, offset={offset:.2f}m, width=2m')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--side', choices=['east', 'west', 'north', 'south'], default='east')
    parser.add_argument('--offset', type=float, default=0.0)
    parser.add_argument('--random', action='store_true', help='Choose side and offset randomly')
    parser.add_argument('--seed', type=int, default=None)
    args = parser.parse_args()
    if args.random:
        rng = random.Random(args.seed)
        args.side = rng.choice(['east', 'north', 'west', 'south'])
        args.offset = rng.uniform(-2.5, 2.5)
    generate(args.side, args.offset, Path(__file__).with_name('tp3_room.sdf'))
