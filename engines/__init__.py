from os      import listdir, path
from os.path import isfile,  dirname

all_  = {}
pairs = {}

exclude       = ['base.py']
mypath        = dirname(__file__)
files         = [f for f in listdir(mypath) if isfile(path.join(mypath, f))]
files         = [f for f in files if f not in exclude]
modules_names = [ n[:-3] for n in files if n[-3:] =='.py' and n[:1]!='_']

del listdir, path, isfile, dirname, mypath, files, exclude

for name in modules_names:
    locals()[name] = __import__(f'engines.{name}', globals(), locals(),
                                ['command'], 0).Engine

    all_[name] = locals()[name]

    if all_[name].convert not in pairs:
        pairs[all_[name].convert] = {}
    pairs[all_[name].convert][name] = all_[name]

del name, modules_names
