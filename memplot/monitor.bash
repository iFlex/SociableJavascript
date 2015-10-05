while true; do
ps -C firefox -o pid=,%mem=,vsz= >> /tmp/mem.log
gnuplot /home/mlf/level4/memplot/plot.gnuplot
sleep 1
done
