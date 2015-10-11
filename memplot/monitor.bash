rm /tmp/mem.log
while true; do
ps -C v8wrapper.bin -o pid=,%mem=,vsz= >> /tmp/mem.log
gnuplot ~/level4/SociableJavascript/memplot/plot.gnuplot
sleep 1
done
