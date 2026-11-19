#include <iostream.h>
#include <string.h>
#include <assert.h>

/***********************************************************************/
/**                                                                   **/
/**                   General constants and types                     **/
/**                                                                   **/
/***********************************************************************/

const int MAX_COL  = 35;
const int INCR     =  1;
const int DECR     =  0;

typedef int scores[MAX_COL];


/***********************************************************************/
/**                                                                   **/
/**                ATM data for the two replications                  **/
/**                                                                   **/
/***********************************************************************/

/* ATM constants for the two replications */

const int ATM_NOV_ERR  =  29;
const int ATM_NOV      =  12;

const int ATM_JUN_ERR  =  29;
const int ATM_JUN      =  14;

/* ATM scores for NOV replication */

scores atm_nov[ATM_NOV] =            // All data arrays are padded with 0
{/*
ID  P  1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 
----------------------------------------------------------------*/
1,  1, 0,1,1,1,1,0,0,1,0,0,0,0,1,0,0,0,0,1,0,0,1,0,0,0,1,0,0,0,0, 0,0,0,0,
2,  1, 0,0,0,1,0,0,0,1,0,0,1,0,0,0,0,1,1,0,0,0,1,0,0,0,0,0,1,0,0, 0,0,0,0,
3,  0, 0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, 0,0,0,0,
4,  0, 0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,1,0,0,1,0,0,0,0,0,0,0,0,0,0, 0,0,0,0,
6,  2, 0,1,1,0,1,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0, 0,0,0,0,
7,  2, 0,0,1,1,1,0,0,1,0,1,0,0,0,0,0,1,1,0,1,1,1,0,1,1,0,0,0,1,0, 0,0,0,0,
8,  0, 0,0,0,1,0,0,1,0,0,0,0,0,0,0,0,1,1,0,1,0,0,0,1,1,0,0,1,0,0, 0,0,0,0,
9,  0, 0,1,0,1,1,0,0,1,0,0,1,0,0,0,1,0,0,0,0,0,1,1,1,0,1,0,1,0,0, 0,0,0,0,
11, 3, 1,1,0,1,0,0,1,0,0,0,1,0,0,0,0,1,0,0,1,0,0,0,0,0,0,0,1,0,1, 0,0,0,0,
12, 3, 0,0,0,1,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,1,0,0, 0,0,0,0,
13, 0, 0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1, 0,0,0,0,
14, 0, 0,0,1,1,1,0,0,0,0,0,1,0,0,0,0,1,0,0,1,1,0,0,1,0,0,0,0,0,1, 0,0,0,0
};

/* ATM scores for JUN replication */

scores atm_jun[ATM_JUN] = 
{/*
ID  P  1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 
----------------------------------------------------------------*/
1,  0, 0,0,0,1,0,0,0,0,0,0,1,0,0,0,0,1,0,0,1,0,0,0,0,0,0,0,0,0,0, 0,0,0,0,
2,  0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,1,0,0,0,0,0,0,0,0,0,0, 0,0,0,0,
3,  0, 0,0,0,1,0,1,0,0,0,1,1,0,0,0,0,1,1,0,1,1,0,0,0,0,0,0,0,0,0, 0,0,0,0,
4,  1, 0,0,0,1,0,0,1,0,0,0,0,0,0,0,0,1,1,0,1,1,0,0,0,0,0,0,0,1,0, 0,0,0,0,
5,  2, 1,1,1,1,0,1,1,1,1,0,1,0,0,0,1,0,1,1,0,1,0,0,1,0,0,1,0,0,0, 0,0,0,0,
6,  3, 0,1,0,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,0,0,0,0,1,0,0,0,1,0,1, 0,0,0,0,
7,  0, 1,0,0,1,1,1,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,1,0,0,1, 0,0,0,0,
8,  0, 0,0,0,1,0,0,0,1,0,0,1,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0, 0,0,0,0,
9,  0, 0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1,1,0, 0,0,0,0,
10, 1, 0,0,1,1,1,0,1,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0, 0,0,0,0,
11, 2, 0,1,1,1,0,1,0,1,0,0,1,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,1,0,0, 0,0,0,0,
12, 3, 0,1,1,1,0,0,1,0,0,1,0,0,0,0,0,1,0,0,1,0,0,0,0,0,0,1,0,0,1, 0,0,0,0,
13, 0, 1,1,0,1,0,0,1,1,0,1,0,0,0,0,1,1,0,1,0,0,0,0,0,1,0,0,0,0,0, 0,0,0,0,
14, 0, 1,0,0,1,1,0,1,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1, 0,0,0,0
};


