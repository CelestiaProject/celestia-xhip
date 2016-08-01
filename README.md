Celestia-XHIP
=============

About Celestia XHIP
-------------------
This project contains Python scripts to parse the XHIP catalogue for use with
Celestia/Celestia.Sci. At present it only generates the binary file, the text
version (stars.txt) is not supported.

Python 3 is not supported.

Required packages
-----------------
* PLY
* Astropy
* Numpy

Operation
---------
Download the XHIP data from ftp://cdsarc.u-strasbg.fr/pub/cats/V/137D/ - the
following files are required:

* ReadMe
* main.dat
* photo.dat

Note that the main.dat and photo.dat files must be extracted from the .gz
archives. These files must be placed in the same directory as the Python
scripts. Then simply run

```bash
python buildstardb.py
```

After a short while the stars.dat file is created. This can then be copied
into the data directory of the Celestia installation.

License
-------
Copyright (C) 2016  Andrew Tribick

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
