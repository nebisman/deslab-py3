FUNCTION_BLOCK random_number
	VAR_INPUT
		IN : BOOL;
	END_VAR
	VAR
		M : BOOL;
		INIT : BOOL;
	END_VAR
	VAR_OUTPUT
		OUT : DINT;
	END_VAR

	IF INIT = 0 THEN
		{#include <stdio.h>}
		{#include <stdlib.h>}
		IN := 1;
	END_IF;
	IF M = 0 and IN = 1 THEN
		{SetFbVar(OUT,rand())}
	END_IF;
END_FUNCTION_BLOCK
PROGRAM supcon
	VAR
		random : random_number;
		random_num : DINT;
		initial : BOOL;
		state : ARRAY [0..8] OF DINT;
		slt0 : ARRAY [0..2] OF DINT;
		slt1 : ARRAY [0..12] OF DINT;
		INTERN_0_G : ARRAY [0..2] OF BOOL;
		INTERN_1_G : ARRAY [0..2] OF BOOL;
		FE_M1E : F_TRIG;
		FE_M2E : F_TRIG;
		FE_A : F_TRIG;
		FE_PL : F_TRIG;
		FE_PR : F_TRIG;
		INTERN_4 : BOOL;
		INTERN_5 : BOOL;
		INTERN_2 : BOOL;
		INTERN_3 : BOOL;
		INTERN_0 : BOOL;
		INTERN_1 : BOOL;
	END_VAR
	VAR
		GD_OUT_3 AT %QX100.3 : BOOL;
 		GD_OUT_8 AT %QX101.0 : BOOL;
 		GD_OUT_9 AT %QX101.1 : BOOL;
 		GD_OUT_0 AT %QX100.0 : BOOL;
		GD_OUT_1 AT %QX100.1 : BOOL;
		GD_IN_0 AT %IX100.0 : BOOL;
		GD_IN_1 AT %IX100.1 : BOOL;
		GD_IN_15 AT %IX100.5 : BOOL;
		GD_OUT_2 AT %QX100.2 : BOOL;
		GD_IN_2 AT %IX100.2 : BOOL;
		GD_OUT_4 AT %QX100.4 : BOOL;
		GD_IN_3 AT %IX100.3 : BOOL;
		GD_IN_4 AT %IX100.4 : BOOL;
		GD_OUT_5 AT %QX100.5 : BOOL;
		GD_OUT_6 AT %QX100.6 : BOOL;
		GD_IN_10 AT %IX101.0 : BOOL;
		GD_IN_11 AT %IX101.1 : BOOL;
		GD_IN_12 AT %IX101.2 : BOOL;
		GD_IN_13 AT %IX101.3 : BOOL;
		GD_OUT_10 AT %QX101.2 : BOOL;
		GD_OUT_11 AT %QX101.3 : BOOL;
	END_VAR
	FE_M1E(CLK:= GD_IN_0);
	FE_M2E(CLK:= GD_IN_1);
	FE_A(CLK:= GD_IN_2);
	FE_PL(CLK:= GD_IN_3);
	FE_PR(CLK:= GD_IN_4);
	random(
		IN := True,
		OUT => random_num);
	IF NOT initial THEN
		IF GD_IN_15 THEN
			initial := 1;
		END_IF;
	ELSIF initial THEN
		IF state[0] = 1 & NOT GD_IN_10 THEN
	  		state[0] := 2;
	  	ELSIF state[0] = 1 & FE_PL.Q THEN
	  		state[0] := 3;
	  	ELSIF state[0] = 2 & NOT GD_IN_0 THEN
	  		state[0] := 0;
	  	ELSIF state[0] = 4 & NOT GD_IN_10 THEN
	  		state[0] := 7;
	  	ELSIF state[0] = 4 & FE_PL.Q THEN
	  		state[0] := 8;
	  	ELSIF state[0] = 5 & NOT GD_IN_11 THEN
	  		state[0] := 9;
	  	ELSIF state[0] = 5 & FE_M2E.Q THEN
	  		state[0] := 0;
	  	ELSIF state[0] = 6 & NOT GD_IN_10 THEN
	  		state[0] := 10;
	  	ELSIF state[0] = 6 & NOT GD_IN_11 THEN
	  		state[0] := 11;
	  	ELSIF state[0] = 6 & FE_PL.Q THEN
	  		state[0] := 12;
	  	ELSIF state[0] = 6 & FE_M2E.Q THEN
	  		state[0] := 1;
	  	ELSIF state[0] = 7 & NOT GD_IN_0 THEN
	  		state[0] := 3;
	  	ELSIF state[0] = 9 & FE_M2E.Q THEN
	  		state[0] := 13;
	  	ELSIF state[0] = 10 & NOT GD_IN_0 THEN
	  		state[0] := 5;
	  	ELSIF state[0] = 10 & NOT GD_IN_11 THEN
	  		state[0] := 14;
	  	ELSIF state[0] = 10 & FE_M2E.Q THEN
	  		state[0] := 2;
	  	ELSIF state[0] = 11 & NOT GD_IN_10 THEN
	  		state[0] := 14;
	  	ELSIF state[0] = 11 & FE_PL.Q THEN
	  		state[0] := 15;
	  	ELSIF state[0] = 11 & FE_M2E.Q THEN
	  		state[0] := 16;
	  	ELSIF state[0] = 12 & NOT GD_IN_11 THEN
	  		state[0] := 15;
	  	ELSIF state[0] = 12 & FE_M2E.Q THEN
	  		state[0] := 3;
	  	ELSIF state[0] = 14 & NOT GD_IN_0 THEN
	  		state[0] := 9;
	  	ELSIF state[0] = 14 & FE_M2E.Q THEN
	  		state[0] := 18;
	  	ELSIF state[0] = 15 & FE_M2E.Q THEN
	  		state[0] := 20;
	  	ELSIF state[0] = 16 & NOT GD_IN_10 THEN
	  		state[0] := 18;
	  	ELSIF state[0] = 16 & FE_PL.Q THEN
	  		state[0] := 20;
	  	ELSIF state[0] = 17 & NOT GD_IN_10 THEN
	  		state[0] := 21;
	  	ELSIF state[0] = 17 & NOT GD_IN_11 THEN
	  		state[0] := 19;
	  	ELSIF state[0] = 17 & FE_PL.Q THEN
	  		state[0] := 22;
	  	ELSIF state[0] = 17 & FE_M2E.Q THEN
	  		state[0] := 4;
	  	ELSIF state[0] = 18 & NOT GD_IN_0 THEN
	  		state[0] := 13;
	  	ELSIF state[0] = 19 & NOT GD_IN_10 THEN
	  		state[0] := 23;
	  	ELSIF state[0] = 19 & FE_PL.Q THEN
	  		state[0] := 24;
	  	ELSIF state[0] = 19 & FE_M2E.Q THEN
	  		state[0] := 25;
	  	ELSIF state[0] = 21 & NOT GD_IN_0 THEN
	  		state[0] := 12;
	  	ELSIF state[0] = 21 & NOT GD_IN_11 THEN
	  		state[0] := 23;
	  	ELSIF state[0] = 21 & FE_M2E.Q THEN
	  		state[0] := 7;
	  	ELSIF state[0] = 22 & NOT GD_IN_11 THEN
	  		state[0] := 24;
	  	ELSIF state[0] = 22 & FE_M2E.Q THEN
	  		state[0] := 8;
	  	ELSIF state[0] = 23 & NOT GD_IN_0 THEN
	  		state[0] := 15;
	  	ELSIF state[0] = 23 & FE_M2E.Q THEN
	  		state[0] := 27;
	  	ELSIF state[0] = 24 & FE_M2E.Q THEN
	  		state[0] := 28;
	  	ELSIF state[0] = 25 & NOT GD_IN_10 THEN
	  		state[0] := 27;
	  	ELSIF state[0] = 25 & FE_PL.Q THEN
	  		state[0] := 28;
	  	ELSIF state[0] = 26 & NOT GD_IN_11 THEN
	  		state[0] := 9;
	  	ELSIF state[0] = 26 & FE_M2E.Q THEN
	  		state[0] := 13;
	  	ELSIF state[0] = 27 & NOT GD_IN_0 THEN
	  		state[0] := 20;
	  	ELSIF state[0] = 29 & NOT GD_IN_10 THEN
	  		state[0] := 30;
	  	ELSIF state[0] = 29 & NOT GD_IN_11 THEN
	  		state[0] := 11;
	  	ELSIF state[0] = 29 & FE_PL.Q THEN
	  		state[0] := 31;
	  	ELSIF state[0] = 29 & FE_M2E.Q THEN
	  		state[0] := 16;
	  	ELSIF state[0] = 30 & NOT GD_IN_0 THEN
	  		state[0] := 26;
	  	ELSIF state[0] = 30 & NOT GD_IN_11 THEN
	  		state[0] := 14;
	  	ELSIF state[0] = 30 & FE_M2E.Q THEN
	  		state[0] := 18;
	  	ELSIF state[0] = 31 & NOT GD_IN_11 THEN
	  		state[0] := 15;
	  	ELSIF state[0] = 31 & FE_M2E.Q THEN
	  		state[0] := 20;
	  	ELSIF state[0] = 32 & NOT GD_IN_10 THEN
	  		state[0] := 33;
	  	ELSIF state[0] = 32 & NOT GD_IN_11 THEN
	  		state[0] := 19;
	  	ELSIF state[0] = 32 & FE_PL.Q THEN
	  		state[0] := 34;
	  	ELSIF state[0] = 32 & FE_M2E.Q THEN
	  		state[0] := 25;
	  	ELSIF state[0] = 33 & NOT GD_IN_0 THEN
	  		state[0] := 31;
	  	ELSIF state[0] = 33 & NOT GD_IN_11 THEN
	  		state[0] := 23;
	  	ELSIF state[0] = 33 & FE_M2E.Q THEN
	  		state[0] := 27;
	  	ELSIF state[0] = 34 & NOT GD_IN_11 THEN
	  		state[0] := 24;
	  	ELSIF state[0] = 34 & FE_M2E.Q THEN
	  		state[0] := 28;
	  	END_IF;
	
		IF state[1] = 0 & GD_IN_15 THEN
	  		state[1] := 1;
	  	ELSIF state[1] = 2 & FE_A.Q THEN
	  		state[1] := 5;
	  	ELSIF state[1] = 3 & NOT GD_IN_10 THEN
	  		state[1] := 9;
	  	ELSIF state[1] = 3 & FE_PL.Q THEN
	  		state[1] := 1;
	  	ELSIF state[1] = 4 & NOT GD_IN_11 THEN
	  		state[1] := 10;
	  	ELSIF state[1] = 4 & FE_M2E.Q THEN
	  		state[1] := 1;
	  	ELSIF state[1] = 6 & FE_A.Q THEN
	  		state[1] := 12;
	  	ELSIF state[1] = 6 & NOT GD_IN_10 THEN
	  		state[1] := 15;
	  	ELSIF state[1] = 6 & FE_PL.Q THEN
	  		state[1] := 2;
	  	ELSIF state[1] = 7 & FE_A.Q THEN
	  		state[1] := 13;
	  	ELSIF state[1] = 7 & NOT GD_IN_11 THEN
	  		state[1] := 16;
	  	ELSIF state[1] = 7 & FE_M2E.Q THEN
	  		state[1] := 2;
	  	ELSIF state[1] = 8 & NOT GD_IN_10 THEN
	  		state[1] := 17;
	  	ELSIF state[1] = 8 & NOT GD_IN_11 THEN
	  		state[1] := 18;
	  	ELSIF state[1] = 8 & FE_PL.Q THEN
	  		state[1] := 4;
	  	ELSIF state[1] = 8 & FE_M2E.Q THEN
	  		state[1] := 3;
	  	ELSIF state[1] = 9 & NOT GD_IN_0 THEN
	  		state[1] := 1;
	  	ELSIF state[1] = 10 & FE_M2E.Q THEN
	  		state[1] := 1;
	  	ELSIF state[1] = 11 & FE_M1E.Q THEN
	  		state[1] := 1;
	  	ELSIF state[1] = 12 & NOT GD_IN_10 THEN
	  		state[1] := 22;
	  	ELSIF state[1] = 12 & FE_PL.Q THEN
	  		state[1] := 5;
	  	ELSIF state[1] = 13 & NOT GD_IN_11 THEN
	  		state[1] := 23;
	  	ELSIF state[1] = 13 & FE_M2E.Q THEN
	  		state[1] := 5;
	  	ELSIF state[1] = 14 & FE_A.Q THEN
	  		state[1] := 21;
	  	ELSIF state[1] = 14 & NOT GD_IN_10 THEN
	  		state[1] := 24;
	  	ELSIF state[1] = 14 & NOT GD_IN_11 THEN
	  		state[1] := 25;
	  	ELSIF state[1] = 14 & FE_PL.Q THEN
	  		state[1] := 7;
	  	ELSIF state[1] = 14 & FE_M2E.Q THEN
	  		state[1] := 6;
	  	ELSIF state[1] = 15 & FE_A.Q THEN
	  		state[1] := 22;
	  	ELSIF state[1] = 15 & NOT GD_IN_0 THEN
	  		state[1] := 2;
	  	ELSIF state[1] = 16 & FE_A.Q THEN
	  		state[1] := 23;
	  	ELSIF state[1] = 16 & FE_M2E.Q THEN
	  		state[1] := 2;
	  	ELSIF state[1] = 17 & NOT GD_IN_0 THEN
	  		state[1] := 4;
	  	ELSIF state[1] = 17 & NOT GD_IN_11 THEN
	  		state[1] := 26;
	  	ELSIF state[1] = 17 & FE_M2E.Q THEN
	  		state[1] := 9;
	  	ELSIF state[1] = 18 & NOT GD_IN_10 THEN
	  		state[1] := 26;
	  	ELSIF state[1] = 18 & FE_PL.Q THEN
	  		state[1] := 10;
	  	ELSIF state[1] = 18 & FE_M2E.Q THEN
	  		state[1] := 3;
	  	ELSIF state[1] = 19 & FE_M1E.Q THEN
	  		state[1] := 3;
	  	ELSIF state[1] = 19 & NOT GD_IN_10 THEN
	  		state[1] := 28;
	  	ELSIF state[1] = 19 & FE_PL.Q THEN
	  		state[1] := 11;
	  	ELSIF state[1] = 20 & FE_M1E.Q THEN
	  		state[1] := 4;
	  	ELSIF state[1] = 20 & NOT GD_IN_11 THEN
	  		state[1] := 29;
	  	ELSIF state[1] = 20 & FE_M2E.Q THEN
	  		state[1] := 11;
	  	ELSIF state[1] = 21 & NOT GD_IN_10 THEN
	  		state[1] := 30;
	  	ELSIF state[1] = 21 & NOT GD_IN_11 THEN
	  		state[1] := 31;
	  	ELSIF state[1] = 21 & FE_PL.Q THEN
	  		state[1] := 13;
	  	ELSIF state[1] = 21 & FE_M2E.Q THEN
	  		state[1] := 12;
	  	ELSIF state[1] = 22 & NOT GD_IN_0 THEN
	  		state[1] := 5;
	  	ELSIF state[1] = 23 & FE_M2E.Q THEN
	  		state[1] := 5;
	  	ELSIF state[1] = 24 & FE_A.Q THEN
	  		state[1] := 30;
	  	ELSIF state[1] = 24 & NOT GD_IN_0 THEN
	  		state[1] := 7;
	  	ELSIF state[1] = 24 & NOT GD_IN_11 THEN
	  		state[1] := 32;
	  	ELSIF state[1] = 24 & FE_M2E.Q THEN
	  		state[1] := 15;
	  	ELSIF state[1] = 25 & FE_A.Q THEN
	  		state[1] := 31;
	  	ELSIF state[1] = 25 & NOT GD_IN_10 THEN
	  		state[1] := 32;
	  	ELSIF state[1] = 25 & FE_PL.Q THEN
	  		state[1] := 16;
	  	ELSIF state[1] = 25 & FE_M2E.Q THEN
	  		state[1] := 6;
	  	ELSIF state[1] = 26 & NOT GD_IN_0 THEN
	  		state[1] := 10;
	  	ELSIF state[1] = 26 & FE_M2E.Q THEN
	  		state[1] := 9;
	  	ELSIF state[1] = 27 & FE_M1E.Q THEN
	  		state[1] := 8;
	  	ELSIF state[1] = 27 & NOT GD_IN_10 THEN
	  		state[1] := 33;
	  	ELSIF state[1] = 27 & NOT GD_IN_11 THEN
	  		state[1] := 34;
	  	ELSIF state[1] = 27 & FE_PL.Q THEN
	  		state[1] := 20;
	  	ELSIF state[1] = 27 & FE_M2E.Q THEN
	  		state[1] := 19;
	  	ELSIF state[1] = 28 & FE_M1E.Q THEN
	  		state[1] := 9;
	  	ELSIF state[1] = 28 & NOT GD_IN_0 THEN
	  		state[1] := 11;
	  	ELSIF state[1] = 29 & FE_M1E.Q THEN
	  		state[1] := 10;
	  	ELSIF state[1] = 29 & FE_M2E.Q THEN
	  		state[1] := 11;
	  	ELSIF state[1] = 30 & NOT GD_IN_0 THEN
	  		state[1] := 13;
	  	ELSIF state[1] = 30 & NOT GD_IN_11 THEN
	  		state[1] := 35;
	  	ELSIF state[1] = 30 & FE_M2E.Q THEN
	  		state[1] := 22;
	  	ELSIF state[1] = 31 & NOT GD_IN_10 THEN
	  		state[1] := 35;
	  	ELSIF state[1] = 31 & FE_PL.Q THEN
	  		state[1] := 23;
	  	ELSIF state[1] = 31 & FE_M2E.Q THEN
	  		state[1] := 12;
	  	ELSIF state[1] = 32 & FE_A.Q THEN
	  		state[1] := 35;
	  	ELSIF state[1] = 32 & NOT GD_IN_0 THEN
	  		state[1] := 16;
	  	ELSIF state[1] = 32 & FE_M2E.Q THEN
	  		state[1] := 15;
	  	ELSIF state[1] = 33 & FE_M1E.Q THEN
	  		state[1] := 17;
	  	ELSIF state[1] = 33 & NOT GD_IN_0 THEN
	  		state[1] := 20;
	  	ELSIF state[1] = 33 & NOT GD_IN_11 THEN
	  		state[1] := 36;
	  	ELSIF state[1] = 33 & FE_M2E.Q THEN
	  		state[1] := 28;
	  	ELSIF state[1] = 34 & FE_M1E.Q THEN
	  		state[1] := 18;
	  	ELSIF state[1] = 34 & NOT GD_IN_10 THEN
	  		state[1] := 36;
	  	ELSIF state[1] = 34 & FE_PL.Q THEN
	  		state[1] := 29;
	  	ELSIF state[1] = 34 & FE_M2E.Q THEN
	  		state[1] := 19;
	  	ELSIF state[1] = 35 & NOT GD_IN_0 THEN
	  		state[1] := 23;
	  	ELSIF state[1] = 35 & FE_M2E.Q THEN
	  		state[1] := 22;
	  	ELSIF state[1] = 36 & FE_M1E.Q THEN
	  		state[1] := 26;
	  	ELSIF state[1] = 36 & NOT GD_IN_0 THEN
	  		state[1] := 29;
	  	ELSIF state[1] = 36 & FE_M2E.Q THEN
	  		state[1] := 28;
	  	END_IF;
	
		IF state[2] = 0 & GD_OUT_0 THEN
	  		state[2] := 1;
	  	ELSIF state[2] = 1 & GD_IN_0 THEN
	  		state[2] := 2;
	  	ELSIF state[2] = 3 & FE_M1E.Q THEN
	  		state[2] := 0;
	  	END_IF;
	
		IF state[3] = 0 & GD_OUT_1 THEN
	  		state[3] := 1;
	  	ELSIF state[3] = 1 & GD_IN_1 THEN
	  		state[3] := 2;
	  	ELSIF state[3] = 3 & FE_M2E.Q THEN
	  		state[3] := 0;
	  	END_IF;
	
		IF state[4] = 0 & GD_IN_0 THEN
	  		state[4] := 1;
	  	ELSIF state[4] = 1 & FE_M1E.Q THEN
	  		state[4] := 2;
	  	ELSIF state[4] = 1 & NOT GD_IN_10 THEN
	  		state[4] := 3;
	  	ELSIF state[4] = 3 & FE_M1E.Q THEN
	  		state[4] := 0;
	  	ELSIF state[4] = 4 & FE_PL.Q THEN
	  		state[4] := 5;
	  	END_IF;
	
		IF state[5] = 0 & GD_IN_15 THEN
	  		state[5] := 1;
	  	ELSIF state[5] = 1 & FE_M1E.Q THEN
	  		state[5] := 2;
	  	ELSIF state[5] = 1 & NOT GD_IN_10 THEN
	  		state[5] := 3;
	  	ELSIF state[5] = 3 & FE_M1E.Q THEN
	  		state[5] := 1;
	  	ELSIF state[5] = 4 & FE_PR.Q THEN
	  		state[5] := 5;
	  	ELSIF state[5] = 6 & FE_M1E.Q THEN
	  		state[5] := 7;
	  	ELSIF state[5] = 6 & FE_M2E.Q THEN
	  		state[5] := 2;
	  	ELSIF state[5] = 8 & FE_PL.Q THEN
	  		state[5] := 9;
	  	ELSIF state[5] = 8 & FE_M2E.Q THEN
	  		state[5] := 2;
	  	END_IF;
	
		IF state[6] = 0 & FE_M2E.Q THEN
	  		state[6] := 1;
	  	ELSIF state[6] = 2 & FE_PR.Q THEN
	  		state[6] := 3;
	  	END_IF;
	
		IF state[7] = 0 & NOT GD_IN_10 THEN
	  		state[7] := 1;
	  	ELSIF state[7] = 0 & NOT GD_IN_11 THEN
	  		state[7] := 2;
	  	ELSIF state[7] = 3 & GD_IN_12 THEN
	  		state[7] := 5;
	  	ELSIF state[7] = 3 & NOT GD_IN_11 THEN
	  		state[7] := 6;
	  	ELSIF state[7] = 4 & GD_IN_13 THEN
	  		state[7] := 7;
	  	ELSIF state[7] = 4 & NOT GD_IN_10 THEN
	  		state[7] := 8;
	  	ELSIF state[7] = 8 & GD_IN_13 THEN
	  		state[7] := 12;
	  	ELSIF state[7] = 13 & NOT GD_IN_0 THEN
	  		state[7] := 16;
	  	ELSIF state[7] = 14 & FE_M2E.Q THEN
	  		state[7] := 17;
	  	ELSIF state[7] = 18 & FE_M2E.Q THEN
	  		state[7] := 19;
	  	END_IF;
	
	
		CASE state[0] OF
	  		0:
	  			INTERN_0_G[0] := 1;
			3:
	  			CASE slt0[0] OF
	  				0:
	  					INTERN_0_G[0] := 1;
	  				1:
	  					INTERN_1_G[0] := 1;
	  			END_CASE;
	  			slt0[0] := (random_num + slt0[0]) MOD 2;
	  			random_num := random_num - slt0[0];
	 		4:
	  			INTERN_1_G[0] := 1;
			5:
	  			INTERN_0_G[0] := 1;
			7:
	  			INTERN_1_G[0] := 1;
			8:
	  			INTERN_1_G[0] := 1;
			9:
	  			INTERN_0_G[0] := 1;
			12:
	  			INTERN_0_G[0] := 1;
			13:
	  			INTERN_0_G[0] := 1;
			15:
	  			INTERN_0_G[0] := 1;
			20:
	  			CASE slt0[1] OF
	  				0:
	  					INTERN_0_G[0] := 1;
	  				1:
	  					INTERN_1_G[0] := 1;
	  			END_CASE;
	  			slt0[1] := (random_num + slt0[1]) MOD 2;
	  			random_num := random_num - slt0[1];
	 		25:
	  			INTERN_1_G[0] := 1;
			26:
	  			INTERN_0_G[0] := 1;
			27:
	  			INTERN_1_G[0] := 1;
			28:
	  			INTERN_1_G[0] := 1;
			31:
	  			INTERN_0_G[0] := 1;
		END_CASE;
	
		CASE state[1] OF
	  		1:
	  			CASE slt1[0] OF
	  				0:
	  					GD_OUT_2 := 1;
	  				1:
	  					INTERN_0_G[1] := 1;
	  				2:
	  					INTERN_1_G[1] := 1;
	  			END_CASE;
	  			slt1[0] := (random_num + slt1[0]) MOD 3;
	  			random_num := random_num - slt1[0];
	 		2:
	  			CASE slt1[1] OF
	  				0:
	  					INTERN_0_G[1] := 1;
	  				1:
	  					INTERN_1_G[1] := 1;
	  			END_CASE;
	  			slt1[1] := (random_num + slt1[1]) MOD 2;
	  			random_num := random_num - slt1[1];
	 		3:
	  			CASE slt1[2] OF
	  				0:
	  					GD_OUT_2 := 1;
	  				1:
	  					INTERN_1_G[1] := 1;
	  			END_CASE;
	  			slt1[2] := (random_num + slt1[2]) MOD 2;
	  			random_num := random_num - slt1[2];
	 		4:
	  			CASE slt1[3] OF
	  				0:
	  					GD_OUT_2 := 1;
	  				1:
	  					INTERN_0_G[1] := 1;
	  			END_CASE;
	  			slt1[3] := (random_num + slt1[3]) MOD 2;
	  			random_num := random_num - slt1[3];
	 		5:
	  			CASE slt1[4] OF
	  				0:
	  					GD_OUT_2 := 0;
	  				1:
	  					INTERN_0_G[1] := 1;
	  				2:
	  					INTERN_1_G[1] := 1;
	  			END_CASE;
	  			slt1[4] := (random_num + slt1[4]) MOD 3;
	  			random_num := random_num - slt1[4];
	 		6:
	  			INTERN_1_G[1] := 1;
			7:
	  			INTERN_0_G[1] := 1;
			8:
	  			GD_OUT_2 := 1;
			9:
	  			CASE slt1[5] OF
	  				0:
	  					GD_OUT_2 := 1;
	  				1:
	  					INTERN_1_G[1] := 1;
	  			END_CASE;
	  			slt1[5] := (random_num + slt1[5]) MOD 2;
	  			random_num := random_num - slt1[5];
	 		10:
	  			CASE slt1[6] OF
	  				0:
	  					GD_OUT_2 := 1;
	  				1:
	  					INTERN_0_G[1] := 1;
	  			END_CASE;
	  			slt1[6] := (random_num + slt1[6]) MOD 2;
	  			random_num := random_num - slt1[6];
	 		11:
	  			CASE slt1[7] OF
	  				0:
	  					INTERN_0_G[1] := 1;
	  				1:
	  					INTERN_1_G[1] := 1;
	  			END_CASE;
	  			slt1[7] := (random_num + slt1[7]) MOD 2;
	  			random_num := random_num - slt1[7];
	 		12:
	  			CASE slt1[8] OF
	  				0:
	  					GD_OUT_2 := 0;
	  				1:
	  					INTERN_1_G[1] := 1;
	  			END_CASE;
	  			slt1[8] := (random_num + slt1[8]) MOD 2;
	  			random_num := random_num - slt1[8];
	 		13:
	  			CASE slt1[9] OF
	  				0:
	  					GD_OUT_2 := 0;
	  				1:
	  					INTERN_0_G[1] := 1;
	  			END_CASE;
	  			slt1[9] := (random_num + slt1[9]) MOD 2;
	  			random_num := random_num - slt1[9];
	 		15:
	  			INTERN_1_G[1] := 1;
			16:
	  			INTERN_0_G[1] := 1;
			17:
	  			GD_OUT_2 := 1;
			18:
	  			GD_OUT_2 := 1;
			19:
	  			INTERN_1_G[1] := 1;
			20:
	  			INTERN_0_G[1] := 1;
			21:
	  			GD_OUT_2 := 0;
	  		22:
	  			CASE slt1[10] OF
	  				0:
	  					GD_OUT_2 := 0;
	  				1:
	  					INTERN_1_G[1] := 1;
	  			END_CASE;
	  			slt1[10] := (random_num + slt1[10]) MOD 2;
	  			random_num := random_num - slt1[10];
	 		23:
	  			CASE slt1[11] OF
	  				0:
	  					GD_OUT_2 := 0;
	  				1:
	  					INTERN_0_G[1] := 1;
	  			END_CASE;
	  			slt1[11] := (random_num + slt1[11]) MOD 2;
	  			random_num := random_num - slt1[11];
	 		26:
	  			GD_OUT_2 := 1;
			28:
	  			INTERN_1_G[1] := 1;
			29:
	  			INTERN_0_G[1] := 1;
			30:
	  			GD_OUT_2 := 0;
	  		31:
	  			GD_OUT_2 := 0;
	  		35:
	  			GD_OUT_2 := 0;
	  	END_CASE;
	
		CASE state[2] OF
	  		2:
	  			GD_OUT_0 := 0;
	  	END_CASE;
	
		CASE state[3] OF
	  		2:
	  			GD_OUT_1 := 0;
	  	END_CASE;
	
		CASE state[4] OF
	  		2:
	  			GD_OUT_5 := 1;
			5:
	  			GD_OUT_5 := 0;
	  	END_CASE;
	
		CASE state[5] OF
	  		2:
	  			GD_OUT_4 := 1;
			5:
	  			GD_OUT_4 := 0;
	  		7:
	  			GD_OUT_4 := 1;
			9:
	  			GD_OUT_4 := 0;
	  	END_CASE;
	
		CASE state[6] OF
	  		1:
	  			GD_OUT_6 := 0;
	  		3:
	  			GD_OUT_6 := 1;
		END_CASE;
	
		CASE state[7] OF
	  		1:
	  			INTERN_2 := 1;
			2:
	  			INTERN_3 := 1;
			5:
	  			GD_OUT_10 := 1;
			6:
	  			INTERN_2 := 0;
	  		7:
	  			GD_OUT_11 := 1;
			9:
	  			INTERN_2 := 0;
	  		10:
	  			INTERN_3 := 1;
			11:
	  			INTERN_3 := 0;
	  		12:
	  			GD_OUT_11 := 1;
			15:
	  			INTERN_3 := 0;
	  		16:
	  			GD_OUT_10 := 0;
	  		17:
	  			GD_OUT_11 := 0;
	  		19:
	  			GD_OUT_11 := 0;
	  	END_CASE;
		IF INTERN_0_G[0] <> INTERN_0_G[1] THEN
			INTERN_0_G[0] := INTERN_0;
			INTERN_0_G[1] := INTERN_0;
		END_IF;
		INTERN_0 := INTERN_0_G[0];
		IF INTERN_1_G[0] <> INTERN_1_G[1] THEN
			INTERN_1_G[0] := INTERN_1;
			INTERN_1_G[1] := INTERN_1;
		END_IF;
		INTERN_1 := INTERN_1_G[0];
		IF state[0] = 0 & INTERN_0 THEN
	  		state[0] := 1;
	  	ELSIF state[0] = 3 & INTERN_0 THEN
	  		state[0] := 4;
	  	ELSIF state[0] = 3 & INTERN_1 THEN
	  		state[0] := 5;
	  	ELSIF state[0] = 4 & INTERN_1 THEN
	  		state[0] := 6;
	  	ELSIF state[0] = 5 & INTERN_0 THEN
	  		state[0] := 6;
	  	ELSIF state[0] = 7 & INTERN_1 THEN
	  		state[0] := 10;
	  	ELSIF state[0] = 8 & INTERN_1 THEN
	  		state[0] := 12;
	  	ELSIF state[0] = 9 & INTERN_0 THEN
	  		state[0] := 11;
	  	ELSIF state[0] = 12 & INTERN_0 THEN
	  		state[0] := 17;
	  	ELSIF state[0] = 13 & INTERN_0 THEN
	  		state[0] := 16;
	  	ELSIF state[0] = 15 & INTERN_0 THEN
	  		state[0] := 19;
	  	ELSIF state[0] = 20 & INTERN_0 THEN
	  		state[0] := 25;
	  	ELSIF state[0] = 20 & INTERN_1 THEN
	  		state[0] := 26;
	  	ELSIF state[0] = 25 & INTERN_1 THEN
	  		state[0] := 29;
	  	ELSIF state[0] = 26 & INTERN_0 THEN
	  		state[0] := 29;
	  	ELSIF state[0] = 27 & INTERN_1 THEN
	  		state[0] := 30;
	  	ELSIF state[0] = 28 & INTERN_1 THEN
	  		state[0] := 31;
	  	ELSIF state[0] = 31 & INTERN_0 THEN
	  		state[0] := 32;
	  	END_IF;
	
		IF state[1] = 1 & GD_OUT_2 THEN
	  		state[1] := 2;
	  	ELSIF state[1] = 1 & INTERN_0 THEN
	  		state[1] := 3;
	  	ELSIF state[1] = 1 & INTERN_1 THEN
	  		state[1] := 4;
	  	ELSIF state[1] = 2 & INTERN_0 THEN
	  		state[1] := 6;
	  	ELSIF state[1] = 2 & INTERN_1 THEN
	  		state[1] := 7;
	  	ELSIF state[1] = 3 & GD_OUT_2 THEN
	  		state[1] := 6;
	  	ELSIF state[1] = 3 & INTERN_1 THEN
	  		state[1] := 8;
	  	ELSIF state[1] = 4 & GD_OUT_2 THEN
	  		state[1] := 7;
	  	ELSIF state[1] = 4 & INTERN_0 THEN
	  		state[1] := 8;
	  	ELSIF state[1] = 5 & NOT GD_OUT_2 THEN
	  		state[1] := 11;
	  	ELSIF state[1] = 5 & INTERN_0 THEN
	  		state[1] := 12;
	  	ELSIF state[1] = 5 & INTERN_1 THEN
	  		state[1] := 13;
	  	ELSIF state[1] = 6 & INTERN_1 THEN
	  		state[1] := 14;
	  	ELSIF state[1] = 7 & INTERN_0 THEN
	  		state[1] := 14;
	  	ELSIF state[1] = 8 & GD_OUT_2 THEN
	  		state[1] := 14;
	  	ELSIF state[1] = 9 & GD_OUT_2 THEN
	  		state[1] := 15;
	  	ELSIF state[1] = 9 & INTERN_1 THEN
	  		state[1] := 17;
	  	ELSIF state[1] = 10 & GD_OUT_2 THEN
	  		state[1] := 16;
	  	ELSIF state[1] = 10 & INTERN_0 THEN
	  		state[1] := 18;
	  	ELSIF state[1] = 11 & INTERN_0 THEN
	  		state[1] := 19;
	  	ELSIF state[1] = 11 & INTERN_1 THEN
	  		state[1] := 20;
	  	ELSIF state[1] = 12 & NOT GD_OUT_2 THEN
	  		state[1] := 19;
	  	ELSIF state[1] = 12 & INTERN_1 THEN
	  		state[1] := 21;
	  	ELSIF state[1] = 13 & NOT GD_OUT_2 THEN
	  		state[1] := 20;
	  	ELSIF state[1] = 13 & INTERN_0 THEN
	  		state[1] := 21;
	  	ELSIF state[1] = 15 & INTERN_1 THEN
	  		state[1] := 24;
	  	ELSIF state[1] = 16 & INTERN_0 THEN
	  		state[1] := 25;
	  	ELSIF state[1] = 17 & GD_OUT_2 THEN
	  		state[1] := 24;
	  	ELSIF state[1] = 18 & GD_OUT_2 THEN
	  		state[1] := 25;
	  	ELSIF state[1] = 19 & INTERN_1 THEN
	  		state[1] := 27;
	  	ELSIF state[1] = 20 & INTERN_0 THEN
	  		state[1] := 27;
	  	ELSIF state[1] = 21 & NOT GD_OUT_2 THEN
	  		state[1] := 27;
	  	ELSIF state[1] = 22 & NOT GD_OUT_2 THEN
	  		state[1] := 28;
	  	ELSIF state[1] = 22 & INTERN_1 THEN
	  		state[1] := 30;
	  	ELSIF state[1] = 23 & NOT GD_OUT_2 THEN
	  		state[1] := 29;
	  	ELSIF state[1] = 23 & INTERN_0 THEN
	  		state[1] := 31;
	  	ELSIF state[1] = 26 & GD_OUT_2 THEN
	  		state[1] := 32;
	  	ELSIF state[1] = 28 & INTERN_1 THEN
	  		state[1] := 33;
	  	ELSIF state[1] = 29 & INTERN_0 THEN
	  		state[1] := 34;
	  	ELSIF state[1] = 30 & NOT GD_OUT_2 THEN
	  		state[1] := 33;
	  	ELSIF state[1] = 31 & NOT GD_OUT_2 THEN
	  		state[1] := 34;
	  	ELSIF state[1] = 35 & NOT GD_OUT_2 THEN
	  		state[1] := 36;
	  	END_IF;
	
		IF state[2] = 2 & NOT GD_OUT_0 THEN
	  		state[2] := 3;
	  	END_IF;
	
		IF state[3] = 2 & NOT GD_OUT_1 THEN
	  		state[3] := 3;
	  	END_IF;
	
		IF state[4] = 2 & GD_OUT_5 THEN
	  		state[4] := 4;
	  	ELSIF state[4] = 5 & NOT GD_OUT_5 THEN
	  		state[4] := 0;
	  	END_IF;
	
		IF state[5] = 2 & GD_OUT_4 THEN
	  		state[5] := 4;
	  	ELSIF state[5] = 5 & NOT GD_OUT_4 THEN
	  		state[5] := 6;
	  	ELSIF state[5] = 7 & GD_OUT_4 THEN
	  		state[5] := 8;
	  	ELSIF state[5] = 9 & NOT GD_OUT_4 THEN
	  		state[5] := 6;
	  	END_IF;
	
		IF state[6] = 1 & NOT GD_OUT_6 THEN
	  		state[6] := 2;
	  	ELSIF state[6] = 3 & GD_OUT_6 THEN
	  		state[6] := 0;
	  	END_IF;
	
		IF state[7] = 1 & INTERN_2 THEN
	  		state[7] := 3;
	  	ELSIF state[7] = 2 & INTERN_3 THEN
	  		state[7] := 4;
	  	ELSIF state[7] = 5 & GD_OUT_10 THEN
	  		state[7] := 9;
	  	ELSIF state[7] = 6 & NOT INTERN_2 THEN
	  		state[7] := 10;
	  	ELSIF state[7] = 7 & GD_OUT_11 THEN
	  		state[7] := 11;
	  	ELSIF state[7] = 9 & NOT INTERN_2 THEN
	  		state[7] := 13;
	  	ELSIF state[7] = 10 & INTERN_3 THEN
	  		state[7] := 8;
	  	ELSIF state[7] = 11 & NOT INTERN_3 THEN
	  		state[7] := 14;
	  	ELSIF state[7] = 12 & GD_OUT_11 THEN
	  		state[7] := 15;
	  	ELSIF state[7] = 15 & NOT INTERN_3 THEN
	  		state[7] := 18;
	  	ELSIF state[7] = 16 & NOT GD_OUT_10 THEN
	  		state[7] := 0;
	  	ELSIF state[7] = 17 & NOT GD_OUT_11 THEN
	  		state[7] := 0;
	  	ELSIF state[7] = 19 & NOT GD_OUT_11 THEN
	  		state[7] := 1;
	  	END_IF;
	
		IF NOT GD_OUT_1 & INTERN_1 THEN
			GD_OUT_1 := 1;
		ELSIF GD_OUT_1 & INTERN_1 THEN
			INTERN_1 := 0;
			INTERN_1_G[0] := 0;
	END_IF;
		IF NOT GD_OUT_0 & INTERN_0 THEN
			GD_OUT_0 := 1;
		ELSIF GD_OUT_0 & INTERN_0 THEN
			INTERN_0 := 0;
			INTERN_0_G[0] := 0;
	END_IF;
		GD_OUT_3 := GD_OUT_2;
	 	GD_OUT_8 := NOT GD_IN_10;
	 	GD_OUT_9 := NOT GD_IN_11;
	 
	END_IF;
END_PROGRAM

CONFIGURATION Config0

	RESOURCE Res0 ON PLC
		TASK task0(INTERVAL := T#20ms,PRIORITY := 0);
		PROGRAM instance0 WITH task0 : supcon;
	END_RESOURCE
END_CONFIGURATION