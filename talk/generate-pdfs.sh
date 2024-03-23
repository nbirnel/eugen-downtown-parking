#!/bin/sh

sent="the-footprint-of-parking-in-downtown-eugene.sent"
slides=$(./count-sent-pages "$sent")

sent "$sent" &


x=2446
y=1020
w=1440
h=900

y_header=35

y=$(expr $y + $y_header)
h=$(expr $h - $y_header)

echo $x $y $w $h

window="$(xdotool search \
    --sync \
    --all \
    --onlyvisible \
    --name '^sent$' 
)"
echo $window
test -n "$window" || exit 1

mkdir -p tmp

for slide in $(seq -w $slides); do
    sleep .2
    scrot -a $x,$y,$w,$h tmp/$slide.jpg
    xdotool key --window $window key space
done

xdotool key --window $window key q

gm convert tmp/*.jpg deck.pdf
rm -rf tmp/