/***********************************************************************/
/**                                                                   **/
/**                 PG data for the two replications                  **/
/**                                                                   **/
/***********************************************************************/

/* PG constants for the two replications */

const int PG_NOV_ERR   =  27;
const int PG_NOV       =  12;

const int PG_JUN_ERR   =  27;
const int PG_JUN       =  14;

/* PG scores for NOV replication */

scores pg_nov[PG_NOV] = 
{/*
ID  P  1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 
------------------------------------------------------------*/
1,  0, 0,1,0,0,0,0,0,0,0,0,1,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,
2,  0, 0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,
3,  1, 0,1,0,0,1,0,0,0,0,0,0,0,0,0,0,1,0,0,1,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,
4,  1, 0,1,0,0,1,1,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0, 0,0,0,0,0,0,
6,  0, 0,1,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,1,0,0,0,0,0,0,1,0, 0,0,0,0,0,0,
7,  0, 0,1,0,1,0,0,1,1,0,0,0,1,0,1,1,0,0,0,0,0,0,0,0,0,0,1,0, 0,0,0,0,0,0,
8,  2, 0,1,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,
9,  2, 0,0,0,0,0,1,0,0,1,1,0,0,0,0,1,0,0,0,1,0,0,0,0,1,0,0,0, 0,0,0,0,0,0,
11, 0, 0,1,0,1,0,0,0,0,0,1,1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,
12, 0, 0,1,0,0,1,1,0,0,1,0,1,0,1,1,0,0,0,1,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,
13, 3, 1,1,1,0,0,1,0,0,1,0,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,0,0, 0,0,0,0,0,0,
14, 3, 0,1,0,0,1,0,1,0,0,1,1,0,1,0,0,0,1,0,0,0,0,0,1,0,0,0,0, 0,0,0,0,0,0
};

/* PG scores for JUN replication */

scores pg_jun[PG_JUN] = 
{/*
ID  P  1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 
----------------------------------------------------------------*/
1,  1, 0,0,0,0,0,1,0,0,1,1,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,
2,  2, 1,1,0,0,0,0,0,0,0,1,0,0,0,1,1,0,0,0,1,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,
3,  3, 0,1,1,0,1,1,0,0,1,1,0,1,0,1,0,0,0,1,0,0,0,0,0,0,0,0,1, 0,0,0,0,0,0,
4,  0, 0,1,1,0,1,1,0,0,1,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,
5,  0, 1,1,0,1,1,1,0,0,1,1,1,1,1,1,1,0,1,1,0,0,1,0,0,0,1,0,0, 0,0,0,0,0,0,
6,  0, 0,1,0,1,0,0,0,0,1,0,0,0,0,1,1,0,0,0,0,1,1,1,0,0,0,1,0, 0,0,0,0,0,0,
7,  1, 0,1,0,1,1,0,1,0,1,0,1,0,1,0,1,1,1,1,0,0,1,0,0,0,0,0,1, 0,0,0,0,0,0,
8,  2, 0,1,0,0,1,0,0,1,1,1,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,
9,  3, 0,1,1,0,1,1,0,0,1,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,
10, 0, 0,0,0,0,1,0,0,0,0,0,1,1,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,
11, 0, 0,0,0,1,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,1,0,0,0,0,0, 0,0,0,0,0,0,
12, 0, 0,1,0,0,1,0,1,0,1,0,1,0,1,0,1,0,0,0,0,0,0,0,0,0,0,1,0, 0,0,0,0,0,0,
13, 1, 1,0,0,1,0,0,1,0,1,0,1,1,0,1,1,0,0,1,1,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,
14, 2, 0,0,1,0,1,1,0,1,0,0,1,0,0,1,0,1,1,0,0,0,0,1,1,0,0,1,0, 0,0,0,0,0,0
};


