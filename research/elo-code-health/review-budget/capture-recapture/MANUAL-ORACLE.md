# Independent tally of one source pair

The parent manually counted the first two `atm_nov` rows in the unchanged public source before receiving the parser's counts or estimator output. Study fault columns are numbered from 1 immediately after ID and P; trailing padding is excluded.

- Participant 1, perspective 1: reference faults {2, 3, 4, 5, 8, 13, 18, 21, 25}; count 9.
- Participant 2, perspective 1: reference faults {4, 8, 11, 16, 17, 21, 27}; count 7.
- Intersection {4, 8, 21}; overlap 3.
- Union size 9+7-3=13; declared reference count 29; remaining reference faults 16.
- Chapman estimated total (9+1)(7+1)/(3+1)-1=19.
- Estimated unseen 19-13=6; error relative to remaining reference faults is -10, or -62.5%.

This pair is an arithmetic and parsing oracle. It is not representative sampling, a stopping recommendation, or proof that the study reference list contains every natural defect.

Source SHA256: `696c9397d1213da986db451ab83c369e328e46d6d22afd9091c2ea066faffbcd`. Source rows inspected 2026-11-17; no source program was executed.
