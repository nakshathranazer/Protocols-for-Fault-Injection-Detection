from pathlib import Path
import site

myPackagePath = Path(__file__).parent.absolute()

pathspec = r"""
# Generated by GST's installer (install_GST.py)
# In the lines below, list the paths where Python should look for
# GateSetTomography-supplied modules, one directory per line.
#
# If a directory does not exist when Python is started, it will be ignored.
%s
""" % myPackagePath

print("Adding path:", myPackagePath)

usp = Path(site.getusersitepackages())
usp.mkdir(parents=True, exist_ok=True)
uspfile = usp / 'GST.pth'
with open(uspfile, 'w') as f:
    f.write(pathspec)
    print('Wrote to {}'.format(uspfile))

print("GST package installed successfully!")