/***********************************************************************/
/**                                                                   **/
/**               NASA A data for the two replications                **/
/**                                                                   **/
/***********************************************************************/

/* NASA A constants for the two replications */

const int A_NOV_ERR   =  18;
const int A_NOV       =  12;

const int A_JUN_ERR   =  15;
const int A_JUN       =  13;

/* NASA A scores for NOV replication */

scores a_nov[A_NOV] = 
{/*
ID  P  1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8
------------------------------------------*/
1,  1, 0,1,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, 
2,  1, 1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
3,  0, 0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
4,  0, 1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
6,  2, 0,1,0,1,0,0,0,0,0,0,1,0,1,1,0,0,0,0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
7,  2, 1,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
8,  0, 1,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
9,  0, 1,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
11, 3, 1,0,0,1,0,0,0,0,0,0,0,0,0,1,0,0,0,0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
12, 3, 0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
13, 0, 0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
14, 0, 1,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
};

/* NASA A scores for JUN replication */

scores a_jun[A_JUN] = 
{/*
ID  P  1 2 3 4 5 6 7 8 9 0 1 2 3 4 5
------------------------------------*/
1,  0, 0,1,1,0,1,1,0,0,0,0,0,0,1,0,0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
2,  0, 0,0,0,1,0,1,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
3,  0, 1,0,1,0,0,0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
4,  1, 1,0,1,0,0,1,1,1,1,0,1,0,0,0,0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
5,  2, 0,0,0,1,0,1,1,1,1,1,1,1,0,1,0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
6,  3, 1,0,0,0,1,1,1,1,1,0,0,0,0,1,1, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
7,  0, 1,0,1,1,1,1,1,1,0,1,1,0,0,0,0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
8,  0, 1,0,1,0,1,1,1,1,0,0,1,0,0,0,0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
9,  0, 1,0,0,0,1,1,0,1,1,1,1,1,1,1,0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
10, 1, 0,0,0,0,0,0,0,0,0,1,1,0,1,0,0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
11, 2, 1,1,1,0,0,1,1,0,1,1,1,0,1,0,1, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
12, 3, 1,1,1,1,1,1,1,1,1,1,1,0,0,1,1, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
13, 0, 1,0,1,0,1,1,1,1,1,0,1,0,0,1,1, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
};


/***********************************************************************/
/**                                                                   **/
/**               NASA B data for the two replications                **/
/**                                                                   **/
/***********************************************************************/

/* NASA B constants for the two replications */

const int B_NOV_ERR   =  15;
const int B_NOV       =  12;

const int B_JUN_ERR   =  15;
const int B_JUN       =  13;

/* NASA B scores for NOV replication */

scores b_nov[B_NOV] = 
{/*
ID  P  1 2 3 4 5 6 7 8 9 0 1 2 3 4 5
------------------------------------*/
1,  0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
2,  0, 0,0,1,0,0,0,0,0,0,0,1,0,0,0,1, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
3,  1, 0,0,0,1,0,0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
4,  1, 1,0,1,0,0,0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
6,  0, 0,0,1,1,0,0,0,0,0,1,1,1,0,1,0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
7,  0, 0,0,1,0,0,0,0,0,0,0,1,0,0,0,0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
8,  2, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
9,  2, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
11, 0, 0,0,1,1,0,0,0,1,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
12, 0, 1,0,0,0,0,0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
13, 3, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,1, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
14, 3, 0,0,1,0,0,0,0,0,1,0,1,0,0,0,1, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
};

