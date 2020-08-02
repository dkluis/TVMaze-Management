'''
Try.py  Proof out the docopt library

Usage:
  try.py -d
  try.py -r
  try.py -f <show> <episode>
  try.py -h | --help
  try.py --version

Options:
  -h --help     Show this screen.
  -d            Download all outstanding Episodes
  -r            Review all newly detected Shows
  -f            Find download options for Show and Episode (Episode can also be a whole season - S01E05 or S01)
  --version     Show version.
'''

from docopt import docopt
import pprint;
args = docopt(__doc__)
# print(args)
print(f'Option -d was selected {args["-d"]}')
print(f'Option -r was selected {args["-r"]}')
print(f'Option -f was selected {args["-f"]}')

pprint.pprint(args)
