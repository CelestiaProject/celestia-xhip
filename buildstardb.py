#!/usr/bin/python

# buildstardb.py: Parse the XHIP catalogue for Celestia
# Copyright (C) 2016  Andrew Tribick
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA  02110-1301, USA.

from __future__ import print_function
from __future__ import division
from builtins import range

import struct

from astropy import table
from astropy.io import ascii
from specparse import SpecParser
from specinfo import CelestiaSpectrum

import numpy as np
from numpy import cos,log10,radians,sin

OBLIQUITY = radians(23.4392911)
LY_PER_PC = 3.26167

ROTMATRIX = np.matrix((
    (1, 0, 0),
    (0, cos(OBLIQUITY), sin(OBLIQUITY)),
    (0, -sin(OBLIQUITY), cos(OBLIQUITY))
))

maindata = ascii.read("main.dat", readme="ReadMe")
photdata = ascii.read("photo.dat", readme="ReadMe")

alldata = table.join(maindata, photdata, keys='HIP')

used_dist = 0
used_plx = 0
skipped = 0

parser = SpecParser()

packed_stars = []

for i in range(len(alldata)):
    if not alldata['SpType'].mask[i]:
        sptype = CelestiaSpectrum.create(parser.parse(alldata['SpType'][i]))
    else:
        sptype = CelestiaSpectrum()
    
    RArad = radians(alldata['RAdeg'][i])
    DErad = radians(alldata['DEdeg'][i])
    
    if alldata['Vmag'].mask[i]:
        skipped += 1
        continue
    
    if not alldata['Dist'].mask[i]:
        used_dist += 1
        distance = alldata['Dist'][i]
    elif alldata['e_Plx'][i] < alldata['Plx'][i]:
        used_plx += 1
        distance = 1000 / alldata['Plx'][i]
    else:
        skipped += 1
        continue
    
    absmag = alldata['Vmag'][i] - 5*(log10(distance)-1)
    
    distance *= LY_PER_PC
    
    vector = np.matrix((
        (distance*cos(RArad)*cos(DErad),),
        (distance*sin(DErad),),
        (-distance*sin(RArad)*cos(DErad),)
    ))
    
    ecliptic = ROTMATRIX*vector
    
    packed_stars.append(struct.pack('<l3fhH',
                                    alldata['HIP'][i],
                                    ecliptic.item(0),
                                    ecliptic.item(1),
                                    ecliptic.item(2),
                                    int(round(absmag*256)),
                                    sptype.code))

print("Found", len(packed_stars))
print("Used dist for", used_dist)
print("Used plx for", used_plx)
print("Skipped", skipped)

with open('stars.dat', 'wb') as f:
    f.write(struct.pack('<8sHL', 'CELSTARS', 0x0100, len(packed_stars)))
    for packed_star in packed_stars:
        f.write(packed_star)