/* NASA B scores for JUN replication */

scores b_jun[B_JUN] = 
{/*
ID  P  1 2 3 4 5 6 7 8 9 0 1 2 3 4 5
------------------------------------*/
1,  1, 0,1,0,1,1,1,1,1,1,0,0,0,0,1,0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
2,  2, 1,0,0,0,0,0,0,0,0,0,1,0,0,0,0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
3,  3, 0,0,0,0,0,0,0,1,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
4,  0, 1,0,0,0,1,1,1,0,0,0,1,0,0,0,1, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
5,  0, 1,0,1,1,1,1,1,1,1,0,1,1,0,1,1, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
6,  0, 1,0,0,0,1,1,1,0,1,0,1,1,0,1,1, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
7,  1, 1,1,1,1,1,0,0,0,0,0,1,1,0,1,0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
8,  2, 1,1,0,1,1,0,1,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
9,  3, 1,1,1,1,1,1,1,1,1,0,1,1,1,1,1, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
10, 0, 0,1,0,0,0,0,1,0,0,0,0,0,0,1,1, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
11, 0, 1,1,0,0,0,0,1,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
12, 0, 1,1,1,1,1,1,1,1,1,0,1,1,0,1,1, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
13, 1, 1,0,1,1,1,0,1,1,1,0,1,1,1,1,1, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
};


/***********************************************************************/
/**                                                                   **/
/**                  Merge and/or sort two tables                     **/
/**                                                                   **/
/***********************************************************************/

scores *merge_sort(int key, int order,    // key is index for sort key
                   scores *a, int a_rows, // order is INCR or DECR
                   scores *b, int b_rows) 
{
  int i, j, k, tmp;
  scores *tab = new scores[a_rows + b_rows]; // Allocates dynamic memory
                                             // for new table
  if (a != 0)
    for (i=0;i<a_rows;i++)
      for (j=0;j<MAX_COL;j++)
        tab[i][j] = a[i][j];        // Copy all elements from a

  if (b != 0)
    for (i=0;i<b_rows;i++)
      for (j=0;j<MAX_COL;j++)
        tab[i+a_rows][j] = b[i][j]; // Copy all elements from b
  
  for (i=0;i<b_rows+a_rows;i++)
    for (j=i;j<b_rows+a_rows;j++)
      if (order <= 0)               // If decreasing order 
      {
        if (tab[i][key] < tab[j][key])
          for (k=0;k<MAX_COL;k++)
          {
            tmp = tab[i][k];
            tab[i][k] = tab[j][k];
            tab[j][k] = tmp;
          }
      }
      else                          // If increasing order
      {
        if (tab[i][key] > tab[j][key])
          for (k=0;k<MAX_COL;k++)
          {
            tmp = tab[i][k];
            tab[i][k] = tab[j][k];
            tab[j][k] = tmp;
          }
      }

  return tab;
}


/***********************************************************************/
/**                                                                   **/
/**                             Choose                                **/
/**                                                                   **/
/***********************************************************************/

int choose(int a, int b) // Implements the binomial function
{
  int nom = 1, denom = 1, i=0;
  for (i=a;i>(a-b);i--)
    nom *= i;
  for (i=b;i>1;i--)
    denom *= i;

  return nom/denom;
}

/***********************************************************************/
/**                                                                   **/
/**                          Legal team                               **/
/**                                                                   **/
/***********************************************************************/

int legal_team(int a, int b, int c) // Perspectives of members - 
{                                   // always sorted with a<=b<=c
  if (b!=4 && (a==b || b==c))
    return 0;
  return 1;
}

/***********************************************************************/
/**                                                                   **/
/**                             Cross                                 **/
/**                                                                   **/
/***********************************************************************/

