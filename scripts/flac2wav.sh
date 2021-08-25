#!/bin/bash

function flacToWav(){
  echo $1
  ext=${1##*.}
  echo $ext
  if [ $ext = 'flac' ]
  then
    #echo "True"
    filename=$(basename $1 .flac)
    echo $filename
    sox $1 -c 1 -r 8000 -b 16 ${filename}.wav
    rm -rf $1
  fi
}

function travFolder(){
  echo $1
  flist=`ls $1`
  cd $1
  #echo $flist
  for f in $flist
  do
    if test -d $f
    then
      travFolder $f
    else
      flacToWav $f
    fi
  done
  cd ../
}
travFolder $1
