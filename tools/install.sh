#!/bin/sh

if [ $# -ne 2 ]; then
    echo "Usage: tools/install.sh <os> <version>"
    exit 1
fi

os=${1}
version=${2}
target=""

if [ "${os}" = "mac" ]; then
    addon_dir="${HOME}/Library/Application Support/Blender/${version}/scripts/addons"
    mkdir -p "${addon_dir}"
    target="${addon_dir}/blender_mqo"
elif [ "${os}" = "linux" ]; then
    addon_dir="${HOME}/.config/blender/${version}/scripts/addons"
    mkdir -p "${addon_dir}"
    target="${addon_dir}/blender_mqo"
else
    echo "Invalid operating system."
    exit 1
fi

rm -rf "${target}"
cp -r src/blender_mqo "${target}"
