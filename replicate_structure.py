import shutil
import os
import json

def ignore_files(src, names):
    # Return a list of all names that are NOT directories (i.e. ignore all files)
    ignored = []
    for name in names:
        path = os.path.join(src, name)
        if not os.path.isdir(path):
            ignored.append(name)
    return ignored

src_dir = 'data/2023'
dst_dir = 'data/2024'

if not os.path.exists(src_dir):
    print(f"Source directory {src_dir} does not exist.")
    exit(1)

print(f"Replicating structure from {src_dir} to {dst_dir}...")
# dirs_exist_ok=True allows us to run this even if data/2024 exists (merging/overwriting structure)
# We ignore all files from source, so only directories are created/verified
shutil.copytree(src_dir, dst_dir, ignore=ignore_files, dirs_exist_ok=True)

print(f"Creating empty data.json and metadata.json in leaf directories of {dst_dir}...")
for root, dirs, files in os.walk(dst_dir):
    # If a directory has no subdirectories (dirs list is empty), it is a leaf node
    if not dirs:
        # Create empty data.json
        with open(os.path.join(root, 'data.json'), 'w') as f:
            json.dump({}, f)
        
        # Create empty metadata.json
        with open(os.path.join(root, 'metadata.json'), 'w') as f:
            json.dump({}, f)
    else:
        # Check if we need to clean up files if they were created by previous run in non-leaf
        # This is optional but good for idempotency if we are correcting a previous run
        data_json = os.path.join(root, 'data.json')
        meta_json = os.path.join(root, 'metadata.json')
        if os.path.exists(data_json):
            os.remove(data_json)
        if os.path.exists(meta_json):
            os.remove(meta_json)

print("Done.")
