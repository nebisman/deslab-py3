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
		state : ARRAY [0..9] OF DINT;
		aux : BOOL := 0;
		INTERN_1_C : ARRAY [0..1] OF BOOL;
		INTERN_3_C : ARRAY [0..1] OF BOOL;
		INTERN_5_C : ARRAY [0..1] OF BOOL;
		slt0 : ARRAY [0..2] OF DINT;
		INTERN_3_G : ARRAY [0..2] OF BOOL;
		INTERN_5_G : ARRAY [0..2] OF BOOL;
		INTERN_1_G : ARRAY [0..1] OF BOOL;
		RE_M1 : R_TRIG;
		FE_M2E : F_TRIG;
		FE_CP : F_TRIG;
		RE_CP : R_TRIG;
		FE_M1 : F_TRIG;
		FE_B1 : F_TRIG;
		FE_B1O : F_TRIG;
		FE_PO : F_TRIG;
		FE_PR : F_TRIG;
		FE_AT : F_TRIG;
		FE_MZ : F_TRIG;
		FE_RO : F_TRIG;
		INTERN_1 : BOOL;
		INTERN_3 : BOOL;
		INTERN_5 : BOOL;
	END_VAR
	VAR
		GD_OUT_1 AT %QX100.1 : BOOL;
 		GD_OUT_2 AT %QX100.2 : BOOL;
 		GD_OUT_3 AT %QX100.3 : BOOL;
 		GD_OUT_11 AT %QX101.3 : BOOL;
 		GD_OUT_12 AT %QX101.4 : BOOL;
 		GD_OUT_13 AT %QX101.5 : BOOL;
 		GD_OUT_14 AT %QX101.6 : BOOL;
 		GD_IN_0 AT %IX100.0 : BOOL;
		GD_IN_8 AT %IX101.0 : BOOL;
		GD_IN_1 AT %IX100.1 : BOOL;
		GD_IN_6 AT %IX100.6 : BOOL;
		GD_OUT_7 AT %QX100.7 : BOOL;
		GD_IN_7 AT %IX100.7 : BOOL;
		GD_OUT_4 AT %QX100.4 : BOOL;
		GD_IN_2 AT %IX100.2 : BOOL;
		GD_IN_3 AT %IX100.3 : BOOL;
		GD_OUT_5 AT %QX100.5 : BOOL;
		GD_OUT_6 AT %QX100.6 : BOOL;
		GD_IN_4 AT %IX100.4 : BOOL;
		GD_IN_5 AT %IX100.5 : BOOL;
		GD_OUT_8 AT %QX101.0 : BOOL;
		GD_OUT_9 AT %QX101.1 : BOOL;
		GD_OUT_10 AT %QX101.2 : BOOL;
		GD_IN_9 AT %IX101.1 : BOOL;
		GD_IN_11 AT %IX101.3 : BOOL;
		GD_IN_10 AT %IX101.2 : BOOL;
		GD_IN_12 AT %IX101.4 : BOOL;
		GD_IN_13 AT %IX101.5 : BOOL;
		GD_OUT_15 AT %QX101.7 : BOOL;
		GD_OUT_18 AT %QX102.2 : BOOL;
		GD_OUT_16 AT %QX102.0 : BOOL;
		GD_OUT_17 AT %QX102.1 : BOOL;
		GD_OUT_0 AT %QX100.0 : BOOL;
	END_VAR
	RE_M1(CLK:= GD_IN_1);
	FE_M2E(CLK:= GD_IN_6);
	FE_CP(CLK:= GD_IN_7);
	RE_CP(CLK:= GD_IN_7);
	FE_M1(CLK:= GD_IN_1);
	FE_B1(CLK:= GD_IN_3);
	FE_B1O(CLK:= GD_IN_5);
	FE_PO(CLK:= GD_IN_9);
	FE_PR(CLK:= GD_IN_11);
	FE_AT(CLK:= GD_IN_10);
	FE_MZ(CLK:= GD_IN_12);
	FE_RO(CLK:= GD_IN_13);
	random(
		IN := True,
		OUT => random_num);
	IF NOT initial THEN
		IF GD_IN_0 THEN
			initial := 1;
		END_IF;
	ELSIF initial THEN
		IF state[0] = 0 & GD_IN_0 THEN
	  		state[0] := 1;
	  	ELSIF state[0] = 2 & RE_M1.Q THEN
	  		state[0] := 4;
	  	ELSIF state[0] = 3 & FE_PR.Q THEN
	  		state[0] := 4;
	  	ELSIF state[0] = 3 & FE_PO.Q THEN
	  		state[0] := 1;
	  	ELSIF state[0] = 5 & RE_CP.Q THEN
	  		state[0] := 1;
	  	ELSIF state[0] = 6 & RE_M1.Q THEN
	  		state[0] := 8;
	  	ELSIF state[0] = 6 & RE_CP.Q THEN
	  		state[0] := 2;
	  	ELSIF state[0] = 7 & FE_PR.Q THEN
	  		state[0] := 8;
	  	ELSIF state[0] = 7 & RE_CP.Q THEN
	  		state[0] := 3;
	  	ELSIF state[0] = 7 & FE_PO.Q THEN
	  		state[0] := 5;
	  	ELSIF state[0] = 8 & RE_CP.Q THEN
	  		state[0] := 4;
	  	END_IF;
	
		IF state[1] = 1 & RE_CP.Q THEN
	  		state[1] := 2;
	  	ELSIF state[1] = 3 & FE_PR.Q THEN
	  		state[1] := 0;
	  	ELSIF state[1] = 3 & FE_PO.Q THEN
	  		state[1] := 0;
	  	ELSIF state[1] = 4 & FE_PR.Q THEN
	  		state[1] := 1;
	  	ELSIF state[1] = 4 & RE_CP.Q THEN
	  		state[1] := 5;
	  	ELSIF state[1] = 4 & FE_PO.Q THEN
	  		state[1] := 1;
	  	ELSIF state[1] = 5 & FE_PR.Q THEN
	  		state[1] := 2;
	  	ELSIF state[1] = 5 & FE_PO.Q THEN
	  		state[1] := 2;
	  	END_IF;
	
		IF state[2] = 0 & GD_OUT_0 THEN
	  		state[2] := 1;
	  	ELSIF state[2] = 0 & FE_M1.Q THEN
	  		state[2] := 2;
	  	ELSIF state[2] = 1 & FE_M1.Q THEN
	  		state[2] := 3;
	  	ELSIF state[2] = 2 & GD_OUT_0 THEN
	  		state[2] := 3;
	  	END_IF;
	
		IF state[3] = 0 & RE_M1.Q THEN
	  		state[3] := 1;
	  	ELSIF state[3] = 0 & FE_PR.Q THEN
	  		state[3] := 1;
	  	ELSIF state[3] = 2 & FE_B1.Q THEN
	  		state[3] := 3;
	  	ELSIF state[3] = 2 & FE_B1O.Q THEN
	  		state[3] := 4;
	  	ELSIF state[3] = 3 & FE_B1O.Q THEN
	  		state[3] := 5;
	  	ELSIF state[3] = 4 & FE_B1.Q THEN
	  		state[3] := 5;
	  	ELSIF state[3] = 4 & RE_M1.Q THEN
	  		state[3] := 7;
	  	ELSIF state[3] = 4 & FE_PR.Q THEN
	  		state[3] := 7;
	  	ELSIF state[3] = 5 & RE_M1.Q THEN
	  		state[3] := 8;
	  	ELSIF state[3] = 5 & FE_PR.Q THEN
	  		state[3] := 8;
	  	ELSIF state[3] = 6 & FE_B1O.Q THEN
	  		state[3] := 9;
	  	ELSIF state[3] = 7 & FE_B1.Q THEN
	  		state[3] := 8;
	  	ELSIF state[3] = 9 & RE_M1.Q THEN
	  		state[3] := 11;
	  	ELSIF state[3] = 9 & FE_PR.Q THEN
	  		state[3] := 11;
	  	ELSIF state[3] = 10 & GD_IN_2 THEN
	  		state[3] := 13;
	  	ELSIF state[3] = 10 & FE_B1O.Q THEN
	  		state[3] := 12;
	  	ELSIF state[3] = 12 & GD_IN_2 THEN
	  		state[3] := 15;
	  	ELSIF state[3] = 12 & RE_M1.Q THEN
	  		state[3] := 14;
	  	ELSIF state[3] = 12 & FE_PR.Q THEN
	  		state[3] := 14;
	  	ELSIF state[3] = 13 & FE_B1O.Q THEN
	  		state[3] := 15;
	  	ELSIF state[3] = 14 & GD_IN_2 THEN
	  		state[3] := 17;
	  	ELSIF state[3] = 15 & RE_M1.Q THEN
	  		state[3] := 17;
	  	ELSIF state[3] = 15 & FE_PR.Q THEN
	  		state[3] := 17;
	  	ELSIF state[3] = 16 & FE_B1O.Q THEN
	  		state[3] := 18;
	  	ELSIF state[3] = 18 & RE_M1.Q THEN
	  		state[3] := 20;
	  	ELSIF state[3] = 18 & FE_PR.Q THEN
	  		state[3] := 20;
	  	ELSIF state[3] = 19 & FE_B1O.Q THEN
	  		state[3] := 21;
	  	ELSIF state[3] = 21 & RE_M1.Q THEN
	  		state[3] := 23;
	  	ELSIF state[3] = 21 & FE_PR.Q THEN
	  		state[3] := 23;
	  	ELSIF state[3] = 22 & FE_B1O.Q THEN
	  		state[3] := 24;
	  	ELSIF state[3] = 24 & RE_M1.Q THEN
	  		state[3] := 26;
	  	ELSIF state[3] = 24 & FE_PR.Q THEN
	  		state[3] := 26;
	  	ELSIF state[3] = 25 & FE_B1O.Q THEN
	  		state[3] := 27;
	  	ELSIF state[3] = 27 & RE_M1.Q THEN
	  		state[3] := 28;
	  	ELSIF state[3] = 27 & FE_PR.Q THEN
	  		state[3] := 28;
	  	ELSIF state[3] = 29 & RE_M1.Q THEN
	  		state[3] := 30;
	  	ELSIF state[3] = 29 & FE_PR.Q THEN
	  		state[3] := 30;
	  	ELSIF state[3] = 31 & RE_M1.Q THEN
	  		state[3] := 32;
	  	ELSIF state[3] = 31 & FE_PR.Q THEN
	  		state[3] := 32;
	  	END_IF;
	
		IF state[4] = 0 & GD_OUT_7 THEN
	  		state[4] := 1;
	  	ELSIF state[4] = 1 & GD_IN_6 THEN
	  		state[4] := 2;
	  	ELSIF state[4] = 3 & FE_M2E.Q THEN
	  		state[4] := 0;
	  	END_IF;
	
		IF state[5] = 0 & GD_IN_6 THEN
	  		state[5] := 1;
	  	ELSIF state[5] = 1 & FE_M2E.Q THEN
	  		state[5] := 2;
	  	ELSIF state[5] = 3 & RE_CP.Q THEN
	  		state[5] := 4;
	  	END_IF;
	
		IF state[6] = 0 & GD_OUT_9 THEN
	  		state[6] := 1;
	  	ELSIF state[6] = 1 & FE_CP.Q THEN
	  		state[6] := 2;
	  	ELSIF state[6] = 2 & GD_IN_8 THEN
	  		state[6] := 3;
	  	ELSIF state[6] = 2 & NOT GD_IN_8 THEN
	  		state[6] := 4;
	  	ELSIF state[6] = 3 & FE_PO.Q THEN
	  		state[6] := 5;
	  	ELSIF state[6] = 6 & FE_AT.Q THEN
	  		state[6] := 7;
	  	END_IF;
	
		IF state[7] = 0 & FE_AT.Q THEN
	  		state[7] := 1;
	  	ELSIF state[7] = 2 & FE_MZ.Q THEN
	  		state[7] := 3;
	  	ELSIF state[7] = 5 & FE_MZ.Q THEN
	  		state[7] := 6;
	  	ELSIF state[7] = 7 & FE_RO.Q THEN
	  		state[7] := 8;
	  	ELSIF state[7] = 10 & FE_MZ.Q THEN
	  		state[7] := 11;
	  	ELSIF state[7] = 13 & FE_MZ.Q THEN
	  		state[7] := 14;
	  	ELSIF state[7] = 15 & FE_RO.Q THEN
	  		state[7] := 16;
	  	END_IF;
	
	
		CASE state[0] OF
	  		1:
	  			CASE slt0[0] OF
	  				0:
	  					INTERN_1_G[0] := 1;
	  				1:
	  					INTERN_5_G[0] := 1;
	  			END_CASE;
	  			slt0[0] := (random_num + slt0[0]) MOD 2;
	  			random_num := random_num - slt0[0];
	 		4:
	  			INTERN_3_G[0] := 1;
			5:
	  			CASE slt0[1] OF
	  				0:
	  					INTERN_1_G[0] := 1;
	  				1:
	  					INTERN_5_G[0] := 1;
	  			END_CASE;
	  			slt0[1] := (random_num + slt0[1]) MOD 2;
	  			random_num := random_num - slt0[1];
	 	END_CASE;
	
		CASE state[1] OF
	  		0:
	  			INTERN_3_G[1] := 1;
			2:
	  			INTERN_5_G[1] := 1;
			3:
	  			INTERN_3_G[1] := 1;
		END_CASE;
	
		CASE state[2] OF
	  		3:
	  			GD_OUT_0 := 0;
	  	END_CASE;
	
		CASE state[3] OF
	  		1:
	  			GD_OUT_5 := 1;
			3:
	  			GD_OUT_5 := 0;
	  		5:
	  			GD_OUT_5 := 0;
	  		6:
	  			GD_OUT_4 := 1;
			8:
	  			GD_OUT_5 := 0;
	  		9:
	  			GD_OUT_4 := 1;
			11:
	  			GD_OUT_4 := 1;
			13:
	  			GD_OUT_4 := 0;
	  		15:
	  			GD_OUT_4 := 0;
	  		16:
	  			GD_OUT_6 := 1;
			17:
	  			GD_OUT_4 := 0;
	  		18:
	  			GD_OUT_6 := 1;
			19:
	  			GD_IN_4 := 1;
			20:
	  			GD_OUT_6 := 1;
			21:
	  			GD_IN_4 := 1;
			22:
	  			GD_OUT_5 := 1;
			23:
	  			GD_IN_4 := 1;
			26:
	  			GD_OUT_5 := 1;
			27:
	  			GD_OUT_5 := 0;
	  		28:
	  			GD_OUT_5 := 0;
	  		29:
	  			GD_OUT_6 := 0;
	  		30:
	  			GD_OUT_6 := 0;
	  		31:
	  			GD_IN_4 := 1;
			32:
	  			GD_IN_4 := 1;
		END_CASE;
	
		CASE state[4] OF
	  		2:
	  			GD_OUT_7 := 0;
	  	END_CASE;
	
		CASE state[5] OF
	  		2:
	  			GD_OUT_8 := 1;
			4:
	  			GD_OUT_8 := 0;
	  	END_CASE;
	
		CASE state[6] OF
	  		4:
	  			GD_OUT_10 := 1;
			5:
	  			GD_OUT_9 := 0;
	  		7:
	  			GD_OUT_10 := 0;
	  		8:
	  			GD_OUT_9 := 0;
	  	END_CASE;
	
		CASE state[7] OF
	  		1:
	  			GD_OUT_15 := 1;
			3:
	  			GD_OUT_18 := 1;
			4:
	  			GD_OUT_15 := 0;
	  		6:
	  			GD_OUT_16 := 1;
			8:
	  			GD_OUT_16 := 0;
	  		9:
	  			GD_OUT_15 := 1;
			11:
	  			GD_OUT_18 := 0;
	  		12:
	  			GD_OUT_15 := 0;
	  		14:
	  			GD_OUT_17 := 1;
			16:
	  			GD_OUT_17 := 0;
	  	END_CASE;
		CASE state[8] OF
	  		0:
	  			INTERN_1_C[1] := 1;
				INTERN_3_C[1] := 1;
				INTERN_5_C[1] := 0;
			1:
	  			INTERN_1_C[1] := 0;
				INTERN_3_C[1] := 0;
				INTERN_5_C[1] := 1;
		END_CASE;
	  	IF INTERN_3_G[0] <> INTERN_3_G[1] THEN
			INTERN_3_G[0] := INTERN_3;
			INTERN_3_G[1] := INTERN_3;
		END_IF;
		aux := INTERN_3_G[0];
		IF aux XOR INTERN_3 THEN
			IF NOT aux & INTERN_3_C[0] THEN
				INTERN_3 := 0;
			ELSIF aux & INTERN_3_C[1] THEN
				INTERN_3 := 1;
			END_IF;
		END_IF;
		INTERN_3_G[0] := INTERN_3;
		IF INTERN_5_G[0] <> INTERN_5_G[1] THEN
			INTERN_5_G[0] := INTERN_5;
			INTERN_5_G[1] := INTERN_5;
		END_IF;
		aux := INTERN_5_G[0];
		IF aux XOR INTERN_5 THEN
			IF NOT aux & INTERN_5_C[0] THEN
				INTERN_5 := 0;
			ELSIF aux & INTERN_5_C[1] THEN
				INTERN_5 := 1;
			END_IF;
		END_IF;
		INTERN_5_G[0] := INTERN_5;
	
		aux := INTERN_1_G[0];
		IF aux XOR INTERN_1 THEN
			IF NOT aux & INTERN_1_C[0] THEN
				INTERN_1 := 0;
			ELSIF aux & INTERN_1_C[1] THEN
				INTERN_1 := 1;
			END_IF;
		END_IF;
		INTERN_1_G[0] := INTERN_1;
		IF state[8] = 0 & INTERN_3 THEN
	  		state[8] := 1;
	  	ELSIF state[8] = 1 & INTERN_5 THEN
	  		state[8] := 0;
	  	END_IF;
		IF state[0] = 1 & INTERN_1 THEN
	  		state[0] := 2;
	  	ELSIF state[0] = 1 & INTERN_5 THEN
	  		state[0] := 3;
	  	ELSIF state[0] = 4 & INTERN_3 THEN
	  		state[0] := 5;
	  	ELSIF state[0] = 5 & INTERN_1 THEN
	  		state[0] := 6;
	  	ELSIF state[0] = 5 & INTERN_5 THEN
	  		state[0] := 7;
	  	END_IF;
	
		IF state[1] = 0 & INTERN_3 THEN
	  		state[1] := 1;
	  	ELSIF state[1] = 2 & INTERN_5 THEN
	  		state[1] := 3;
	  	ELSIF state[1] = 3 & INTERN_3 THEN
	  		state[1] := 4;
	  	END_IF;
	
		IF state[2] = 3 & NOT GD_OUT_0 THEN
	  		state[2] := 0;
	  	END_IF;
	
		IF state[3] = 1 & GD_OUT_5 THEN
	  		state[3] := 2;
	  	ELSIF state[3] = 3 & NOT GD_OUT_5 THEN
	  		state[3] := 6;
	  	ELSIF state[3] = 5 & NOT GD_OUT_5 THEN
	  		state[3] := 9;
	  	ELSIF state[3] = 6 & GD_OUT_4 THEN
	  		state[3] := 10;
	  	ELSIF state[3] = 8 & NOT GD_OUT_5 THEN
	  		state[3] := 11;
	  	ELSIF state[3] = 9 & GD_OUT_4 THEN
	  		state[3] := 12;
	  	ELSIF state[3] = 11 & GD_OUT_4 THEN
	  		state[3] := 14;
	  	ELSIF state[3] = 13 & NOT GD_OUT_4 THEN
	  		state[3] := 16;
	  	ELSIF state[3] = 15 & NOT GD_OUT_4 THEN
	  		state[3] := 18;
	  	ELSIF state[3] = 16 & GD_OUT_6 THEN
	  		state[3] := 19;
	  	ELSIF state[3] = 17 & NOT GD_OUT_4 THEN
	  		state[3] := 20;
	  	ELSIF state[3] = 18 & GD_OUT_6 THEN
	  		state[3] := 21;
	  	ELSIF state[3] = 19 & GD_IN_4 THEN
	  		state[3] := 22;
	  	ELSIF state[3] = 20 & GD_OUT_6 THEN
	  		state[3] := 23;
	  	ELSIF state[3] = 21 & GD_IN_4 THEN
	  		state[3] := 24;
	  	ELSIF state[3] = 22 & GD_OUT_5 THEN
	  		state[3] := 25;
	  	ELSIF state[3] = 23 & GD_IN_4 THEN
	  		state[3] := 26;
	  	ELSIF state[3] = 26 & GD_OUT_5 THEN
	  		state[3] := 25;
	  	ELSIF state[3] = 27 & NOT GD_OUT_5 THEN
	  		state[3] := 29;
	  	ELSIF state[3] = 28 & NOT GD_OUT_5 THEN
	  		state[3] := 30;
	  	ELSIF state[3] = 29 & NOT GD_OUT_6 THEN
	  		state[3] := 31;
	  	ELSIF state[3] = 30 & NOT GD_OUT_6 THEN
	  		state[3] := 32;
	  	ELSIF state[3] = 31 & GD_IN_4 THEN
	  		state[3] := 0;
	  	ELSIF state[3] = 32 & GD_IN_4 THEN
	  		state[3] := 1;
	  	END_IF;
	
		IF state[4] = 2 & NOT GD_OUT_7 THEN
	  		state[4] := 3;
	  	END_IF;
	
		IF state[5] = 2 & GD_OUT_8 THEN
	  		state[5] := 3;
	  	ELSIF state[5] = 4 & NOT GD_OUT_8 THEN
	  		state[5] := 0;
	  	END_IF;
	
		IF state[6] = 4 & GD_OUT_10 THEN
	  		state[6] := 6;
	  	ELSIF state[6] = 5 & NOT GD_OUT_9 THEN
	  		state[6] := 0;
	  	ELSIF state[6] = 7 & NOT GD_OUT_10 THEN
	  		state[6] := 8;
	  	ELSIF state[6] = 8 & NOT GD_OUT_9 THEN
	  		state[6] := 0;
	  	END_IF;
	
		IF state[7] = 1 & GD_OUT_15 THEN
	  		state[7] := 2;
	  	ELSIF state[7] = 3 & GD_OUT_18 THEN
	  		state[7] := 4;
	  	ELSIF state[7] = 4 & NOT GD_OUT_15 THEN
	  		state[7] := 5;
	  	ELSIF state[7] = 6 & GD_OUT_16 THEN
	  		state[7] := 7;
	  	ELSIF state[7] = 8 & NOT GD_OUT_16 THEN
	  		state[7] := 9;
	  	ELSIF state[7] = 9 & GD_OUT_15 THEN
	  		state[7] := 10;
	  	ELSIF state[7] = 11 & NOT GD_OUT_18 THEN
	  		state[7] := 12;
	  	ELSIF state[7] = 12 & NOT GD_OUT_15 THEN
	  		state[7] := 13;
	  	ELSIF state[7] = 14 & GD_OUT_17 THEN
	  		state[7] := 15;
	  	ELSIF state[7] = 16 & NOT GD_OUT_17 THEN
	  		state[7] := 0;
	  	END_IF;
	
		IF NOT GD_OUT_0 & INTERN_1 THEN
			GD_OUT_0 := 1;
		ELSIF GD_OUT_0 & INTERN_1 THEN
			INTERN_1 := 0;
			INTERN_1_G[0] := 0;
	END_IF;
		IF NOT GD_OUT_7 & INTERN_3 THEN
			GD_OUT_7 := 1;
		ELSIF GD_OUT_7 & INTERN_3 THEN
			INTERN_3 := 0;
			INTERN_3_G[0] := 0;
	END_IF;
		IF NOT GD_OUT_9 & INTERN_5 THEN
			GD_OUT_9 := 1;
		ELSIF GD_OUT_9 & INTERN_5 THEN
			INTERN_5 := 0;
			INTERN_5_G[0] := 0;
	END_IF;
		GD_OUT_1 := GD_OUT_0;
	 	GD_OUT_2 := GD_OUT_0;
	 	GD_OUT_3 := GD_OUT_0;
	 	GD_OUT_11 := GD_OUT_10;
	 	GD_OUT_12 := GD_OUT_10;
	 	GD_OUT_13 := GD_OUT_10;
	 	GD_OUT_14 := GD_OUT_10;
	 
	END_IF;
END_PROGRAM

CONFIGURATION Config0

	RESOURCE Res0 ON PLC
		TASK task0(INTERVAL := T#20ms,PRIORITY := 0);
		PROGRAM instance0 WITH task0 : tesis0;
	END_RESOURCE
END_CONFIGURATION