int cross(int a) // Computes the cross sum of the binary representation
{                // of a number
  int sum=0;
  do
    sum += a % 2; // % means MOD
  while (a=a/2);  // / of integers means DIV

  return sum;
}

/***********************************************************************/
/**                                                                   **/
/**                            Power                                  **/
/**                                                                   **/
/***********************************************************************/

int power(int a, int b) // Computes a**b
{
  if (b==0)
    return 1;
  return a * power(a, b-1); // Recursive invocation of the power function
}


/***********************************************************************/
/**                                                                   **/
/**                          Combine teams                            **/
/**                                                                   **/
/***********************************************************************/

scores *combine_teams(scores *matr, int rows, int err, int &n_teams)
{
  int i, j, k, l, nasa, design, test, use, poseur, sum;
  scores *matrix = merge_sort(1, INCR, matr, rows, 0, 0); // Make a copy
  nasa=design=test=use=poseur=n_teams=0; 
  for (i=0;i<rows;i++)                   // Find number of people of each 
    if (matrix[i][1] == 0) nasa++;       // perspective
      else if (matrix[i][1] == 1) design++;
      else if (matrix[i][1] == 2) test++;
      else if (matrix[i][1] == 3) use++;
      else if (matrix[i][1] == 4) poseur++;
  scores *teams = new scores[choose(nasa, 3) +  // Allocate memory for all
                             choose(design+test+use+poseur, 3)]; // teams
  for (i=0; i<=nasa-3; i++)
    for (j=i+1; j<=nasa-2; j++)
      for (k=j+1; k<=nasa-1; k++)
      {
        teams[n_teams][0] = n_teams+1;    // A team ID
        teams[n_teams][1] = 0;            // NASA-team
        teams[n_teams][2] = matrix[i][1]; // Perspective of
        teams[n_teams][3] = matrix[j][1]; // all three members
        teams[n_teams][4] = matrix[k][1]; // of the team
        sum = 0;
        for (l=2; l<err+2; l++) // Go through all defects and 
        {                       // check for coverage
          teams[n_teams][l+3]=0;
          if (matrix[i][l] || matrix[j][l] || matrix[k][l])
            sum = sum + (teams[n_teams][l+3] = 1);
        }
        teams[n_teams][err+5] = sum; // Total number of true defects
        n_teams++;                   // found
      }
  for (i=nasa; i<rows-2; i++)  // Exactly the same algorithm for the
    for (j=i+1; j<rows-1; j++) // prspective-based teams, except we
      for (k=j+1; k<rows; k++) // have to check for illegal combinations
      {
        if (legal_team(matrix[i][1], matrix[j][1], matrix[k][1]))
	{
          teams[n_teams][0] = n_teams+1;
          teams[n_teams][1] = 1;            // Perspective-based team
          teams[n_teams][2] = matrix[i][1];
          teams[n_teams][3] = matrix[j][1];
          teams[n_teams][4] = matrix[k][1];
          sum = 0;
          for (l=2; l<=err+1; l++)
          {
            teams[n_teams][l+3]=0;
            if (matrix[i][l] || matrix[j][l] || matrix[k][l])
              sum = sum + (teams[n_teams][l+3] = 1);
          }
          teams[n_teams][err+5] = sum;
          n_teams++;
        }
      }
  delete matrix; // The temporary matrix can be deleted
  return teams;
}


/***********************************************************************/
/**                                                                   **/
/**                     Print individual scores                       **/
/**                                                                   **/
/***********************************************************************/

