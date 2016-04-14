import sys
import re

print(re.sub('(\S+)', '<span class="word">\\1</span>', sys.stdin.read()))
