import json, subprocess

def run_as_python3(module, options):
  out = subprocess.check_output(['python3', 'runas3.py', module, json.dumps(options)])
  print(out)
  return out