void print_ind_scores(char* head, scores *matrix, int rows, int err)
{
  int i, j;
  float sum;

  cout << head << "\n";

  cout << "ID P ";
  for (i=1; i<=err; i++) 
    cout << i%10;        // Prints a heading with defect numbers

  cout << " %" << "\n";

  for (i=0; i<rows; i++)
  {
    cout << matrix[i][0];
    if (matrix[i][0]<10)
      cout << " ";
    cout << " " << matrix[i][1] << " ";
    for (j=2, sum=0; j<err+2; j++) 
    {
      cout <<  matrix[i][j];
      if (matrix[i][j]) sum += 1; // Sum up number of defects found
    };
    cout.precision(3);
    cout << " " << sum*100/err << "\n"; // Defect detection rate
  };
  cout << "\n";
}


/***********************************************************************/
/**                                                                   **/
/**                        Print team scores                          **/
/**                                                                   **/
/***********************************************************************/

void print_team_scores(char* head, scores *matrix, int rows, int err)
{
  int i, j;
  float sum;

  cout << head << "(" << rows << " teams)\n";

  cout << "ID P Persp\t";
  for (i=1; i<=err; i++) 
    cout << i%10;

  cout << " %" << "\n";

  for (i=0; i<rows; i++)
  {
    cout << matrix[i][0];
    if (matrix[i][0]<10)
      cout << "  ";
    else
      cout << " ";
    cout << matrix[i][1] << " " // Perspectives of members of the team
         << matrix[i][2] << ","
         << matrix[i][3] << ","
         << matrix[i][4] << "\t";
    for (j=5, sum=0; j<err+5; j++) 
      cout <<  matrix[i][j];

    cout.precision(3);
    cout << " " << (float)matrix[i][err+5]*100/err << "\n"; // Detection rate
  };
  cout << "\n";
}


/***********************************************************************/
/**                                                                   **/
/**                         Dillution                                 **/
/**                                                                   **/
/***********************************************************************/

void dillute(scores *a, int a_rows, int a_err, // Two tables for data that
             scores *b, int b_rows, int b_err) // is to be dilluted. Assumes
{                                              // a_rows == b_rows
  int i, j, k, n_pbr, a_teams, b_teams;
  int *mask = new int [choose(a_rows, a_rows/2)]; // Mask for various perm's
  float a_nasa, a_pbr, b_nasa, b_pbr;
  scores *a_copy, *b_copy, *tmp;

  struct perm_val // For each permutation of people, this struct is
  {               // used to tell the resulting test statistic and
    float stat;   // an indicator of how extensive the dillution was
    int   dill;
  };

  n_pbr = 0;
  for (i=0;i<a_rows;i++) // Find number of PBR people in table a
    if (a[i][1])         // Then, the number of PBR people in table
      n_pbr++;           // b is a_rows - n_pbr. 

  perm_val *tot = new perm_val [choose(a_rows, n_pbr)], // Array of the
            tmp_perm_val;              // results of all permutations

  for (i=0,j=0;i<power(2, a_rows);i++) // Numbers that may be masks 
    if (cross(i) == n_pbr)             // if the cross sum == n_pbr 
      mask[j++] = i;

  for (i=0;i<choose(a_rows, n_pbr);i++) // Loop through all combinations
  {
    a_copy = merge_sort(0, INCR, a, a_rows, 0, 0); // Make copies of both
    b_copy = merge_sort(0, INCR, b, b_rows, 0, 0); // arrays (perspectives
    tot[i].dill = 0;                               // are manipulated)
    for (j=0;j<a_rows;j++)
    {
      if (a_copy[j][1] == 0 && (mask[i] % 2)) // For a, mask[i] == 1 means
      {                                       // that the corresponding
        a_copy[j][1] = 4;                     // reviewer shall be considered
        tot[i].dill++;                        // using PBR. So if he used
      }                                       // the NASA technique, he will
      else if (a_copy[j][1] && !(mask[i] % 2))// be considered a "poseur".
      {                                       // OTOH, if he used PBR and the
        a_copy[j][1] = 0;                     // mask says 0, he is considered
        tot[i].dill++;                        // NASA reviewer. Dillution indi-
      }                                       // cator is updated accordingly.
      if (b_copy[j][1] == 0 && !(mask[i] % 2))// For b it's the same except
        b_copy[j][1] = 4;                     // the mask gets the opposite
      else if (b_copy[j][1] && (mask[i] % 2)) // meaning (1=>NASA, 0=>PBR)
        b_copy[j][1] = 0;

      mask[i] = mask[i]/2;
    }


    tmp = combine_teams(a_copy, a_rows,  // Teams are combined for table a
                        a_err, a_teams);
    j = 0;
    a_nasa = a_pbr = 0;
    while (tmp[j][1]==0)
      a_nasa += (float)tmp[j++][a_err+5]*100/a_err; // Sum up detection rates
    a_nasa = a_nasa/j;                         // to find mean for NASA teams

    j = a_teams-1;
    while (tmp[j][1]==1)
      a_pbr += (float)tmp[j--][a_err+5]*100/a_err; // Same for PBR teams
    a_pbr = a_pbr/(a_teams-j-1);

    delete tmp;

    tmp = combine_teams(b_copy, b_rows, b_err, b_teams); // Same for table b
    j = 0;
    b_nasa = b_pbr = 0;
    while (tmp[j][1]==0)
      b_nasa += (float)tmp[j++][b_err+5]*100/b_err;
    b_nasa = b_nasa/j;

    j = b_teams-1;
    while (tmp[j][1]==1)
      b_pbr += (float)tmp[j--][b_err+5]*100/b_err;
    b_pbr = b_pbr/(b_teams-j-1);

    tot[i].stat = (a_pbr - b_nasa) - (a_nasa - b_pbr); // Compute test stat

    delete tmp;
    delete a_copy;
    delete b_copy;
  }

  for (i=0;i<choose(a_rows, n_pbr);i++)   // Sort the results in decrasing
    for (j=i;j<choose(a_rows, n_pbr);j++) // order
      if (tot[i].stat < tot[j].stat)
      {
        tmp_perm_val = tot[i];
        tot[i] = tot[j];
        tot[j] = tmp_perm_val;
      }

  for (i=0;i<choose(a_rows, n_pbr);i++)   // Print the results
  {
    cout << i+1 << "\t" << tot[i].stat << "\t";
    for (j=0;j<tot[i].dill;j++)
      cout << "*";                        // Bars to indicate dillution
    cout << endl;
  }
}


