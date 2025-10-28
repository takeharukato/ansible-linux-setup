set terminal pngcairo size 1280,720
set output OUTPNG
set title TITLE
set xlabel "value"
set ylabel "count"
set grid

binwidth = exists("BINW") ? BINW : 1.0
bin(x,width) = width*floor(x/width) + width/2.0

set boxwidth binwidth
set style fill solid 0.7
plot INFILE using (bin($1,binwidth)):(1.0) smooth freq with boxes title "histogram"

