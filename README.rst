pyxmahjongg
===========

python rewrite of the original xmahjongg-game from 1989:

https://www.lcdf.org/xmahjongg/

The python implementation does not need the X11 files anymore, however the name is still 'pyxmahjongg'.


Run the program
---------------

    python pyxmahjongg.py -h

Use the optional -h flag for help to change colors and layouts.


Requirements
------------

Requires 'pillow' for image-handling.

'pyxmahjongg' is developed with Python 3.6 and and pillow 4.0.0 and not tested with earlier versions.


Remarks
-------

This implementation uses the same layout-files as the original one but just the dorothys tileset. Excerpt from the original documentation:

The default tileset was originally created in color by Dorothy Robinson <mokuren@teleport.com> with Mark A. Holm <markh@aracnet.com>. The publically available version was in black-and-white. Holm copyrighted the tiles in 1988, giving permission to copy and distribute for non-profit purposes. The significantly altered color version that comes with xmahjongg was created by Eddie Kohler in later years.


License
-------

Because of the original license it is permitted to use the tileset for non-profit purposes. As a consequence any commercial uses of this program and the used tileset is prohibited. Furthermore the usage of this program is entirely at your own risk.