/***********************************************************************/
/**                                                                   **/
/**                         Main program                              **/
/**                                                                   **/
/***********************************************************************/

int main()
{
  scores *atm_nov_teams = 0, *atm_jun_teams = 0,
         *pg_nov_teams  = 0, *pg_jun_teams  = 0,
         *a_nov_teams   = 0, *a_jun_teams   = 0,
         *b_nov_teams   = 0, *b_jun_teams   = 0;




  int atm_n_nov, atm_n_jun, pg_n_nov, pg_n_jun, 
      a_n_nov, a_n_jun, b_n_nov, b_n_jun;

  atm_nov_teams = combine_teams(atm_nov, ATM_NOV, ATM_NOV_ERR, atm_n_nov);
  atm_jun_teams = combine_teams(atm_jun, ATM_JUN, ATM_JUN_ERR, atm_n_jun);

  pg_nov_teams = combine_teams(pg_nov, PG_NOV, PG_NOV_ERR, pg_n_nov);
  pg_jun_teams = combine_teams(pg_jun, PG_JUN, PG_JUN_ERR, pg_n_jun);

  a_nov_teams = combine_teams(a_nov, A_NOV, A_NOV_ERR, a_n_nov);
  a_jun_teams = combine_teams(a_jun, A_JUN, A_JUN_ERR, a_n_jun);

  b_nov_teams = combine_teams(b_nov, B_NOV, B_NOV_ERR, b_n_nov);
  b_jun_teams = combine_teams(b_jun, B_JUN, B_JUN_ERR, b_n_jun);

  atm_nov_teams = merge_sort(ATM_NOV_ERR+5, DECR, atm_nov_teams, 
                             atm_n_nov, 0, 0);
  atm_jun_teams = merge_sort(ATM_JUN_ERR+5, DECR, atm_jun_teams, 
                             atm_n_jun, 0, 0);

  pg_nov_teams = merge_sort(PG_NOV_ERR+5, DECR, pg_nov_teams, 
                             pg_n_nov, 0, 0);
  pg_jun_teams = merge_sort(PG_JUN_ERR+5, DECR, pg_jun_teams, 
                             pg_n_jun, 0, 0);

  a_nov_teams = merge_sort(A_NOV_ERR+5, DECR, a_nov_teams, 
                             a_n_nov, 0, 0);
  a_jun_teams = merge_sort(A_JUN_ERR+5, DECR, a_jun_teams, 
                             a_n_jun, 0, 0);

  b_nov_teams = merge_sort(B_NOV_ERR+5, DECR, b_nov_teams, 
                             b_n_nov, 0, 0);
  b_jun_teams = merge_sort(B_JUN_ERR+5, DECR, b_jun_teams, 
                             b_n_jun, 0, 0);

                                              // Print individual scores
  print_ind_scores("ATM November individuals",
                   atm_nov, ATM_NOV, ATM_NOV_ERR);
  print_ind_scores("ATM June individuals",
                   atm_jun, ATM_JUN, ATM_JUN_ERR);

  print_ind_scores("PG November individuals",
                   pg_nov, PG_NOV, PG_NOV_ERR);
  print_ind_scores("PG June individuals",
                   pg_jun, PG_JUN, PG_JUN_ERR);

  print_ind_scores("NASA A November individuals",
                   a_nov, A_NOV, A_NOV_ERR);
  print_ind_scores("NASA A June individuals",
                   a_jun, A_JUN, A_JUN_ERR);

  print_ind_scores("NASA B November individuals",
                   b_nov, B_NOV, B_NOV_ERR);
  print_ind_scores("NASA B June individuals",
                   b_jun, B_JUN, B_JUN_ERR);

                                               // Print team scores
  print_team_scores("ATM November teams",
                    atm_nov_teams, atm_n_nov, ATM_NOV_ERR);
  print_team_scores("ATM June teams", 
                    atm_jun_teams, atm_n_jun, ATM_JUN_ERR);

  print_team_scores("PG November teams", 
                    pg_nov_teams, pg_n_nov, PG_NOV_ERR);
  print_team_scores("PG June teams", 
                    pg_jun_teams, pg_n_jun, PG_JUN_ERR);

  print_team_scores("NASA A November teams", 
                    a_nov_teams, a_n_nov, A_NOV_ERR);
  print_team_scores("NASA A June teams", 
                    a_jun_teams, a_n_jun, A_JUN_ERR);

  print_team_scores("NASA B November teams", 
                    b_nov_teams, b_n_nov, B_NOV_ERR);
  print_team_scores("NASA B June teams", 
                    b_jun_teams, b_n_jun, B_JUN_ERR);

  cout << "\nGenerics, November" << endl; 
  dillute(atm_nov, ATM_NOV, ATM_NOV_ERR, // Dillute November team data 
          pg_nov, PG_NOV, PG_NOV_ERR);

  cout << "\nGenerics, June" << endl;   
  dillute(atm_jun, ATM_JUN, ATM_JUN_ERR, // Dillute June team data 
          pg_jun, PG_JUN, PG_JUN_ERR);

  cout << "\nNASA, November" << endl; 
  dillute(a_nov, A_NOV, A_NOV_ERR,       // Dillute November team data 
          b_nov, B_NOV, B_NOV_ERR);

  cout << "\nNASA, June" << endl;   
  dillute(a_jun, A_JUN, A_JUN_ERR,       // Dillute June team data 
          b_jun, B_JUN, B_JUN_ERR);
}
