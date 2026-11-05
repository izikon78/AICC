: t0 ( n -- ) ." Starting controller service for " 0 .r ."  runs" cr ;
: t1 ( a n -- ) swap ." Restarting controller service for run " 0 .r ."  of " 0 .r cr ;
: main ( n -- ) dup 0 max 0 ?do i 0= if dup t0 else i 1+ over t1 then loop drop ;
