import finnemit
import sys
fname = sys.argv[1]
dct = finnemit.get_emissions(fname)
print()
for k,v in dct.items():
    print(', '.join([str(_) for _ in (k,v)]))

