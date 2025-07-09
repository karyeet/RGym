"""
Generate a dict giving compiler versions used per kernel version.
"""
import rcompose
import os
import json


kernel_configs_dir = "../configs"
mapping = rcompose.generate_compiler_mapping(kernel_configs_dir)

json.dump(mapping, open('compiler_mapping.json', 'w'))
print()

# usage example
mapping = json.load(open('compiler_mapping.json', 'r'))
suggested_compiler_version = rcompose.pick_compiler_version("5.10.100", mapping)
print(f"Suggested compiler version for 5.10.100: {suggested_compiler_version}")