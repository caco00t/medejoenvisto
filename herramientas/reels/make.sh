#!/bin/bash
# Crea un reel 1080x1920 a partir de un HTML animado con render(t).
# uso: ./make.sh nombre duracion estilo_audio "efectos"
#   estilo_audio: musicbox | beat | beat-soft | lofi | tick
#   efectos: lista separada por comas tipo pop:3.2,ding:5,whoosh:6,boom:7,tap:8,buzz:9
set -e
cd "$(dirname "$0")"
N=$1; D=$2; A=$3; S=$4
mkdir -p out
python3 render.py $N.html fr_$N all $D
python3 audio.py $A $D $N.wav "$S"
ffmpeg -y -loglevel error -framerate 30 -i fr_$N/f_%04d.jpg -i $N.wav -c:v libx264 -preset veryfast -crf 19 -pix_fmt yuv420p -c:a aac -b:a 160k -shortest -movflags +faststart out/$N.mp4
rm -rf fr_$N $N.wav
echo "listo: out/$N.mp4"
