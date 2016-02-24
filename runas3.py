from sys import argv
import json, importlib

if len(argv) == 3:
  print('python3')
  module = importlib.import_module('engine.plugins.' + argv[1])
  print(argv[2])
  print(module.run(json.loads(argv[2])))
