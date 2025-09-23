# RGym
Rgym is a system to streamline patch and reproducer testing on the linux kernel.

## Setup
### Install Node
Install node 20, my preferred way is [nvm](https://github.com/nvm-sh/nvm).

`nvm install 20`

`nvm use 20`

### Clone and cd
`git clone https://github.com/karyeet/RGym`

`cd RGym`

### Install Dependencies
`npm i`

### Build RGym and container images
`npm run build`

### Download the root fs image and keys
[Download here (Google Drive)](https://drive.google.com/drive/folders/1eAzMR7bK4pKGy6V6Z8LEIZ0v07fWCVyW?usp=sharing)

`tar xvf syzkallerimage.tar.gz`

### Create a config.json
`touch ./config.json`

Use absolute paths,
Example:
```
{
    "data_path": "/home/ks/RGym/data",
    "rootfs_path": "/home/ks/RGym/syzkallerimage/bullseye.img",
    "sshkey_path": "/home/ks/RGym/syzkallerimage/bullseye.id_rsa",
    "docker_images": {
        "gcc-5": "karyeet/rgym:gcc-5",
        "gcc-6": "karyeet/rgym:gcc-6",
        "gcc-7": "karyeet/rgym:gcc-7",
        "gcc-8": "karyeet/rgym:gcc-8",
        "gcc-9": "karyeet/rgym:gcc-9",
        "gcc-10": "karyeet/rgym:gcc-10",
        "gcc-11": "karyeet/rgym:gcc-11",
        "gcc-12": "karyeet/rgym:gcc-12",
        "clang-9": "karyeet/rgym:clang-9",
        "clang-10": "karyeet/rgym:clang-10",
        "clang-11": "karyeet/rgym:clang-11",
        "clang-12": "karyeet/rgym:clang-12",
        "clang-13": "karyeet/rgym:clang-13",
        "clang-14": "karyeet/rgym:clang-14",
        "clang-15": "karyeet/rgym:clang-15",
        "clang-20": "karyeet/rgym:clang-20",
        "reproducer": "karyeet/rgym:reproducer"
    }
}
```
### Start
`npm run start`

If you want to leave it running in the background, use screen

`screen`

`npm run start`

Then hit `ctrl+a` `d`

## Usage (WIP)

### Jobs
Rgym comes with two jobs by default.

1. [Builder](https://github.com/karyeet/RGym/blob/main/Docker/build-kernel/setup.py)
2. [Reproducer](https://github.com/karyeet/RGym/blob/main/Docker/reproducer/setup.py)

Each job will produce exit codes shown in the file.

Please see [example.py](https://github.com/karyeet/RGym/blob/main/RCompose/example.py) for example usage. Note example.py is more verbose than needed, for example theres no need to run start twice, but we do it to show it will return false if the job is running.

Added jobs are not automatically started and must be started by a seperate call. RGym does no scheduling.

### Build Images
The **build images** are only built with some compilers by default, the following are built:
- clang 9 - 15, 20
- gcc 5 - 12

You may add more in the [gcc compose](https://github.com/karyeet/RGym/blob/main/Docker/gcc-images.yml) or the [clang compose](https://github.com/karyeet/RGym/blob/main/Docker/clang-images.yml) and run `sudo docker compose build`.

The images can be used outside of RGym by overriding the entrypoint. Ex:

`sudo docker run -it --rm --entrypoint=bash karyeet/rgym:clang-10`

### Compiler mapping
Some .configs do not have the compiler listed, for convenience a [mapping](https://github.com/karyeet/RGym/blob/main/RCompose/compiler_mapping.json) is provided based off syzbot, along with a script to generate it based off .configs. The mapping can be used and generated (even without RGym running) using the `pick_compiler_version` function in [rcompose.py](https://github.com/karyeet/RGym/blob/3f1956c2cf04bf0b2b1ac356c38df560b3ae6925/RCompose/rcompose.py#L116)


