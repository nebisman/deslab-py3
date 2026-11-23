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
PROGRAM tesis0
	VAR
		random : random_number;
		random_num : DINT;
		initial : BOOL;
		state : ARRAY [0..7] OF DINT;
		slt0 : ARRAY [0..36] OF DINT;
		FE_M1E : F_TRIG;
		FE_M2E : F_TRIG;
		FE_A : F_TRIG;
		FE_PL : F_TRIG;
		FE_PR : F_TRIG;
		INTERN_4 : BOOL;
		INTERN_5 : BOOL;
		INTERN_2 : BOOL;
		INTERN_3 : BOOL;
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
		IF state[0] = 0 & GD_IN_15 THEN
	  		state[0] := 1;
	  	ELSIF state[0] = 2 & FE_A.Q THEN
	  		state[0] := 4;
	  	ELSIF state[0] = 3 & NOT GD_IN_10 THEN
	  		state[0] := 6;
	  	ELSIF state[0] = 3 & FE_PL.Q THEN
	  		state[0] := 7;
	  	ELSIF state[0] = 5 & FE_A.Q THEN
	  		state[0] := 9;
	  	ELSIF state[0] = 5 & NOT GD_IN_10 THEN
	  		state[0] := 10;
	  	ELSIF state[0] = 5 & FE_PL.Q THEN
	  		state[0] := 11;
	  	ELSIF state[0] = 6 & NOT GD_IN_0 THEN
	  		state[0] := 1;
	  	ELSIF state[0] = 8 & FE_M1E.Q THEN
	  		state[0] := 1;
	  	ELSIF state[0] = 9 & NOT GD_IN_10 THEN
	  		state[0] := 15;
	  	ELSIF state[0] = 9 & FE_PL.Q THEN
	  		state[0] := 16;
	  	ELSIF state[0] = 10 & FE_A.Q THEN
	  		state[0] := 15;
	  	ELSIF state[0] = 10 & NOT GD_IN_0 THEN
	  		state[0] := 2;
	  	ELSIF state[0] = 11 & FE_A.Q THEN
	  		state[0] := 16;
	  	ELSIF state[0] = 12 & NOT GD_IN_10 THEN
	  		state[0] := 20;
	  	ELSIF state[0] = 12 & FE_PL.Q THEN
	  		state[0] := 21;
	  	ELSIF state[0] = 13 & NOT GD_IN_11 THEN
	  		state[0] := 22;
	  	ELSIF state[0] = 13 & FE_M2E.Q THEN
	  		state[0] := 1;
	  	ELSIF state[0] = 14 & FE_M1E.Q THEN
	  		state[0] := 3;
	  	ELSIF state[0] = 14 & NOT GD_IN_10 THEN
	  		state[0] := 23;
	  	ELSIF state[0] = 14 & FE_PL.Q THEN
	  		state[0] := 24;
	  	ELSIF state[0] = 15 & NOT GD_IN_0 THEN
	  		state[0] := 4;
	  	ELSIF state[0] = 17 & FE_A.Q THEN
	  		state[0] := 25;
	  	ELSIF state[0] = 17 & NOT GD_IN_10 THEN
	  		state[0] := 28;
	  	ELSIF state[0] = 17 & FE_PL.Q THEN
	  		state[0] := 29;
	  	ELSIF state[0] = 18 & FE_A.Q THEN
	  		state[0] := 26;
	  	ELSIF state[0] = 18 & NOT GD_IN_11 THEN
	  		state[0] := 30;
	  	ELSIF state[0] = 18 & FE_M2E.Q THEN
	  		state[0] := 2;
	  	ELSIF state[0] = 19 & NOT GD_IN_10 THEN
	  		state[0] := 31;
	  	ELSIF state[0] = 19 & NOT GD_IN_11 THEN
	  		state[0] := 32;
	  	ELSIF state[0] = 19 & FE_PL.Q THEN
	  		state[0] := 33;
	  	ELSIF state[0] = 19 & FE_M2E.Q THEN
	  		state[0] := 3;
	  	ELSIF state[0] = 20 & NOT GD_IN_0 THEN
	  		state[0] := 7;
	  	ELSIF state[0] = 22 & FE_M2E.Q THEN
	  		state[0] := 34;
	  	ELSIF state[0] = 23 & FE_M1E.Q THEN
	  		state[0] := 6;
	  	ELSIF state[0] = 23 & NOT GD_IN_0 THEN
	  		state[0] := 8;
	  	ELSIF state[0] = 24 & FE_M1E.Q THEN
	  		state[0] := 7;
	  	ELSIF state[0] = 25 & NOT GD_IN_10 THEN
	  		state[0] := 38;
	  	ELSIF state[0] = 25 & FE_PL.Q THEN
	  		state[0] := 39;
	  	ELSIF state[0] = 26 & NOT GD_IN_11 THEN
	  		state[0] := 40;
	  	ELSIF state[0] = 26 & FE_M2E.Q THEN
	  		state[0] := 4;
	  	ELSIF state[0] = 27 & FE_A.Q THEN
	  		state[0] := 37;
	  	ELSIF state[0] = 27 & NOT GD_IN_10 THEN
	  		state[0] := 41;
	  	ELSIF state[0] = 27 & NOT GD_IN_11 THEN
	  		state[0] := 42;
	  	ELSIF state[0] = 27 & FE_PL.Q THEN
	  		state[0] := 43;
	  	ELSIF state[0] = 27 & FE_M2E.Q THEN
	  		state[0] := 5;
	  	ELSIF state[0] = 28 & FE_A.Q THEN
	  		state[0] := 38;
	  	ELSIF state[0] = 28 & NOT GD_IN_0 THEN
	  		state[0] := 11;
	  	ELSIF state[0] = 29 & FE_A.Q THEN
	  		state[0] := 39;
	  	ELSIF state[0] = 30 & FE_A.Q THEN
	  		state[0] := 40;
	  	ELSIF state[0] = 30 & FE_M2E.Q THEN
	  		state[0] := 44;
	  	ELSIF state[0] = 31 & NOT GD_IN_0 THEN
	  		state[0] := 13;
	  	ELSIF state[0] = 31 & NOT GD_IN_11 THEN
	  		state[0] := 45;
	  	ELSIF state[0] = 31 & FE_M2E.Q THEN
	  		state[0] := 6;
	  	ELSIF state[0] = 32 & NOT GD_IN_10 THEN
	  		state[0] := 45;
	  	ELSIF state[0] = 32 & FE_PL.Q THEN
	  		state[0] := 46;
	  	ELSIF state[0] = 32 & FE_M2E.Q THEN
	  		state[0] := 47;
	  	ELSIF state[0] = 33 & NOT GD_IN_11 THEN
	  		state[0] := 46;
	  	ELSIF state[0] = 33 & FE_M2E.Q THEN
	  		state[0] := 7;
	  	ELSIF state[0] = 35 & FE_M1E.Q THEN
	  		state[0] := 12;
	  	ELSIF state[0] = 35 & NOT GD_IN_10 THEN
	  		state[0] := 50;
	  	ELSIF state[0] = 35 & FE_PL.Q THEN
	  		state[0] := 51;
	  	ELSIF state[0] = 36 & FE_M1E.Q THEN
	  		state[0] := 13;
	  	ELSIF state[0] = 36 & NOT GD_IN_11 THEN
	  		state[0] := 52;
	  	ELSIF state[0] = 36 & FE_M2E.Q THEN
	  		state[0] := 8;
	  	ELSIF state[0] = 37 & NOT GD_IN_10 THEN
	  		state[0] := 53;
	  	ELSIF state[0] = 37 & NOT GD_IN_11 THEN
	  		state[0] := 54;
	  	ELSIF state[0] = 37 & FE_PL.Q THEN
	  		state[0] := 55;
	  	ELSIF state[0] = 37 & FE_M2E.Q THEN
	  		state[0] := 9;
	  	ELSIF state[0] = 38 & NOT GD_IN_0 THEN
	  		state[0] := 16;
	  	ELSIF state[0] = 40 & FE_M2E.Q THEN
	  		state[0] := 56;
	  	ELSIF state[0] = 41 & FE_A.Q THEN
	  		state[0] := 53;
	  	ELSIF state[0] = 41 & NOT GD_IN_0 THEN
	  		state[0] := 18;
	  	ELSIF state[0] = 41 & NOT GD_IN_11 THEN
	  		state[0] := 57;
	  	ELSIF state[0] = 41 & FE_M2E.Q THEN
	  		state[0] := 10;
	  	ELSIF state[0] = 42 & FE_A.Q THEN
	  		state[0] := 54;
	  	ELSIF state[0] = 42 & NOT GD_IN_10 THEN
	  		state[0] := 57;
	  	ELSIF state[0] = 42 & FE_PL.Q THEN
	  		state[0] := 58;
	  	ELSIF state[0] = 42 & FE_M2E.Q THEN
	  		state[0] := 59;
	  	ELSIF state[0] = 43 & FE_A.Q THEN
	  		state[0] := 55;
	  	ELSIF state[0] = 43 & NOT GD_IN_11 THEN
	  		state[0] := 58;
	  	ELSIF state[0] = 43 & FE_M2E.Q THEN
	  		state[0] := 11;
	  	ELSIF state[0] = 44 & FE_A.Q THEN
	  		state[0] := 56;
	  	ELSIF state[0] = 45 & NOT GD_IN_0 THEN
	  		state[0] := 22;
	  	ELSIF state[0] = 45 & FE_M2E.Q THEN
	  		state[0] := 61;
	  	ELSIF state[0] = 46 & FE_M2E.Q THEN
	  		state[0] := 63;
	  	ELSIF state[0] = 47 & NOT GD_IN_10 THEN
	  		state[0] := 61;
	  	ELSIF state[0] = 47 & FE_PL.Q THEN
	  		state[0] := 63;
	  	ELSIF state[0] = 48 & NOT GD_IN_10 THEN
	  		state[0] := 64;
	  	ELSIF state[0] = 48 & NOT GD_IN_11 THEN
	  		state[0] := 62;
	  	ELSIF state[0] = 48 & FE_PL.Q THEN
	  		state[0] := 65;
	  	ELSIF state[0] = 48 & FE_M2E.Q THEN
	  		state[0] := 12;
	  	ELSIF state[0] = 49 & FE_M1E.Q THEN
	  		state[0] := 19;
	  	ELSIF state[0] = 49 & NOT GD_IN_10 THEN
	  		state[0] := 66;
	  	ELSIF state[0] = 49 & NOT GD_IN_11 THEN
	  		state[0] := 67;
	  	ELSIF state[0] = 49 & FE_PL.Q THEN
	  		state[0] := 68;
	  	ELSIF state[0] = 49 & FE_M2E.Q THEN
	  		state[0] := 14;
	  	ELSIF state[0] = 50 & FE_M1E.Q THEN
	  		state[0] := 20;
	  	ELSIF state[0] = 50 & NOT GD_IN_0 THEN
	  		state[0] := 24;
	  	ELSIF state[0] = 51 & FE_M1E.Q THEN
	  		state[0] := 21;
	  	ELSIF state[0] = 52 & FE_M1E.Q THEN
	  		state[0] := 22;
	  	ELSIF state[0] = 52 & FE_M2E.Q THEN
	  		state[0] := 69;
	  	ELSIF state[0] = 53 & NOT GD_IN_0 THEN
	  		state[0] := 26;
	  	ELSIF state[0] = 53 & NOT GD_IN_11 THEN
	  		state[0] := 70;
	  	ELSIF state[0] = 53 & FE_M2E.Q THEN
	  		state[0] := 15;
	  	ELSIF state[0] = 54 & NOT GD_IN_10 THEN
	  		state[0] := 70;
	  	ELSIF state[0] = 54 & FE_PL.Q THEN
	  		state[0] := 71;
	  	ELSIF state[0] = 54 & FE_M2E.Q THEN
	  		state[0] := 72;
	  	ELSIF state[0] = 55 & NOT GD_IN_11 THEN
	  		state[0] := 71;
	  	ELSIF state[0] = 55 & FE_M2E.Q THEN
	  		state[0] := 16;
	  	ELSIF state[0] = 57 & FE_A.Q THEN
	  		state[0] := 70;
	  	ELSIF state[0] = 57 & NOT GD_IN_0 THEN
	  		state[0] := 30;
	  	ELSIF state[0] = 57 & FE_M2E.Q THEN
	  		state[0] := 74;
	  	ELSIF state[0] = 58 & FE_A.Q THEN
	  		state[0] := 71;
	  	ELSIF state[0] = 58 & FE_M2E.Q THEN
	  		state[0] := 76;
	  	ELSIF state[0] = 59 & FE_A.Q THEN
	  		state[0] := 72;
	  	ELSIF state[0] = 59 & NOT GD_IN_10 THEN
	  		state[0] := 74;
	  	ELSIF state[0] = 59 & FE_PL.Q THEN
	  		state[0] := 76;
	  	ELSIF state[0] = 60 & FE_A.Q THEN
	  		state[0] := 73;
	  	ELSIF state[0] = 60 & NOT GD_IN_10 THEN
	  		state[0] := 77;
	  	ELSIF state[0] = 60 & NOT GD_IN_11 THEN
	  		state[0] := 75;
	  	ELSIF state[0] = 60 & FE_PL.Q THEN
	  		state[0] := 78;
	  	ELSIF state[0] = 60 & FE_M2E.Q THEN
	  		state[0] := 17;
	  	ELSIF state[0] = 61 & NOT GD_IN_0 THEN
	  		state[0] := 34;
	  	ELSIF state[0] = 62 & NOT GD_IN_10 THEN
	  		state[0] := 79;
	  	ELSIF state[0] = 62 & FE_PL.Q THEN
	  		state[0] := 80;
	  	ELSIF state[0] = 62 & FE_M2E.Q THEN
	  		state[0] := 81;
	  	ELSIF state[0] = 64 & NOT GD_IN_0 THEN
	  		state[0] := 33;
	  	ELSIF state[0] = 64 & NOT GD_IN_11 THEN
	  		state[0] := 79;
	  	ELSIF state[0] = 64 & FE_M2E.Q THEN
	  		state[0] := 20;
	  	ELSIF state[0] = 65 & NOT GD_IN_11 THEN
	  		state[0] := 80;
	  	ELSIF state[0] = 65 & FE_M2E.Q THEN
	  		state[0] := 21;
	  	ELSIF state[0] = 66 & FE_M1E.Q THEN
	  		state[0] := 31;
	  	ELSIF state[0] = 66 & NOT GD_IN_0 THEN
	  		state[0] := 36;
	  	ELSIF state[0] = 66 & NOT GD_IN_11 THEN
	  		state[0] := 83;
	  	ELSIF state[0] = 66 & FE_M2E.Q THEN
	  		state[0] := 23;
	  	ELSIF state[0] = 67 & FE_M1E.Q THEN
	  		state[0] := 32;
	  	ELSIF state[0] = 67 & NOT GD_IN_10 THEN
	  		state[0] := 83;
	  	ELSIF state[0] = 67 & FE_PL.Q THEN
	  		state[0] := 84;
	  	ELSIF state[0] = 67 & FE_M2E.Q THEN
	  		state[0] := 85;
	  	ELSIF state[0] = 68 & FE_M1E.Q THEN
	  		state[0] := 33;
	  	ELSIF state[0] = 68 & NOT GD_IN_11 THEN
	  		state[0] := 84;
	  	ELSIF state[0] = 68 & FE_M2E.Q THEN
	  		state[0] := 24;
	  	ELSIF state[0] = 69 & FE_M1E.Q THEN
	  		state[0] := 34;
	  	ELSIF state[0] = 70 & NOT GD_IN_0 THEN
	  		state[0] := 40;
	  	ELSIF state[0] = 70 & FE_M2E.Q THEN
	  		state[0] := 87;
	  	ELSIF state[0] = 71 & FE_M2E.Q THEN
	  		state[0] := 89;
	  	ELSIF state[0] = 72 & NOT GD_IN_10 THEN
	  		state[0] := 87;
	  	ELSIF state[0] = 72 & FE_PL.Q THEN
	  		state[0] := 89;
	  	ELSIF state[0] = 73 & NOT GD_IN_10 THEN
	  		state[0] := 90;
	  	ELSIF state[0] = 73 & NOT GD_IN_11 THEN
	  		state[0] := 88;
	  	ELSIF state[0] = 73 & FE_PL.Q THEN
	  		state[0] := 91;
	  	ELSIF state[0] = 73 & FE_M2E.Q THEN
	  		state[0] := 25;
	  	ELSIF state[0] = 74 & FE_A.Q THEN
	  		state[0] := 87;
	  	ELSIF state[0] = 74 & NOT GD_IN_0 THEN
	  		state[0] := 44;
	  	ELSIF state[0] = 75 & FE_A.Q THEN
	  		state[0] := 88;
	  	ELSIF state[0] = 75 & NOT GD_IN_10 THEN
	  		state[0] := 92;
	  	ELSIF state[0] = 75 & FE_PL.Q THEN
	  		state[0] := 93;
	  	ELSIF state[0] = 75 & FE_M2E.Q THEN
	  		state[0] := 94;
	  	ELSIF state[0] = 76 & FE_A.Q THEN
	  		state[0] := 89;
	  	ELSIF state[0] = 77 & FE_A.Q THEN
	  		state[0] := 90;
	  	ELSIF state[0] = 77 & NOT GD_IN_0 THEN
	  		state[0] := 43;
	  	ELSIF state[0] = 77 & NOT GD_IN_11 THEN
	  		state[0] := 92;
	  	ELSIF state[0] = 77 & FE_M2E.Q THEN
	  		state[0] := 28;
	  	ELSIF state[0] = 78 & FE_A.Q THEN
	  		state[0] := 91;
	  	ELSIF state[0] = 78 & NOT GD_IN_11 THEN
	  		state[0] := 93;
	  	ELSIF state[0] = 78 & FE_M2E.Q THEN
	  		state[0] := 29;
	  	ELSIF state[0] = 79 & NOT GD_IN_0 THEN
	  		state[0] := 46;
	  	ELSIF state[0] = 79 & FE_M2E.Q THEN
	  		state[0] := 96;
	  	ELSIF state[0] = 80 & FE_M2E.Q THEN
	  		state[0] := 97;
	  	ELSIF state[0] = 81 & NOT GD_IN_10 THEN
	  		state[0] := 96;
	  	ELSIF state[0] = 81 & FE_PL.Q THEN
	  		state[0] := 97;
	  	ELSIF state[0] = 82 & NOT GD_IN_11 THEN
	  		state[0] := 22;
	  	ELSIF state[0] = 82 & FE_M2E.Q THEN
	  		state[0] := 34;
	  	ELSIF state[0] = 83 & FE_M1E.Q THEN
	  		state[0] := 45;
	  	ELSIF state[0] = 83 & NOT GD_IN_0 THEN
	  		state[0] := 52;
	  	ELSIF state[0] = 83 & FE_M2E.Q THEN
	  		state[0] := 99;
	  	ELSIF state[0] = 84 & FE_M1E.Q THEN
	  		state[0] := 46;
	  	ELSIF state[0] = 84 & FE_M2E.Q THEN
	  		state[0] := 101;
	  	ELSIF state[0] = 85 & FE_M1E.Q THEN
	  		state[0] := 47;
	  	ELSIF state[0] = 85 & NOT GD_IN_10 THEN
	  		state[0] := 99;
	  	ELSIF state[0] = 85 & FE_PL.Q THEN
	  		state[0] := 101;
	  	ELSIF state[0] = 86 & FE_M1E.Q THEN
	  		state[0] := 48;
	  	ELSIF state[0] = 86 & NOT GD_IN_10 THEN
	  		state[0] := 102;
	  	ELSIF state[0] = 86 & NOT GD_IN_11 THEN
	  		state[0] := 100;
	  	ELSIF state[0] = 86 & FE_PL.Q THEN
	  		state[0] := 103;
	  	ELSIF state[0] = 86 & FE_M2E.Q THEN
	  		state[0] := 35;
	  	ELSIF state[0] = 87 & NOT GD_IN_0 THEN
	  		state[0] := 56;
	  	ELSIF state[0] = 88 & NOT GD_IN_10 THEN
	  		state[0] := 104;
	  	ELSIF state[0] = 88 & FE_PL.Q THEN
	  		state[0] := 105;
	  	ELSIF state[0] = 88 & FE_M2E.Q THEN
	  		state[0] := 106;
	  	ELSIF state[0] = 90 & NOT GD_IN_0 THEN
	  		state[0] := 55;
	  	ELSIF state[0] = 90 & NOT GD_IN_11 THEN
	  		state[0] := 104;
	  	ELSIF state[0] = 90 & FE_M2E.Q THEN
	  		state[0] := 38;
	  	ELSIF state[0] = 91 & NOT GD_IN_11 THEN
	  		state[0] := 105;
	  	ELSIF state[0] = 91 & FE_M2E.Q THEN
	  		state[0] := 39;
	  	ELSIF state[0] = 92 & FE_A.Q THEN
	  		state[0] := 104;
	  	ELSIF state[0] = 92 & NOT GD_IN_0 THEN
	  		state[0] := 58;
	  	ELSIF state[0] = 92 & FE_M2E.Q THEN
	  		state[0] := 108;
	  	ELSIF state[0] = 93 & FE_A.Q THEN
	  		state[0] := 105;
	  	ELSIF state[0] = 93 & FE_M2E.Q THEN
	  		state[0] := 109;
	  	ELSIF state[0] = 94 & FE_A.Q THEN
	  		state[0] := 106;
	  	ELSIF state[0] = 94 & NOT GD_IN_10 THEN
	  		state[0] := 108;
	  	ELSIF state[0] = 94 & FE_PL.Q THEN
	  		state[0] := 109;
	  	ELSIF state[0] = 95 & FE_A.Q THEN
	  		state[0] := 107;
	  	ELSIF state[0] = 95 & NOT GD_IN_11 THEN
	  		state[0] := 30;
	  	ELSIF state[0] = 95 & FE_M2E.Q THEN
	  		state[0] := 44;
	  	ELSIF state[0] = 96 & NOT GD_IN_0 THEN
	  		state[0] := 63;
	  	ELSIF state[0] = 98 & NOT GD_IN_10 THEN
	  		state[0] := 111;
	  	ELSIF state[0] = 98 & NOT GD_IN_11 THEN
	  		state[0] := 32;
	  	ELSIF state[0] = 98 & FE_PL.Q THEN
	  		state[0] := 112;
	  	ELSIF state[0] = 98 & FE_M2E.Q THEN
	  		state[0] := 47;
	  	ELSIF state[0] = 99 & FE_M1E.Q THEN
	  		state[0] := 61;
	  	ELSIF state[0] = 99 & NOT GD_IN_0 THEN
	  		state[0] := 69;
	  	ELSIF state[0] = 100 & FE_M1E.Q THEN
	  		state[0] := 62;
	  	ELSIF state[0] = 100 & NOT GD_IN_10 THEN
	  		state[0] := 113;
	  	ELSIF state[0] = 100 & FE_PL.Q THEN
	  		state[0] := 114;
	  	ELSIF state[0] = 100 & FE_M2E.Q THEN
	  		state[0] := 115;
	  	ELSIF state[0] = 101 & FE_M1E.Q THEN
	  		state[0] := 63;
	  	ELSIF state[0] = 102 & FE_M1E.Q THEN
	  		state[0] := 64;
	  	ELSIF state[0] = 102 & NOT GD_IN_0 THEN
	  		state[0] := 68;
	  	ELSIF state[0] = 102 & NOT GD_IN_11 THEN
	  		state[0] := 113;
	  	ELSIF state[0] = 102 & FE_M2E.Q THEN
	  		state[0] := 50;
	  	ELSIF state[0] = 103 & FE_M1E.Q THEN
	  		state[0] := 65;
	  	ELSIF state[0] = 103 & NOT GD_IN_11 THEN
	  		state[0] := 114;
	  	ELSIF state[0] = 103 & FE_M2E.Q THEN
	  		state[0] := 51;
	  	ELSIF state[0] = 104 & NOT GD_IN_0 THEN
	  		state[0] := 71;
	  	ELSIF state[0] = 104 & FE_M2E.Q THEN
	  		state[0] := 117;
	  	ELSIF state[0] = 105 & FE_M2E.Q THEN
	  		state[0] := 118;
	  	ELSIF state[0] = 106 & NOT GD_IN_10 THEN
	  		state[0] := 117;
	  	ELSIF state[0] = 106 & FE_PL.Q THEN
	  		state[0] := 118;
	  	ELSIF state[0] = 107 & NOT GD_IN_11 THEN
	  		state[0] := 40;
	  	ELSIF state[0] = 107 & FE_M2E.Q THEN
	  		state[0] := 56;
	  	ELSIF state[0] = 108 & FE_A.Q THEN
	  		state[0] := 117;
	  	ELSIF state[0] = 108 & NOT GD_IN_0 THEN
	  		state[0] := 76;
	  	ELSIF state[0] = 109 & FE_A.Q THEN
	  		state[0] := 118;
	  	ELSIF state[0] = 110 & FE_A.Q THEN
	  		state[0] := 119;
	  	ELSIF state[0] = 110 & NOT GD_IN_10 THEN
	  		state[0] := 120;
	  	ELSIF state[0] = 110 & NOT GD_IN_11 THEN
	  		state[0] := 42;
	  	ELSIF state[0] = 110 & FE_PL.Q THEN
	  		state[0] := 121;
	  	ELSIF state[0] = 110 & FE_M2E.Q THEN
	  		state[0] := 59;
	  	ELSIF state[0] = 111 & NOT GD_IN_0 THEN
	  		state[0] := 82;
	  	ELSIF state[0] = 111 & NOT GD_IN_11 THEN
	  		state[0] := 45;
	  	ELSIF state[0] = 111 & FE_M2E.Q THEN
	  		state[0] := 61;
	  	ELSIF state[0] = 112 & NOT GD_IN_11 THEN
	  		state[0] := 46;
	  	ELSIF state[0] = 112 & FE_M2E.Q THEN
	  		state[0] := 63;
	  	ELSIF state[0] = 113 & FE_M1E.Q THEN
	  		state[0] := 79;
	  	ELSIF state[0] = 113 & NOT GD_IN_0 THEN
	  		state[0] := 84;
	  	ELSIF state[0] = 113 & FE_M2E.Q THEN
	  		state[0] := 123;
	  	ELSIF state[0] = 114 & FE_M1E.Q THEN
	  		state[0] := 80;
	  	ELSIF state[0] = 114 & FE_M2E.Q THEN
	  		state[0] := 124;
	  	ELSIF state[0] = 115 & FE_M1E.Q THEN
	  		state[0] := 81;
	  	ELSIF state[0] = 115 & NOT GD_IN_10 THEN
	  		state[0] := 123;
	  	ELSIF state[0] = 115 & FE_PL.Q THEN
	  		state[0] := 124;
	  	ELSIF state[0] = 116 & FE_M1E.Q THEN
	  		state[0] := 82;
	  	ELSIF state[0] = 116 & NOT GD_IN_11 THEN
	  		state[0] := 52;
	  	ELSIF state[0] = 116 & FE_M2E.Q THEN
	  		state[0] := 69;
	  	ELSIF state[0] = 117 & NOT GD_IN_0 THEN
	  		state[0] := 89;
	  	ELSIF state[0] = 119 & NOT GD_IN_10 THEN
	  		state[0] := 126;
	  	ELSIF state[0] = 119 & NOT GD_IN_11 THEN
	  		state[0] := 54;
	  	ELSIF state[0] = 119 & FE_PL.Q THEN
	  		state[0] := 127;
	  	ELSIF state[0] = 119 & FE_M2E.Q THEN
	  		state[0] := 72;
	  	ELSIF state[0] = 120 & FE_A.Q THEN
	  		state[0] := 126;
	  	ELSIF state[0] = 120 & NOT GD_IN_0 THEN
	  		state[0] := 95;
	  	ELSIF state[0] = 120 & NOT GD_IN_11 THEN
	  		state[0] := 57;
	  	ELSIF state[0] = 120 & FE_M2E.Q THEN
	  		state[0] := 74;
	  	ELSIF state[0] = 121 & FE_A.Q THEN
	  		state[0] := 127;
	  	ELSIF state[0] = 121 & NOT GD_IN_11 THEN
	  		state[0] := 58;
	  	ELSIF state[0] = 121 & FE_M2E.Q THEN
	  		state[0] := 76;
	  	ELSIF state[0] = 122 & NOT GD_IN_10 THEN
	  		state[0] := 129;
	  	ELSIF state[0] = 122 & NOT GD_IN_11 THEN
	  		state[0] := 62;
	  	ELSIF state[0] = 122 & FE_PL.Q THEN
	  		state[0] := 130;
	  	ELSIF state[0] = 122 & FE_M2E.Q THEN
	  		state[0] := 81;
	  	ELSIF state[0] = 123 & FE_M1E.Q THEN
	  		state[0] := 96;
	  	ELSIF state[0] = 123 & NOT GD_IN_0 THEN
	  		state[0] := 101;
	  	ELSIF state[0] = 124 & FE_M1E.Q THEN
	  		state[0] := 97;
	  	ELSIF state[0] = 125 & FE_M1E.Q THEN
	  		state[0] := 98;
	  	ELSIF state[0] = 125 & NOT GD_IN_10 THEN
	  		state[0] := 131;
	  	ELSIF state[0] = 125 & NOT GD_IN_11 THEN
	  		state[0] := 67;
	  	ELSIF state[0] = 125 & FE_PL.Q THEN
	  		state[0] := 132;
	  	ELSIF state[0] = 125 & FE_M2E.Q THEN
	  		state[0] := 85;
	  	ELSIF state[0] = 126 & NOT GD_IN_0 THEN
	  		state[0] := 107;
	  	ELSIF state[0] = 126 & NOT GD_IN_11 THEN
	  		state[0] := 70;
	  	ELSIF state[0] = 126 & FE_M2E.Q THEN
	  		state[0] := 87;
	  	ELSIF state[0] = 127 & NOT GD_IN_11 THEN
	  		state[0] := 71;
	  	ELSIF state[0] = 127 & FE_M2E.Q THEN
	  		state[0] := 89;
	  	ELSIF state[0] = 128 & FE_A.Q THEN
	  		state[0] := 133;
	  	ELSIF state[0] = 128 & NOT GD_IN_10 THEN
	  		state[0] := 134;
	  	ELSIF state[0] = 128 & NOT GD_IN_11 THEN
	  		state[0] := 75;
	  	ELSIF state[0] = 128 & FE_PL.Q THEN
	  		state[0] := 135;
	  	ELSIF state[0] = 128 & FE_M2E.Q THEN
	  		state[0] := 94;
	  	ELSIF state[0] = 129 & NOT GD_IN_0 THEN
	  		state[0] := 112;
	  	ELSIF state[0] = 129 & NOT GD_IN_11 THEN
	  		state[0] := 79;
	  	ELSIF state[0] = 129 & FE_M2E.Q THEN
	  		state[0] := 96;
	  	ELSIF state[0] = 130 & NOT GD_IN_11 THEN
	  		state[0] := 80;
	  	ELSIF state[0] = 130 & FE_M2E.Q THEN
	  		state[0] := 97;
	  	ELSIF state[0] = 131 & FE_M1E.Q THEN
	  		state[0] := 111;
	  	ELSIF state[0] = 131 & NOT GD_IN_0 THEN
	  		state[0] := 116;
	  	ELSIF state[0] = 131 & NOT GD_IN_11 THEN
	  		state[0] := 83;
	  	ELSIF state[0] = 131 & FE_M2E.Q THEN
	  		state[0] := 99;
	  	ELSIF state[0] = 132 & FE_M1E.Q THEN
	  		state[0] := 112;
	  	ELSIF state[0] = 132 & NOT GD_IN_11 THEN
	  		state[0] := 84;
	  	ELSIF state[0] = 132 & FE_M2E.Q THEN
	  		state[0] := 101;
	  	ELSIF state[0] = 133 & NOT GD_IN_10 THEN
	  		state[0] := 137;
	  	ELSIF state[0] = 133 & NOT GD_IN_11 THEN
	  		state[0] := 88;
	  	ELSIF state[0] = 133 & FE_PL.Q THEN
	  		state[0] := 138;
	  	ELSIF state[0] = 133 & FE_M2E.Q THEN
	  		state[0] := 106;
	  	ELSIF state[0] = 134 & FE_A.Q THEN
	  		state[0] := 137;
	  	ELSIF state[0] = 134 & NOT GD_IN_0 THEN
	  		state[0] := 121;
	  	ELSIF state[0] = 134 & NOT GD_IN_11 THEN
	  		state[0] := 92;
	  	ELSIF state[0] = 134 & FE_M2E.Q THEN
	  		state[0] := 108;
	  	ELSIF state[0] = 135 & FE_A.Q THEN
	  		state[0] := 138;
	  	ELSIF state[0] = 135 & NOT GD_IN_11 THEN
	  		state[0] := 93;
	  	ELSIF state[0] = 135 & FE_M2E.Q THEN
	  		state[0] := 109;
	  	ELSIF state[0] = 136 & FE_M1E.Q THEN
	  		state[0] := 122;
	  	ELSIF state[0] = 136 & NOT GD_IN_10 THEN
	  		state[0] := 139;
	  	ELSIF state[0] = 136 & NOT GD_IN_11 THEN
	  		state[0] := 100;
	  	ELSIF state[0] = 136 & FE_PL.Q THEN
	  		state[0] := 140;
	  	ELSIF state[0] = 136 & FE_M2E.Q THEN
	  		state[0] := 115;
	  	ELSIF state[0] = 137 & NOT GD_IN_0 THEN
	  		state[0] := 127;
	  	ELSIF state[0] = 137 & NOT GD_IN_11 THEN
	  		state[0] := 104;
	  	ELSIF state[0] = 137 & FE_M2E.Q THEN
	  		state[0] := 117;
	  	ELSIF state[0] = 138 & NOT GD_IN_11 THEN
	  		state[0] := 105;
	  	ELSIF state[0] = 138 & FE_M2E.Q THEN
	  		state[0] := 118;
	  	ELSIF state[0] = 139 & FE_M1E.Q THEN
	  		state[0] := 129;
	  	ELSIF state[0] = 139 & NOT GD_IN_0 THEN
	  		state[0] := 132;
	  	ELSIF state[0] = 139 & NOT GD_IN_11 THEN
	  		state[0] := 113;
	  	ELSIF state[0] = 139 & FE_M2E.Q THEN
	  		state[0] := 123;
	  	ELSIF state[0] = 140 & FE_M1E.Q THEN
	  		state[0] := 130;
	  	ELSIF state[0] = 140 & NOT GD_IN_11 THEN
	  		state[0] := 114;
	  	ELSIF state[0] = 140 & FE_M2E.Q THEN
	  		state[0] := 124;
	  	END_IF;
	
		IF state[1] = 0 & GD_OUT_0 THEN
	  		state[1] := 1;
	  	ELSIF state[1] = 1 & GD_IN_0 THEN
	  		state[1] := 2;
	  	ELSIF state[1] = 3 & FE_M1E.Q THEN
	  		state[1] := 0;
	  	END_IF;
	
		IF state[2] = 0 & GD_OUT_1 THEN
	  		state[2] := 1;
	  	ELSIF state[2] = 1 & GD_IN_1 THEN
	  		state[2] := 2;
	  	ELSIF state[2] = 3 & FE_M2E.Q THEN
	  		state[2] := 0;
	  	END_IF;
	
		IF state[3] = 0 & GD_IN_0 THEN
	  		state[3] := 1;
	  	ELSIF state[3] = 1 & FE_M1E.Q THEN
	  		state[3] := 2;
	  	ELSIF state[3] = 1 & NOT GD_IN_10 THEN
	  		state[3] := 3;
	  	ELSIF state[3] = 3 & FE_M1E.Q THEN
	  		state[3] := 0;
	  	ELSIF state[3] = 4 & FE_PL.Q THEN
	  		state[3] := 5;
	  	END_IF;
	
		IF state[4] = 0 & GD_IN_15 THEN
	  		state[4] := 1;
	  	ELSIF state[4] = 1 & FE_M1E.Q THEN
	  		state[4] := 2;
	  	ELSIF state[4] = 1 & NOT GD_IN_10 THEN
	  		state[4] := 3;
	  	ELSIF state[4] = 3 & FE_M1E.Q THEN
	  		state[4] := 1;
	  	ELSIF state[4] = 4 & FE_PR.Q THEN
	  		state[4] := 5;
	  	ELSIF state[4] = 6 & FE_M1E.Q THEN
	  		state[4] := 7;
	  	ELSIF state[4] = 6 & FE_M2E.Q THEN
	  		state[4] := 2;
	  	ELSIF state[4] = 8 & FE_PL.Q THEN
	  		state[4] := 9;
	  	ELSIF state[4] = 8 & FE_M2E.Q THEN
	  		state[4] := 2;
	  	END_IF;
	
		IF state[5] = 0 & FE_M2E.Q THEN
	  		state[5] := 1;
	  	ELSIF state[5] = 2 & FE_PR.Q THEN
	  		state[5] := 3;
	  	END_IF;
	
		IF state[6] = 0 & NOT GD_IN_10 THEN
	  		state[6] := 1;
	  	ELSIF state[6] = 0 & NOT GD_IN_11 THEN
	  		state[6] := 2;
	  	ELSIF state[6] = 3 & GD_IN_12 THEN
	  		state[6] := 5;
	  	ELSIF state[6] = 3 & NOT GD_IN_11 THEN
	  		state[6] := 6;
	  	ELSIF state[6] = 4 & GD_IN_13 THEN
	  		state[6] := 7;
	  	ELSIF state[6] = 4 & NOT GD_IN_10 THEN
	  		state[6] := 8;
	  	ELSIF state[6] = 8 & GD_IN_13 THEN
	  		state[6] := 12;
	  	ELSIF state[6] = 13 & NOT GD_IN_0 THEN
	  		state[6] := 16;
	  	ELSIF state[6] = 14 & FE_M2E.Q THEN
	  		state[6] := 17;
	  	ELSIF state[6] = 18 & FE_M2E.Q THEN
	  		state[6] := 19;
	  	END_IF;
	
	
		CASE state[0] OF
	  		1:
	  			CASE slt0[0] OF
	  				0:
	  					GD_OUT_2 := 1;
	  				1:
	  					GD_OUT_0 := 1;
	  			END_CASE;
	  			slt0[0] := (random_num + slt0[0]) MOD 2;
	  			random_num := random_num - slt0[0];
	 		2:
	  			GD_OUT_0 := 1;
			3:
	  			GD_OUT_2 := 1;
			4:
	  			CASE slt0[1] OF
	  				0:
	  					GD_OUT_2 := 0;
	  				1:
	  					GD_OUT_0 := 1;
	  			END_CASE;
	  			slt0[1] := (random_num + slt0[1]) MOD 2;
	  			random_num := random_num - slt0[1];
	 		6:
	  			GD_OUT_2 := 1;
			7:
	  			CASE slt0[2] OF
	  				0:
	  					GD_OUT_2 := 1;
	  				1:
	  					GD_OUT_0 := 1;
	  				2:
	  					GD_OUT_1 := 1;
	  			END_CASE;
	  			slt0[2] := (random_num + slt0[2]) MOD 3;
	  			random_num := random_num - slt0[2];
	 		8:
	  			GD_OUT_0 := 1;
			9:
	  			GD_OUT_2 := 0;
	  		11:
	  			CASE slt0[3] OF
	  				0:
	  					GD_OUT_0 := 1;
	  				1:
	  					GD_OUT_1 := 1;
	  			END_CASE;
	  			slt0[3] := (random_num + slt0[3]) MOD 2;
	  			random_num := random_num - slt0[3];
	 		12:
	  			CASE slt0[4] OF
	  				0:
	  					GD_OUT_2 := 1;
	  				1:
	  					GD_OUT_1 := 1;
	  			END_CASE;
	  			slt0[4] := (random_num + slt0[4]) MOD 2;
	  			random_num := random_num - slt0[4];
	 		13:
	  			CASE slt0[5] OF
	  				0:
	  					GD_OUT_2 := 1;
	  				1:
	  					GD_OUT_0 := 1;
	  			END_CASE;
	  			slt0[5] := (random_num + slt0[5]) MOD 2;
	  			random_num := random_num - slt0[5];
	 		15:
	  			GD_OUT_2 := 0;
	  		16:
	  			CASE slt0[6] OF
	  				0:
	  					GD_OUT_2 := 0;
	  				1:
	  					GD_OUT_0 := 1;
	  				2:
	  					GD_OUT_1 := 1;
	  			END_CASE;
	  			slt0[6] := (random_num + slt0[6]) MOD 3;
	  			random_num := random_num - slt0[6];
	 		17:
	  			GD_OUT_1 := 1;
			18:
	  			GD_OUT_0 := 1;
			19:
	  			GD_OUT_2 := 1;
			20:
	  			CASE slt0[7] OF
	  				0:
	  					GD_OUT_2 := 1;
	  				1:
	  					GD_OUT_1 := 1;
	  			END_CASE;
	  			slt0[7] := (random_num + slt0[7]) MOD 2;
	  			random_num := random_num - slt0[7];
	 		21:
	  			CASE slt0[8] OF
	  				0:
	  					GD_OUT_2 := 1;
	  				1:
	  					GD_OUT_1 := 1;
	  			END_CASE;
	  			slt0[8] := (random_num + slt0[8]) MOD 2;
	  			random_num := random_num - slt0[8];
	 		22:
	  			CASE slt0[9] OF
	  				0:
	  					GD_OUT_2 := 1;
	  				1:
	  					GD_OUT_0 := 1;
	  			END_CASE;
	  			slt0[9] := (random_num + slt0[9]) MOD 2;
	  			random_num := random_num - slt0[9];
	 		24:
	  			CASE slt0[10] OF
	  				0:
	  					GD_OUT_0 := 1;
	  				1:
	  					GD_OUT_1 := 1;
	  			END_CASE;
	  			slt0[10] := (random_num + slt0[10]) MOD 2;
	  			random_num := random_num - slt0[10];
	 		25:
	  			CASE slt0[11] OF
	  				0:
	  					GD_OUT_2 := 0;
	  				1:
	  					GD_OUT_1 := 1;
	  			END_CASE;
	  			slt0[11] := (random_num + slt0[11]) MOD 2;
	  			random_num := random_num - slt0[11];
	 		26:
	  			CASE slt0[12] OF
	  				0:
	  					GD_OUT_2 := 0;
	  				1:
	  					GD_OUT_0 := 1;
	  			END_CASE;
	  			slt0[12] := (random_num + slt0[12]) MOD 2;
	  			random_num := random_num - slt0[12];
	 		28:
	  			GD_OUT_1 := 1;
			29:
	  			GD_OUT_1 := 1;
			30:
	  			GD_OUT_0 := 1;
			31:
	  			GD_OUT_2 := 1;
			32:
	  			GD_OUT_2 := 1;
			33:
	  			CASE slt0[13] OF
	  				0:
	  					GD_OUT_2 := 1;
	  				1:
	  					GD_OUT_0 := 1;
	  			END_CASE;
	  			slt0[13] := (random_num + slt0[13]) MOD 2;
	  			random_num := random_num - slt0[13];
	 		34:
	  			CASE slt0[14] OF
	  				0:
	  					GD_OUT_2 := 1;
	  				1:
	  					GD_OUT_0 := 1;
	  			END_CASE;
	  			slt0[14] := (random_num + slt0[14]) MOD 2;
	  			random_num := random_num - slt0[14];
	 		35:
	  			GD_OUT_1 := 1;
			36:
	  			GD_OUT_0 := 1;
			37:
	  			GD_OUT_2 := 0;
	  		38:
	  			CASE slt0[15] OF
	  				0:
	  					GD_OUT_2 := 0;
	  				1:
	  					GD_OUT_1 := 1;
	  			END_CASE;
	  			slt0[15] := (random_num + slt0[15]) MOD 2;
	  			random_num := random_num - slt0[15];
	 		39:
	  			CASE slt0[16] OF
	  				0:
	  					GD_OUT_2 := 0;
	  				1:
	  					GD_OUT_1 := 1;
	  			END_CASE;
	  			slt0[16] := (random_num + slt0[16]) MOD 2;
	  			random_num := random_num - slt0[16];
	 		40:
	  			CASE slt0[17] OF
	  				0:
	  					GD_OUT_2 := 0;
	  				1:
	  					GD_OUT_0 := 1;
	  			END_CASE;
	  			slt0[17] := (random_num + slt0[17]) MOD 2;
	  			random_num := random_num - slt0[17];
	 		43:
	  			GD_OUT_0 := 1;
			44:
	  			GD_OUT_0 := 1;
			45:
	  			GD_OUT_2 := 1;
			46:
	  			CASE slt0[18] OF
	  				0:
	  					GD_OUT_2 := 1;
	  				1:
	  					GD_OUT_0 := 1;
	  			END_CASE;
	  			slt0[18] := (random_num + slt0[18]) MOD 2;
	  			random_num := random_num - slt0[18];
	 		47:
	  			GD_OUT_2 := 1;
			48:
	  			GD_OUT_2 := 1;
			50:
	  			GD_OUT_1 := 1;
			51:
	  			GD_OUT_1 := 1;
			52:
	  			GD_OUT_0 := 1;
			53:
	  			GD_OUT_2 := 0;
	  		54:
	  			GD_OUT_2 := 0;
	  		55:
	  			CASE slt0[19] OF
	  				0:
	  					GD_OUT_2 := 0;
	  				1:
	  					GD_OUT_0 := 1;
	  			END_CASE;
	  			slt0[19] := (random_num + slt0[19]) MOD 2;
	  			random_num := random_num - slt0[19];
	 		56:
	  			CASE slt0[20] OF
	  				0:
	  					GD_OUT_2 := 0;
	  				1:
	  					GD_OUT_0 := 1;
	  			END_CASE;
	  			slt0[20] := (random_num + slt0[20]) MOD 2;
	  			random_num := random_num - slt0[20];
	 		58:
	  			GD_OUT_0 := 1;
			61:
	  			GD_OUT_2 := 1;
			62:
	  			GD_OUT_2 := 1;
			63:
	  			CASE slt0[21] OF
	  				0:
	  					GD_OUT_2 := 1;
	  				1:
	  					GD_OUT_0 := 1;
	  				2:
	  					GD_OUT_1 := 1;
	  			END_CASE;
	  			slt0[21] := (random_num + slt0[21]) MOD 3;
	  			random_num := random_num - slt0[21];
	 		64:
	  			GD_OUT_2 := 1;
			65:
	  			GD_OUT_2 := 1;
			68:
	  			GD_OUT_0 := 1;
			69:
	  			GD_OUT_0 := 1;
			70:
	  			GD_OUT_2 := 0;
	  		71:
	  			CASE slt0[22] OF
	  				0:
	  					GD_OUT_2 := 0;
	  				1:
	  					GD_OUT_0 := 1;
	  			END_CASE;
	  			slt0[22] := (random_num + slt0[22]) MOD 2;
	  			random_num := random_num - slt0[22];
	 		72:
	  			GD_OUT_2 := 0;
	  		73:
	  			GD_OUT_2 := 0;
	  		76:
	  			CASE slt0[23] OF
	  				0:
	  					GD_OUT_0 := 1;
	  				1:
	  					GD_OUT_1 := 1;
	  			END_CASE;
	  			slt0[23] := (random_num + slt0[23]) MOD 2;
	  			random_num := random_num - slt0[23];
	 		79:
	  			GD_OUT_2 := 1;
			80:
	  			GD_OUT_2 := 1;
			81:
	  			CASE slt0[24] OF
	  				0:
	  					GD_OUT_2 := 1;
	  				1:
	  					GD_OUT_1 := 1;
	  			END_CASE;
	  			slt0[24] := (random_num + slt0[24]) MOD 2;
	  			random_num := random_num - slt0[24];
	 		82:
	  			CASE slt0[25] OF
	  				0:
	  					GD_OUT_2 := 1;
	  				1:
	  					GD_OUT_0 := 1;
	  			END_CASE;
	  			slt0[25] := (random_num + slt0[25]) MOD 2;
	  			random_num := random_num - slt0[25];
	 		84:
	  			GD_OUT_0 := 1;
			87:
	  			GD_OUT_2 := 0;
	  		88:
	  			GD_OUT_2 := 0;
	  		89:
	  			CASE slt0[26] OF
	  				0:
	  					GD_OUT_2 := 0;
	  				1:
	  					GD_OUT_0 := 1;
	  				2:
	  					GD_OUT_1 := 1;
	  			END_CASE;
	  			slt0[26] := (random_num + slt0[26]) MOD 3;
	  			random_num := random_num - slt0[26];
	 		90:
	  			GD_OUT_2 := 0;
	  		91:
	  			GD_OUT_2 := 0;
	  		94:
	  			GD_OUT_1 := 1;
			95:
	  			GD_OUT_0 := 1;
			96:
	  			CASE slt0[27] OF
	  				0:
	  					GD_OUT_2 := 1;
	  				1:
	  					GD_OUT_1 := 1;
	  			END_CASE;
	  			slt0[27] := (random_num + slt0[27]) MOD 2;
	  			random_num := random_num - slt0[27];
	 		97:
	  			CASE slt0[28] OF
	  				0:
	  					GD_OUT_2 := 1;
	  				1:
	  					GD_OUT_1 := 1;
	  			END_CASE;
	  			slt0[28] := (random_num + slt0[28]) MOD 2;
	  			random_num := random_num - slt0[28];
	 		98:
	  			GD_OUT_2 := 1;
			101:
	  			CASE slt0[29] OF
	  				0:
	  					GD_OUT_0 := 1;
	  				1:
	  					GD_OUT_1 := 1;
	  			END_CASE;
	  			slt0[29] := (random_num + slt0[29]) MOD 2;
	  			random_num := random_num - slt0[29];
	 		104:
	  			GD_OUT_2 := 0;
	  		105:
	  			GD_OUT_2 := 0;
	  		106:
	  			CASE slt0[30] OF
	  				0:
	  					GD_OUT_2 := 0;
	  				1:
	  					GD_OUT_1 := 1;
	  			END_CASE;
	  			slt0[30] := (random_num + slt0[30]) MOD 2;
	  			random_num := random_num - slt0[30];
	 		107:
	  			CASE slt0[31] OF
	  				0:
	  					GD_OUT_2 := 0;
	  				1:
	  					GD_OUT_0 := 1;
	  			END_CASE;
	  			slt0[31] := (random_num + slt0[31]) MOD 2;
	  			random_num := random_num - slt0[31];
	 		108:
	  			GD_OUT_1 := 1;
			109:
	  			GD_OUT_1 := 1;
			111:
	  			GD_OUT_2 := 1;
			112:
	  			CASE slt0[32] OF
	  				0:
	  					GD_OUT_2 := 1;
	  				1:
	  					GD_OUT_0 := 1;
	  			END_CASE;
	  			slt0[32] := (random_num + slt0[32]) MOD 2;
	  			random_num := random_num - slt0[32];
	 		115:
	  			GD_OUT_1 := 1;
			116:
	  			GD_OUT_0 := 1;
			117:
	  			CASE slt0[33] OF
	  				0:
	  					GD_OUT_2 := 0;
	  				1:
	  					GD_OUT_1 := 1;
	  			END_CASE;
	  			slt0[33] := (random_num + slt0[33]) MOD 2;
	  			random_num := random_num - slt0[33];
	 		118:
	  			CASE slt0[34] OF
	  				0:
	  					GD_OUT_2 := 0;
	  				1:
	  					GD_OUT_1 := 1;
	  			END_CASE;
	  			slt0[34] := (random_num + slt0[34]) MOD 2;
	  			random_num := random_num - slt0[34];
	 		119:
	  			GD_OUT_2 := 0;
	  		121:
	  			GD_OUT_0 := 1;
			122:
	  			GD_OUT_2 := 1;
			123:
	  			GD_OUT_1 := 1;
			124:
	  			GD_OUT_1 := 1;
			126:
	  			GD_OUT_2 := 0;
	  		127:
	  			CASE slt0[35] OF
	  				0:
	  					GD_OUT_2 := 0;
	  				1:
	  					GD_OUT_0 := 1;
	  			END_CASE;
	  			slt0[35] := (random_num + slt0[35]) MOD 2;
	  			random_num := random_num - slt0[35];
	 		129:
	  			GD_OUT_2 := 1;
			130:
	  			GD_OUT_2 := 1;
			132:
	  			GD_OUT_0 := 1;
			133:
	  			GD_OUT_2 := 0;
	  		137:
	  			GD_OUT_2 := 0;
	  		138:
	  			GD_OUT_2 := 0;
	  	END_CASE;
	
		CASE state[1] OF
	  		2:
	  			GD_OUT_0 := 0;
	  	END_CASE;
	
		CASE state[2] OF
	  		2:
	  			GD_OUT_1 := 0;
	  	END_CASE;
	
		CASE state[3] OF
	  		2:
	  			GD_OUT_5 := 1;
			5:
	  			GD_OUT_5 := 0;
	  	END_CASE;
	
		CASE state[4] OF
	  		2:
	  			GD_OUT_4 := 1;
			5:
	  			GD_OUT_4 := 0;
	  		7:
	  			GD_OUT_4 := 1;
			9:
	  			GD_OUT_4 := 0;
	  	END_CASE;
	
		CASE state[5] OF
	  		1:
	  			GD_OUT_6 := 0;
	  		3:
	  			GD_OUT_6 := 1;
		END_CASE;
	
		CASE state[6] OF
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
		IF state[0] = 1 & GD_OUT_2 THEN
	  		state[0] := 2;
	  	ELSIF state[0] = 1 & GD_OUT_0 THEN
	  		state[0] := 3;
	  	ELSIF state[0] = 2 & GD_OUT_0 THEN
	  		state[0] := 5;
	  	ELSIF state[0] = 3 & GD_OUT_2 THEN
	  		state[0] := 5;
	  	ELSIF state[0] = 4 & NOT GD_OUT_2 THEN
	  		state[0] := 8;
	  	ELSIF state[0] = 4 & GD_OUT_0 THEN
	  		state[0] := 9;
	  	ELSIF state[0] = 6 & GD_OUT_2 THEN
	  		state[0] := 10;
	  	ELSIF state[0] = 7 & GD_OUT_2 THEN
	  		state[0] := 11;
	  	ELSIF state[0] = 7 & GD_OUT_0 THEN
	  		state[0] := 12;
	  	ELSIF state[0] = 7 & GD_OUT_1 THEN
	  		state[0] := 13;
	  	ELSIF state[0] = 8 & GD_OUT_0 THEN
	  		state[0] := 14;
	  	ELSIF state[0] = 9 & NOT GD_OUT_2 THEN
	  		state[0] := 14;
	  	ELSIF state[0] = 11 & GD_OUT_0 THEN
	  		state[0] := 17;
	  	ELSIF state[0] = 11 & GD_OUT_1 THEN
	  		state[0] := 18;
	  	ELSIF state[0] = 12 & GD_OUT_2 THEN
	  		state[0] := 17;
	  	ELSIF state[0] = 12 & GD_OUT_1 THEN
	  		state[0] := 19;
	  	ELSIF state[0] = 13 & GD_OUT_2 THEN
	  		state[0] := 18;
	  	ELSIF state[0] = 13 & GD_OUT_0 THEN
	  		state[0] := 19;
	  	ELSIF state[0] = 15 & NOT GD_OUT_2 THEN
	  		state[0] := 23;
	  	ELSIF state[0] = 16 & NOT GD_OUT_2 THEN
	  		state[0] := 24;
	  	ELSIF state[0] = 16 & GD_OUT_0 THEN
	  		state[0] := 25;
	  	ELSIF state[0] = 16 & GD_OUT_1 THEN
	  		state[0] := 26;
	  	ELSIF state[0] = 17 & GD_OUT_1 THEN
	  		state[0] := 27;
	  	ELSIF state[0] = 18 & GD_OUT_0 THEN
	  		state[0] := 27;
	  	ELSIF state[0] = 19 & GD_OUT_2 THEN
	  		state[0] := 27;
	  	ELSIF state[0] = 20 & GD_OUT_2 THEN
	  		state[0] := 28;
	  	ELSIF state[0] = 20 & GD_OUT_1 THEN
	  		state[0] := 31;
	  	ELSIF state[0] = 21 & GD_OUT_2 THEN
	  		state[0] := 29;
	  	ELSIF state[0] = 21 & GD_OUT_1 THEN
	  		state[0] := 33;
	  	ELSIF state[0] = 22 & GD_OUT_2 THEN
	  		state[0] := 30;
	  	ELSIF state[0] = 22 & GD_OUT_0 THEN
	  		state[0] := 32;
	  	ELSIF state[0] = 24 & GD_OUT_0 THEN
	  		state[0] := 35;
	  	ELSIF state[0] = 24 & GD_OUT_1 THEN
	  		state[0] := 36;
	  	ELSIF state[0] = 25 & NOT GD_OUT_2 THEN
	  		state[0] := 35;
	  	ELSIF state[0] = 25 & GD_OUT_1 THEN
	  		state[0] := 37;
	  	ELSIF state[0] = 26 & NOT GD_OUT_2 THEN
	  		state[0] := 36;
	  	ELSIF state[0] = 26 & GD_OUT_0 THEN
	  		state[0] := 37;
	  	ELSIF state[0] = 28 & GD_OUT_1 THEN
	  		state[0] := 41;
	  	ELSIF state[0] = 29 & GD_OUT_1 THEN
	  		state[0] := 43;
	  	ELSIF state[0] = 30 & GD_OUT_0 THEN
	  		state[0] := 42;
	  	ELSIF state[0] = 31 & GD_OUT_2 THEN
	  		state[0] := 41;
	  	ELSIF state[0] = 32 & GD_OUT_2 THEN
	  		state[0] := 42;
	  	ELSIF state[0] = 33 & GD_OUT_2 THEN
	  		state[0] := 43;
	  	ELSIF state[0] = 33 & GD_OUT_0 THEN
	  		state[0] := 48;
	  	ELSIF state[0] = 34 & GD_OUT_2 THEN
	  		state[0] := 44;
	  	ELSIF state[0] = 34 & GD_OUT_0 THEN
	  		state[0] := 47;
	  	ELSIF state[0] = 35 & GD_OUT_1 THEN
	  		state[0] := 49;
	  	ELSIF state[0] = 36 & GD_OUT_0 THEN
	  		state[0] := 49;
	  	ELSIF state[0] = 37 & NOT GD_OUT_2 THEN
	  		state[0] := 49;
	  	ELSIF state[0] = 38 & NOT GD_OUT_2 THEN
	  		state[0] := 50;
	  	ELSIF state[0] = 38 & GD_OUT_1 THEN
	  		state[0] := 53;
	  	ELSIF state[0] = 39 & NOT GD_OUT_2 THEN
	  		state[0] := 51;
	  	ELSIF state[0] = 39 & GD_OUT_1 THEN
	  		state[0] := 55;
	  	ELSIF state[0] = 40 & NOT GD_OUT_2 THEN
	  		state[0] := 52;
	  	ELSIF state[0] = 40 & GD_OUT_0 THEN
	  		state[0] := 54;
	  	ELSIF state[0] = 43 & GD_OUT_0 THEN
	  		state[0] := 60;
	  	ELSIF state[0] = 44 & GD_OUT_0 THEN
	  		state[0] := 59;
	  	ELSIF state[0] = 45 & GD_OUT_2 THEN
	  		state[0] := 57;
	  	ELSIF state[0] = 46 & GD_OUT_2 THEN
	  		state[0] := 58;
	  	ELSIF state[0] = 46 & GD_OUT_0 THEN
	  		state[0] := 62;
	  	ELSIF state[0] = 47 & GD_OUT_2 THEN
	  		state[0] := 59;
	  	ELSIF state[0] = 48 & GD_OUT_2 THEN
	  		state[0] := 60;
	  	ELSIF state[0] = 50 & GD_OUT_1 THEN
	  		state[0] := 66;
	  	ELSIF state[0] = 51 & GD_OUT_1 THEN
	  		state[0] := 68;
	  	ELSIF state[0] = 52 & GD_OUT_0 THEN
	  		state[0] := 67;
	  	ELSIF state[0] = 53 & NOT GD_OUT_2 THEN
	  		state[0] := 66;
	  	ELSIF state[0] = 54 & NOT GD_OUT_2 THEN
	  		state[0] := 67;
	  	ELSIF state[0] = 55 & NOT GD_OUT_2 THEN
	  		state[0] := 68;
	  	ELSIF state[0] = 55 & GD_OUT_0 THEN
	  		state[0] := 73;
	  	ELSIF state[0] = 56 & NOT GD_OUT_2 THEN
	  		state[0] := 69;
	  	ELSIF state[0] = 56 & GD_OUT_0 THEN
	  		state[0] := 72;
	  	ELSIF state[0] = 58 & GD_OUT_0 THEN
	  		state[0] := 75;
	  	ELSIF state[0] = 61 & GD_OUT_2 THEN
	  		state[0] := 74;
	  	ELSIF state[0] = 62 & GD_OUT_2 THEN
	  		state[0] := 75;
	  	ELSIF state[0] = 63 & GD_OUT_2 THEN
	  		state[0] := 76;
	  	ELSIF state[0] = 63 & GD_OUT_0 THEN
	  		state[0] := 81;
	  	ELSIF state[0] = 63 & GD_OUT_1 THEN
	  		state[0] := 82;
	  	ELSIF state[0] = 64 & GD_OUT_2 THEN
	  		state[0] := 77;
	  	ELSIF state[0] = 65 & GD_OUT_2 THEN
	  		state[0] := 78;
	  	ELSIF state[0] = 68 & GD_OUT_0 THEN
	  		state[0] := 86;
	  	ELSIF state[0] = 69 & GD_OUT_0 THEN
	  		state[0] := 85;
	  	ELSIF state[0] = 70 & NOT GD_OUT_2 THEN
	  		state[0] := 83;
	  	ELSIF state[0] = 71 & NOT GD_OUT_2 THEN
	  		state[0] := 84;
	  	ELSIF state[0] = 71 & GD_OUT_0 THEN
	  		state[0] := 88;
	  	ELSIF state[0] = 72 & NOT GD_OUT_2 THEN
	  		state[0] := 85;
	  	ELSIF state[0] = 73 & NOT GD_OUT_2 THEN
	  		state[0] := 86;
	  	ELSIF state[0] = 76 & GD_OUT_0 THEN
	  		state[0] := 94;
	  	ELSIF state[0] = 76 & GD_OUT_1 THEN
	  		state[0] := 95;
	  	ELSIF state[0] = 79 & GD_OUT_2 THEN
	  		state[0] := 92;
	  	ELSIF state[0] = 80 & GD_OUT_2 THEN
	  		state[0] := 93;
	  	ELSIF state[0] = 81 & GD_OUT_2 THEN
	  		state[0] := 94;
	  	ELSIF state[0] = 81 & GD_OUT_1 THEN
	  		state[0] := 98;
	  	ELSIF state[0] = 82 & GD_OUT_2 THEN
	  		state[0] := 95;
	  	ELSIF state[0] = 82 & GD_OUT_0 THEN
	  		state[0] := 98;
	  	ELSIF state[0] = 84 & GD_OUT_0 THEN
	  		state[0] := 100;
	  	ELSIF state[0] = 87 & NOT GD_OUT_2 THEN
	  		state[0] := 99;
	  	ELSIF state[0] = 88 & NOT GD_OUT_2 THEN
	  		state[0] := 100;
	  	ELSIF state[0] = 89 & NOT GD_OUT_2 THEN
	  		state[0] := 101;
	  	ELSIF state[0] = 89 & GD_OUT_0 THEN
	  		state[0] := 106;
	  	ELSIF state[0] = 89 & GD_OUT_1 THEN
	  		state[0] := 107;
	  	ELSIF state[0] = 90 & NOT GD_OUT_2 THEN
	  		state[0] := 102;
	  	ELSIF state[0] = 91 & NOT GD_OUT_2 THEN
	  		state[0] := 103;
	  	ELSIF state[0] = 94 & GD_OUT_1 THEN
	  		state[0] := 110;
	  	ELSIF state[0] = 95 & GD_OUT_0 THEN
	  		state[0] := 110;
	  	ELSIF state[0] = 96 & GD_OUT_2 THEN
	  		state[0] := 108;
	  	ELSIF state[0] = 96 & GD_OUT_1 THEN
	  		state[0] := 111;
	  	ELSIF state[0] = 97 & GD_OUT_2 THEN
	  		state[0] := 109;
	  	ELSIF state[0] = 97 & GD_OUT_1 THEN
	  		state[0] := 112;
	  	ELSIF state[0] = 98 & GD_OUT_2 THEN
	  		state[0] := 110;
	  	ELSIF state[0] = 101 & GD_OUT_0 THEN
	  		state[0] := 115;
	  	ELSIF state[0] = 101 & GD_OUT_1 THEN
	  		state[0] := 116;
	  	ELSIF state[0] = 104 & NOT GD_OUT_2 THEN
	  		state[0] := 113;
	  	ELSIF state[0] = 105 & NOT GD_OUT_2 THEN
	  		state[0] := 114;
	  	ELSIF state[0] = 106 & NOT GD_OUT_2 THEN
	  		state[0] := 115;
	  	ELSIF state[0] = 106 & GD_OUT_1 THEN
	  		state[0] := 119;
	  	ELSIF state[0] = 107 & NOT GD_OUT_2 THEN
	  		state[0] := 116;
	  	ELSIF state[0] = 107 & GD_OUT_0 THEN
	  		state[0] := 119;
	  	ELSIF state[0] = 108 & GD_OUT_1 THEN
	  		state[0] := 120;
	  	ELSIF state[0] = 109 & GD_OUT_1 THEN
	  		state[0] := 121;
	  	ELSIF state[0] = 111 & GD_OUT_2 THEN
	  		state[0] := 120;
	  	ELSIF state[0] = 112 & GD_OUT_2 THEN
	  		state[0] := 121;
	  	ELSIF state[0] = 112 & GD_OUT_0 THEN
	  		state[0] := 122;
	  	ELSIF state[0] = 115 & GD_OUT_1 THEN
	  		state[0] := 125;
	  	ELSIF state[0] = 116 & GD_OUT_0 THEN
	  		state[0] := 125;
	  	ELSIF state[0] = 117 & NOT GD_OUT_2 THEN
	  		state[0] := 123;
	  	ELSIF state[0] = 117 & GD_OUT_1 THEN
	  		state[0] := 126;
	  	ELSIF state[0] = 118 & NOT GD_OUT_2 THEN
	  		state[0] := 124;
	  	ELSIF state[0] = 118 & GD_OUT_1 THEN
	  		state[0] := 127;
	  	ELSIF state[0] = 119 & NOT GD_OUT_2 THEN
	  		state[0] := 125;
	  	ELSIF state[0] = 121 & GD_OUT_0 THEN
	  		state[0] := 128;
	  	ELSIF state[0] = 122 & GD_OUT_2 THEN
	  		state[0] := 128;
	  	ELSIF state[0] = 123 & GD_OUT_1 THEN
	  		state[0] := 131;
	  	ELSIF state[0] = 124 & GD_OUT_1 THEN
	  		state[0] := 132;
	  	ELSIF state[0] = 126 & NOT GD_OUT_2 THEN
	  		state[0] := 131;
	  	ELSIF state[0] = 127 & NOT GD_OUT_2 THEN
	  		state[0] := 132;
	  	ELSIF state[0] = 127 & GD_OUT_0 THEN
	  		state[0] := 133;
	  	ELSIF state[0] = 129 & GD_OUT_2 THEN
	  		state[0] := 134;
	  	ELSIF state[0] = 130 & GD_OUT_2 THEN
	  		state[0] := 135;
	  	ELSIF state[0] = 132 & GD_OUT_0 THEN
	  		state[0] := 136;
	  	ELSIF state[0] = 133 & NOT GD_OUT_2 THEN
	  		state[0] := 136;
	  	ELSIF state[0] = 137 & NOT GD_OUT_2 THEN
	  		state[0] := 139;
	  	ELSIF state[0] = 138 & NOT GD_OUT_2 THEN
	  		state[0] := 140;
	  	END_IF;
	
		IF state[1] = 2 & NOT GD_OUT_0 THEN
	  		state[1] := 3;
	  	END_IF;
	
		IF state[2] = 2 & NOT GD_OUT_1 THEN
	  		state[2] := 3;
	  	END_IF;
	
		IF state[3] = 2 & GD_OUT_5 THEN
	  		state[3] := 4;
	  	ELSIF state[3] = 5 & NOT GD_OUT_5 THEN
	  		state[3] := 0;
	  	END_IF;
	
		IF state[4] = 2 & GD_OUT_4 THEN
	  		state[4] := 4;
	  	ELSIF state[4] = 5 & NOT GD_OUT_4 THEN
	  		state[4] := 6;
	  	ELSIF state[4] = 7 & GD_OUT_4 THEN
	  		state[4] := 8;
	  	ELSIF state[4] = 9 & NOT GD_OUT_4 THEN
	  		state[4] := 6;
	  	END_IF;
	
		IF state[5] = 1 & NOT GD_OUT_6 THEN
	  		state[5] := 2;
	  	ELSIF state[5] = 3 & GD_OUT_6 THEN
	  		state[5] := 0;
	  	END_IF;
	
		IF state[6] = 1 & INTERN_2 THEN
	  		state[6] := 3;
	  	ELSIF state[6] = 2 & INTERN_3 THEN
	  		state[6] := 4;
	  	ELSIF state[6] = 5 & GD_OUT_10 THEN
	  		state[6] := 9;
	  	ELSIF state[6] = 6 & NOT INTERN_2 THEN
	  		state[6] := 10;
	  	ELSIF state[6] = 7 & GD_OUT_11 THEN
	  		state[6] := 11;
	  	ELSIF state[6] = 9 & NOT INTERN_2 THEN
	  		state[6] := 13;
	  	ELSIF state[6] = 10 & INTERN_3 THEN
	  		state[6] := 8;
	  	ELSIF state[6] = 11 & NOT INTERN_3 THEN
	  		state[6] := 14;
	  	ELSIF state[6] = 12 & GD_OUT_11 THEN
	  		state[6] := 15;
	  	ELSIF state[6] = 15 & NOT INTERN_3 THEN
	  		state[6] := 18;
	  	ELSIF state[6] = 16 & NOT GD_OUT_10 THEN
	  		state[6] := 0;
	  	ELSIF state[6] = 17 & NOT GD_OUT_11 THEN
	  		state[6] := 0;
	  	ELSIF state[6] = 19 & NOT GD_OUT_11 THEN
	  		state[6] := 1;
	  	END_IF;
	
		GD_OUT_3 := GD_OUT_2;
	 	GD_OUT_8 := NOT GD_IN_10;
	 	GD_OUT_9 := NOT GD_IN_11;
	 
	END_IF;
END_PROGRAM

CONFIGURATION Config0

	RESOURCE Res0 ON PLC
		TASK task0(INTERVAL := T#20ms,PRIORITY := 0);
		PROGRAM instance0 WITH task0 : tesis0;
	END_RESOURCE
END_CONFIGURATION