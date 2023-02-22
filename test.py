
import os
import zipfile as zp

from pathlib import Path

print(Path('archive/phm/postprocessing/surfdeg.png').stem)

a = 'archive/phm/postprocessing/surfdeg.png'.split('/')
a[-1] = a[-1].split('.')[0]

print('.'.join(a[1:]))