#!/bin/bash


#echo $0

full_path=$(readlink -f  $0)
#echo $full_path

dir_path=$(dirname $full_path)
#echo $dir_path

ScriptPath="$dir_path/lib/restRequest.py"
LogPath="$dir_path/log"

python "$ScriptPath" "$LogPath"
