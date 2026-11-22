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
		state : ARRAY [0..5] OF DINT;
		slt1 : ARRAY [0..8] OF DINT;
		slt2 : ARRAY [0..15] OF DINT;
		GD_OUT_4_G : ARRAY [0..2] OF BOOL;
		GD_OUT_7_G : ARRAY [0..2] OF BOOL;
		GD_OUT_8_G : ARRAY [0..2] OF BOOL;
		GD_OUT_5_G : ARRAY [0..3] OF BOOL;
		FE_LaP : F_TRIG;
		FE_BaP : F_TRIG;
		FE_PaL : F_TRIG;
		FE_Zag : F_TRIG;
		FE_Xag : F_TRIG;
	END_VAR
	VAR
		GD_OUT_12 AT %QX101.2 : BOOL;
 		GD_OUT_13 AT %QX101.3 : BOOL;
 		GD_OUT_2 AT %QX100.2 : BOOL;
		GD_OUT_3 AT %QX100.3 : BOOL;
		GD_OUT_4 AT %QX100.4 : BOOL;
		GD_OUT_5 AT %QX100.5 : BOOL;
		GD_OUT_6 AT %QX100.6 : BOOL;
		GD_OUT_7 AT %QX100.7 : BOOL;
		GD_OUT_8 AT %QX101.0 : BOOL;
		GD_OUT_9 AT %QX101.1 : BOOL;
		GD_IN_15 AT %IX100.15 : BOOL;
		GD_IN_2 AT %IX100.2 : BOOL;
		GD_IN_4 AT %IX100.4 : BOOL;
		GD_IN_3 AT %IX100.3 : BOOL;
		GD_IN_9 AT %IX101.1 : BOOL;
		GD_IN_5 AT %IX100.5 : BOOL;
		GD_IN_6 AT %IX100.6 : BOOL;
		GD_IN_7 AT %IX100.7 : BOOL;
		GD_IN_8 AT %IX101.0 : BOOL;
		GD_IN_10 AT %IX102.5 : BOOL;
		GD_IN_11 AT %IX102.6 : BOOL;
	END_VAR
	FE_LaP(CLK:= GD_IN_2);
	FE_BaP(CLK:= GD_IN_3);
	FE_PaL(CLK:= GD_IN_9);
	FE_Zag(CLK:= GD_IN_6);
	FE_Xag(CLK:= GD_IN_7);
	random(
		IN := True,
		OUT => random_num);
	IF state[0] = 0 & GD_IN_15 THEN
  		state[0] := 1;
  	ELSIF state[0] = 2 & FE_LaP.Q THEN
  		state[0] := 3;
  	ELSIF state[0] = 5 & GD_IN_4 THEN
  		state[0] := 6;
  	END_IF;

	IF state[1] = 0 & GD_IN_4 THEN
  		state[1] := 1;
  	ELSIF state[1] = 2 & GD_IN_4 THEN
  		state[1] := 3;
  	ELSIF state[1] = 4 & FE_Zag.Q THEN
  		state[1] := 6;
  	ELSIF state[1] = 5 & FE_Zag.Q THEN
  		state[1] := 7;
  	ELSIF state[1] = 12 & FE_Zag.Q THEN
  		state[1] := 14;
  	ELSIF state[1] = 13 & FE_Zag.Q THEN
  		state[1] := 15;
  	ELSIF state[1] = 16 & FE_Xag.Q THEN
  		state[1] := 18;
  	ELSIF state[1] = 17 & FE_Xag.Q THEN
  		state[1] := 19;
  	ELSIF state[1] = 20 & FE_Zag.Q THEN
  		state[1] := 22;
  	ELSIF state[1] = 21 & FE_Zag.Q THEN
  		state[1] := 23;
  	ELSIF state[1] = 26 & FE_Zag.Q THEN
  		state[1] := 28;
  	ELSIF state[1] = 27 & FE_Zag.Q THEN
  		state[1] := 29;
  	ELSIF state[1] = 30 & FE_Xag.Q THEN
  		state[1] := 0;
  	ELSIF state[1] = 31 & FE_Xag.Q THEN
  		state[1] := 2;
  	END_IF;

	IF state[2] = 2 & GD_IN_5 THEN
  		state[2] := 4;
  	ELSIF state[2] = 3 & GD_IN_5 THEN
  		state[2] := 5;
  	ELSIF state[2] = 6 & FE_Xag.Q THEN
  		state[2] := 8;
  	ELSIF state[2] = 7 & FE_Xag.Q THEN
  		state[2] := 9;
  	ELSIF state[2] = 10 & FE_Xag.Q THEN
  		state[2] := 12;
  	ELSIF state[2] = 11 & FE_Xag.Q THEN
  		state[2] := 16;
  	ELSIF state[2] = 13 & FE_Xag.Q THEN
  		state[2] := 20;
  	ELSIF state[2] = 14 & FE_Xag.Q THEN
  		state[2] := 17;
  	ELSIF state[2] = 15 & FE_Xag.Q THEN
  		state[2] := 19;
  	ELSIF state[2] = 18 & FE_Xag.Q THEN
  		state[2] := 25;
  	ELSIF state[2] = 21 & FE_Xag.Q THEN
  		state[2] := 24;
  	ELSIF state[2] = 22 & FE_Xag.Q THEN
  		state[2] := 27;
  	ELSIF state[2] = 22 & GD_IN_5 THEN
  		state[2] := 29;
  	ELSIF state[2] = 23 & FE_Xag.Q THEN
  		state[2] := 30;
  	ELSIF state[2] = 26 & FE_Xag.Q THEN
  		state[2] := 0;
  	ELSIF state[2] = 27 & GD_IN_5 THEN
  		state[2] := 34;
  	ELSIF state[2] = 28 & FE_Xag.Q THEN
  		state[2] := 32;
  	ELSIF state[2] = 28 & GD_IN_5 THEN
  		state[2] := 35;
  	ELSIF state[2] = 29 & FE_Xag.Q THEN
  		state[2] := 34;
  	ELSIF state[2] = 31 & FE_Xag.Q THEN
  		state[2] := 1;
  	ELSIF state[2] = 32 & GD_IN_5 THEN
  		state[2] := 37;
  	ELSIF state[2] = 33 & FE_Xag.Q THEN
  		state[2] := 2;
  	ELSIF state[2] = 33 & GD_IN_5 THEN
  		state[2] := 38;
  	ELSIF state[2] = 35 & FE_Xag.Q THEN
  		state[2] := 37;
  	ELSIF state[2] = 36 & FE_Xag.Q THEN
  		state[2] := 3;
  	ELSIF state[2] = 36 & GD_IN_5 THEN
  		state[2] := 39;
  	ELSIF state[2] = 38 & FE_Xag.Q THEN
  		state[2] := 4;
  	ELSIF state[2] = 39 & FE_Xag.Q THEN
  		state[2] := 5;
  	END_IF;

	IF state[3] = 0 & GD_IN_15 THEN
  		state[3] := 1;
  	ELSIF state[3] = 2 & FE_BaP.Q THEN
  		state[3] := 3;
  	ELSIF state[3] = 5 & GD_IN_5 THEN
  		state[3] := 6;
  	END_IF;

	IF state[4] = 3 & GD_IN_8 THEN
  		state[4] := 4;
  	ELSIF state[4] = 4 & FE_PaL.Q THEN
  		state[4] := 5;
  	END_IF;


	CASE state[0] OF
  		1:
  			GD_OUT_2 := 1;
		3:
  			GD_OUT_2 := 0;
  		4:
  			GD_OUT_4_G[0] := 1;
		6:
  			GD_OUT_4_G[0] := 0;
  	END_CASE;

	CASE state[1] OF
  		0:
  			GD_OUT_4_G[1] := 1;
		1:
  			CASE slt1[0] OF
  				0:
  					GD_OUT_4_G[1] := 1;
  				1:
  					GD_OUT_6 := 1;
  			END_CASE;
  			slt1[0] := (random_num + slt1[0]) MOD 2;
  			random_num := random_num - slt1[0];
 		3:
  			GD_OUT_6 := 1;
		4:
  			GD_OUT_4_G[1] := 1;
		6:
  			CASE slt1[1] OF
  				0:
  					GD_OUT_4_G[1] := 1;
  				1:
  					GD_OUT_7_G[0] := 1;
  			END_CASE;
  			slt1[1] := (random_num + slt1[1]) MOD 2;
  			random_num := random_num - slt1[1];
 		7:
  			GD_OUT_7_G[0] := 1;
		8:
  			GD_OUT_4_G[1] := 1;
		9:
  			GD_OUT_4_G[1] := 0;
  		10:
  			CASE slt1[2] OF
  				0:
  					GD_OUT_4_G[1] := 1;
  				1:
  					GD_OUT_6 := 0;
  			END_CASE;
  			slt1[2] := (random_num + slt1[2]) MOD 2;
  			random_num := random_num - slt1[2];
 		11:
  			GD_OUT_6 := 0;
  		12:
  			GD_OUT_4_G[1] := 1;
		14:
  			CASE slt1[3] OF
  				0:
  					GD_OUT_4_G[1] := 1;
  				1:
  					GD_OUT_8_G[0] := 1;
  			END_CASE;
  			slt1[3] := (random_num + slt1[3]) MOD 2;
  			random_num := random_num - slt1[3];
 		15:
  			GD_OUT_8_G[0] := 1;
		16:
  			GD_OUT_4_G[1] := 1;
		18:
  			CASE slt1[4] OF
  				0:
  					GD_OUT_4_G[1] := 1;
  				1:
  					GD_OUT_6 := 1;
  			END_CASE;
  			slt1[4] := (random_num + slt1[4]) MOD 2;
  			random_num := random_num - slt1[4];
 		19:
  			GD_OUT_6 := 1;
		20:
  			GD_OUT_4_G[1] := 1;
		22:
  			CASE slt1[5] OF
  				0:
  					GD_OUT_4_G[1] := 1;
  				1:
  					GD_OUT_7_G[0] := 0;
  			END_CASE;
  			slt1[5] := (random_num + slt1[5]) MOD 2;
  			random_num := random_num - slt1[5];
 		23:
  			GD_OUT_7_G[0] := 0;
  		24:
  			CASE slt1[6] OF
  				0:
  					GD_OUT_4_G[1] := 1;
  				1:
  					GD_OUT_6 := 0;
  			END_CASE;
  			slt1[6] := (random_num + slt1[6]) MOD 2;
  			random_num := random_num - slt1[6];
 		25:
  			GD_OUT_6 := 0;
  		26:
  			GD_OUT_4_G[1] := 1;
		28:
  			CASE slt1[7] OF
  				0:
  					GD_OUT_4_G[1] := 1;
  				1:
  					GD_OUT_8_G[0] := 0;
  			END_CASE;
  			slt1[7] := (random_num + slt1[7]) MOD 2;
  			random_num := random_num - slt1[7];
 		29:
  			GD_OUT_8_G[0] := 0;
  		30:
  			GD_OUT_4_G[1] := 1;
	END_CASE;

	CASE state[2] OF
  		0:
  			CASE slt2[0] OF
  				0:
  					GD_OUT_7_G[1] := 1;
  				1:
  					GD_OUT_5_G[0] := 1;
  			END_CASE;
  			slt2[0] := (random_num + slt2[0]) MOD 2;
  			random_num := random_num - slt2[0];
 		1:
  			GD_OUT_5_G[0] := 1;
		2:
  			GD_OUT_7_G[1] := 1;
		4:
  			CASE slt2[1] OF
  				0:
  					GD_OUT_7_G[1] := 1;
  				1:
  					GD_OUT_8_G[1] := 1;
  			END_CASE;
  			slt2[1] := (random_num + slt2[1]) MOD 2;
  			random_num := random_num - slt2[1];
 		5:
  			GD_OUT_8_G[1] := 1;
		6:
  			GD_OUT_7_G[1] := 1;
		7:
  			GD_OUT_7_G[1] := 0;
  		8:
  			CASE slt2[2] OF
  				0:
  					GD_OUT_7_G[1] := 1;
  				1:
  					GD_OUT_8_G[1] := 0;
  			END_CASE;
  			slt2[2] := (random_num + slt2[2]) MOD 2;
  			random_num := random_num - slt2[2];
 		9:
  			CASE slt2[3] OF
  				0:
  					GD_OUT_7_G[1] := 0;
  				1:
  					GD_OUT_8_G[1] := 0;
  			END_CASE;
  			slt2[3] := (random_num + slt2[3]) MOD 2;
  			random_num := random_num - slt2[3];
 		10:
  			CASE slt2[4] OF
  				0:
  					GD_OUT_7_G[1] := 1;
  				1:
  					GD_OUT_5_G[0] := 0;
  			END_CASE;
  			slt2[4] := (random_num + slt2[4]) MOD 2;
  			random_num := random_num - slt2[4];
 		11:
  			GD_OUT_7_G[1] := 1;
		12:
  			CASE slt2[5] OF
  				0:
  					GD_OUT_7_G[1] := 1;
  				1:
  					GD_OUT_8_G[1] := 0;
  				2:
  					GD_OUT_5_G[0] := 0;
  			END_CASE;
  			slt2[5] := (random_num + slt2[5]) MOD 3;
  			random_num := random_num - slt2[5];
 		13:
  			GD_OUT_7_G[1] := 0;
  		14:
  			GD_OUT_5_G[0] := 0;
  		15:
  			CASE slt2[6] OF
  				0:
  					GD_OUT_7_G[1] := 1;
  				1:
  					GD_OUT_5_G[0] := 1;
  			END_CASE;
  			slt2[6] := (random_num + slt2[6]) MOD 2;
  			random_num := random_num - slt2[6];
 		16:
  			GD_OUT_7_G[1] := 1;
		17:
  			CASE slt2[7] OF
  				0:
  					GD_OUT_8_G[1] := 0;
  				1:
  					GD_OUT_5_G[0] := 0;
  			END_CASE;
  			slt2[7] := (random_num + slt2[7]) MOD 2;
  			random_num := random_num - slt2[7];
 		18:
  			CASE slt2[8] OF
  				0:
  					GD_OUT_7_G[1] := 1;
  				1:
  					GD_OUT_5_G[0] := 0;
  			END_CASE;
  			slt2[8] := (random_num + slt2[8]) MOD 2;
  			random_num := random_num - slt2[8];
 		19:
  			CASE slt2[9] OF
  				0:
  					GD_OUT_7_G[1] := 1;
  				1:
  					GD_OUT_8_G[1] := 0;
  				2:
  					GD_OUT_5_G[0] := 1;
  			END_CASE;
  			slt2[9] := (random_num + slt2[9]) MOD 3;
  			random_num := random_num - slt2[9];
 		20:
  			GD_OUT_7_G[1] := 0;
  		21:
  			GD_OUT_5_G[0] := 1;
		22:
  			GD_OUT_7_G[1] := 1;
		23:
  			GD_OUT_5_G[0] := 0;
  		24:
  			CASE slt2[10] OF
  				0:
  					GD_OUT_8_G[1] := 0;
  				1:
  					GD_OUT_5_G[0] := 1;
  			END_CASE;
  			slt2[10] := (random_num + slt2[10]) MOD 2;
  			random_num := random_num - slt2[10];
 		25:
  			CASE slt2[11] OF
  				0:
  					GD_OUT_7_G[1] := 1;
  				1:
  					GD_OUT_5_G[0] := 0;
  			END_CASE;
  			slt2[11] := (random_num + slt2[11]) MOD 2;
  			random_num := random_num - slt2[11];
 		26:
  			CASE slt2[12] OF
  				0:
  					GD_OUT_7_G[1] := 1;
  				1:
  					GD_OUT_5_G[0] := 1;
  			END_CASE;
  			slt2[12] := (random_num + slt2[12]) MOD 2;
  			random_num := random_num - slt2[12];
 		27:
  			CASE slt2[13] OF
  				0:
  					GD_OUT_7_G[1] := 1;
  				1:
  					GD_OUT_8_G[1] := 0;
  			END_CASE;
  			slt2[13] := (random_num + slt2[13]) MOD 2;
  			random_num := random_num - slt2[13];
 		29:
  			GD_OUT_7_G[1] := 1;
		30:
  			GD_OUT_5_G[0] := 0;
  		31:
  			GD_OUT_5_G[0] := 1;
		32:
  			GD_OUT_8_G[1] := 0;
  		33:
  			GD_OUT_7_G[1] := 1;
		34:
  			CASE slt2[14] OF
  				0:
  					GD_OUT_7_G[1] := 1;
  				1:
  					GD_OUT_8_G[1] := 0;
  			END_CASE;
  			slt2[14] := (random_num + slt2[14]) MOD 2;
  			random_num := random_num - slt2[14];
 		37:
  			GD_OUT_8_G[1] := 0;
  		38:
  			GD_OUT_7_G[1] := 1;
	END_CASE;

	CASE state[3] OF
  		1:
  			GD_OUT_3 := 1;
		3:
  			GD_OUT_3 := 0;
  		4:
  			GD_OUT_5_G[1] := 1;
		6:
  			GD_OUT_5_G[1] := 0;
  	END_CASE;

	CASE state[4] OF
  		0:
  			GD_OUT_5_G[2] := 1;
		1:
  			GD_OUT_5_G[2] := 0;
  		2:
  			GD_OUT_9 := 1;
		5:
  			GD_OUT_9 := 0;
  	END_CASE;
	IF GD_OUT_4_G[0] <> GD_OUT_4_G[1] THEN
		GD_OUT_4_G[0] := GD_OUT_4;
		GD_OUT_4_G[1] := GD_OUT_4;
	END_IF;
	GD_OUT_4 := GD_OUT_4_G[0];
	IF GD_OUT_7_G[0] <> GD_OUT_7_G[1] THEN
		GD_OUT_7_G[0] := GD_OUT_7;
		GD_OUT_7_G[1] := GD_OUT_7;
	END_IF;
	GD_OUT_7 := GD_OUT_7_G[0];
	IF GD_OUT_8_G[0] <> GD_OUT_8_G[1] THEN
		GD_OUT_8_G[0] := GD_OUT_8;
		GD_OUT_8_G[1] := GD_OUT_8;
	END_IF;
	GD_OUT_8 := GD_OUT_8_G[0];
	IF (GD_OUT_5_G[0] <> GD_OUT_5_G[1]) OR (GD_OUT_5_G[1] <> GD_OUT_5_G[2]) THEN
		GD_OUT_5_G[0] := GD_OUT_5;
		GD_OUT_5_G[1] := GD_OUT_5;
		GD_OUT_5_G[2] := GD_OUT_5;			
	END_IF;
	GD_OUT_5 := GD_OUT_5_G[0];
	IF state[0] = 1 & GD_OUT_2 THEN
  		state[0] := 2;
  	ELSIF state[0] = 3 & NOT GD_OUT_2 THEN
  		state[0] := 4;
  	ELSIF state[0] = 4 & GD_OUT_4 THEN
  		state[0] := 5;
  	ELSIF state[0] = 6 & NOT GD_OUT_4 THEN
  		state[0] := 1;
  	END_IF;

	IF state[1] = 0 & GD_OUT_4 THEN
  		state[1] := 2;
  	ELSIF state[1] = 1 & GD_OUT_4 THEN
  		state[1] := 3;
  	ELSIF state[1] = 1 & GD_OUT_6 THEN
  		state[1] := 4;
  	ELSIF state[1] = 3 & GD_OUT_6 THEN
  		state[1] := 5;
  	ELSIF state[1] = 4 & GD_OUT_4 THEN
  		state[1] := 5;
  	ELSIF state[1] = 6 & GD_OUT_4 THEN
  		state[1] := 7;
  	ELSIF state[1] = 6 & GD_OUT_7 THEN
  		state[1] := 8;
  	ELSIF state[1] = 7 & GD_OUT_7 THEN
  		state[1] := 9;
  	ELSIF state[1] = 8 & GD_OUT_4 THEN
  		state[1] := 9;
  	ELSIF state[1] = 9 & NOT GD_OUT_4 THEN
  		state[1] := 10;
  	ELSIF state[1] = 10 & GD_OUT_4 THEN
  		state[1] := 11;
  	ELSIF state[1] = 10 & NOT GD_OUT_6 THEN
  		state[1] := 12;
  	ELSIF state[1] = 11 & NOT GD_OUT_6 THEN
  		state[1] := 13;
  	ELSIF state[1] = 12 & GD_OUT_4 THEN
  		state[1] := 13;
  	ELSIF state[1] = 14 & GD_OUT_4 THEN
  		state[1] := 15;
  	ELSIF state[1] = 14 & GD_OUT_8 THEN
  		state[1] := 16;
  	ELSIF state[1] = 15 & GD_OUT_8 THEN
  		state[1] := 17;
  	ELSIF state[1] = 16 & GD_OUT_4 THEN
  		state[1] := 17;
  	ELSIF state[1] = 18 & GD_OUT_4 THEN
  		state[1] := 19;
  	ELSIF state[1] = 18 & GD_OUT_6 THEN
  		state[1] := 20;
  	ELSIF state[1] = 19 & GD_OUT_6 THEN
  		state[1] := 21;
  	ELSIF state[1] = 20 & GD_OUT_4 THEN
  		state[1] := 21;
  	ELSIF state[1] = 22 & GD_OUT_4 THEN
  		state[1] := 23;
  	ELSIF state[1] = 22 & NOT GD_OUT_7 THEN
  		state[1] := 24;
  	ELSIF state[1] = 23 & NOT GD_OUT_7 THEN
  		state[1] := 25;
  	ELSIF state[1] = 24 & GD_OUT_4 THEN
  		state[1] := 25;
  	ELSIF state[1] = 24 & NOT GD_OUT_6 THEN
  		state[1] := 26;
  	ELSIF state[1] = 25 & NOT GD_OUT_6 THEN
  		state[1] := 27;
  	ELSIF state[1] = 26 & GD_OUT_4 THEN
  		state[1] := 27;
  	ELSIF state[1] = 28 & GD_OUT_4 THEN
  		state[1] := 29;
  	ELSIF state[1] = 28 & NOT GD_OUT_8 THEN
  		state[1] := 30;
  	ELSIF state[1] = 29 & NOT GD_OUT_8 THEN
  		state[1] := 31;
  	ELSIF state[1] = 30 & GD_OUT_4 THEN
  		state[1] := 31;
  	END_IF;

	IF state[2] = 0 & GD_OUT_7 THEN
  		state[2] := 1;
  	ELSIF state[2] = 0 & GD_OUT_5 THEN
  		state[2] := 2;
  	ELSIF state[2] = 1 & GD_OUT_5 THEN
  		state[2] := 3;
  	ELSIF state[2] = 2 & GD_OUT_7 THEN
  		state[2] := 3;
  	ELSIF state[2] = 4 & GD_OUT_7 THEN
  		state[2] := 5;
  	ELSIF state[2] = 4 & GD_OUT_8 THEN
  		state[2] := 6;
  	ELSIF state[2] = 5 & GD_OUT_8 THEN
  		state[2] := 7;
  	ELSIF state[2] = 6 & GD_OUT_7 THEN
  		state[2] := 7;
  	ELSIF state[2] = 7 & NOT GD_OUT_7 THEN
  		state[2] := 10;
  	ELSIF state[2] = 8 & GD_OUT_7 THEN
  		state[2] := 9;
  	ELSIF state[2] = 8 & NOT GD_OUT_8 THEN
  		state[2] := 11;
  	ELSIF state[2] = 9 & NOT GD_OUT_7 THEN
  		state[2] := 12;
  	ELSIF state[2] = 9 & NOT GD_OUT_8 THEN
  		state[2] := 13;
  	ELSIF state[2] = 10 & GD_OUT_7 THEN
  		state[2] := 14;
  	ELSIF state[2] = 10 & NOT GD_OUT_5 THEN
  		state[2] := 15;
  	ELSIF state[2] = 11 & GD_OUT_7 THEN
  		state[2] := 13;
  	ELSIF state[2] = 12 & GD_OUT_7 THEN
  		state[2] := 17;
  	ELSIF state[2] = 12 & NOT GD_OUT_8 THEN
  		state[2] := 18;
  	ELSIF state[2] = 12 & NOT GD_OUT_5 THEN
  		state[2] := 19;
  	ELSIF state[2] = 13 & NOT GD_OUT_7 THEN
  		state[2] := 18;
  	ELSIF state[2] = 14 & NOT GD_OUT_5 THEN
  		state[2] := 21;
  	ELSIF state[2] = 15 & GD_OUT_7 THEN
  		state[2] := 21;
  	ELSIF state[2] = 15 & GD_OUT_5 THEN
  		state[2] := 22;
  	ELSIF state[2] = 16 & GD_OUT_7 THEN
  		state[2] := 20;
  	ELSIF state[2] = 17 & NOT GD_OUT_8 THEN
  		state[2] := 23;
  	ELSIF state[2] = 17 & NOT GD_OUT_5 THEN
  		state[2] := 24;
  	ELSIF state[2] = 18 & GD_OUT_7 THEN
  		state[2] := 23;
  	ELSIF state[2] = 18 & NOT GD_OUT_5 THEN
  		state[2] := 26;
  	ELSIF state[2] = 19 & GD_OUT_7 THEN
  		state[2] := 24;
  	ELSIF state[2] = 19 & NOT GD_OUT_8 THEN
  		state[2] := 26;
  	ELSIF state[2] = 19 & GD_OUT_5 THEN
  		state[2] := 27;
  	ELSIF state[2] = 20 & NOT GD_OUT_7 THEN
  		state[2] := 25;
  	ELSIF state[2] = 21 & GD_OUT_5 THEN
  		state[2] := 28;
  	ELSIF state[2] = 22 & GD_OUT_7 THEN
  		state[2] := 28;
  	ELSIF state[2] = 23 & NOT GD_OUT_5 THEN
  		state[2] := 31;
  	ELSIF state[2] = 24 & NOT GD_OUT_8 THEN
  		state[2] := 31;
  	ELSIF state[2] = 24 & GD_OUT_5 THEN
  		state[2] := 32;
  	ELSIF state[2] = 25 & GD_OUT_7 THEN
  		state[2] := 30;
  	ELSIF state[2] = 25 & NOT GD_OUT_5 THEN
  		state[2] := 0;
  	ELSIF state[2] = 26 & GD_OUT_7 THEN
  		state[2] := 31;
  	ELSIF state[2] = 26 & GD_OUT_5 THEN
  		state[2] := 33;
  	ELSIF state[2] = 27 & GD_OUT_7 THEN
  		state[2] := 32;
  	ELSIF state[2] = 27 & NOT GD_OUT_8 THEN
  		state[2] := 33;
  	ELSIF state[2] = 29 & GD_OUT_7 THEN
  		state[2] := 35;
  	ELSIF state[2] = 30 & NOT GD_OUT_5 THEN
  		state[2] := 1;
  	ELSIF state[2] = 31 & GD_OUT_5 THEN
  		state[2] := 36;
  	ELSIF state[2] = 32 & NOT GD_OUT_8 THEN
  		state[2] := 36;
  	ELSIF state[2] = 33 & GD_OUT_7 THEN
  		state[2] := 36;
  	ELSIF state[2] = 34 & GD_OUT_7 THEN
  		state[2] := 37;
  	ELSIF state[2] = 34 & NOT GD_OUT_8 THEN
  		state[2] := 38;
  	ELSIF state[2] = 37 & NOT GD_OUT_8 THEN
  		state[2] := 39;
  	ELSIF state[2] = 38 & GD_OUT_7 THEN
  		state[2] := 39;
  	END_IF;

	IF state[3] = 1 & GD_OUT_3 THEN
  		state[3] := 2;
  	ELSIF state[3] = 3 & NOT GD_OUT_3 THEN
  		state[3] := 4;
  	ELSIF state[3] = 4 & GD_OUT_5 THEN
  		state[3] := 5;
  	ELSIF state[3] = 6 & NOT GD_OUT_5 THEN
  		state[3] := 1;
  	END_IF;

	IF state[4] = 0 & GD_OUT_5 THEN
  		state[4] := 1;
  	ELSIF state[4] = 1 & NOT GD_OUT_5 THEN
  		state[4] := 2;
  	ELSIF state[4] = 2 & GD_OUT_9 THEN
  		state[4] := 3;
  	ELSIF state[4] = 5 & NOT GD_OUT_9 THEN
  		state[4] := 0;
  	END_IF;

	GD_OUT_12 := GD_IN_10;
 	GD_OUT_13 := GD_IN_11;
 
END_PROGRAM

CONFIGURATION Config0

	RESOURCE Res0 ON PLC
		TASK task0(INTERVAL := T#20ms,PRIORITY := 0);
		PROGRAM instance0 WITH task0 : tesis0;
	END_RESOURCE
END_CONFIGURATION