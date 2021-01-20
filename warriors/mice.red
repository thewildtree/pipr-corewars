;name MICE
;name Mice
MOV.AB #12, $-1
MOV.I  @-2, <5
DJN.B  $-1, $-3
SPL.B  @3, $0
ADD.AB #65, $2
JMZ.B  $-5, $-6
DAT.F  #0, #833