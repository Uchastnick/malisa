import os, sys

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path: sys.path.append(base_dir)
