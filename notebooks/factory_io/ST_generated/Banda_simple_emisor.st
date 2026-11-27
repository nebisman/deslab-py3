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
		state : ARRAY [0..1] OF DINT;
		RE_INICIO : R_TRIG;
		RE_SALE : R_TRIG;
	END_VAR
	VAR
		Banda AT %QX100.0 : BOOL;
 		Remover AT %QX100.2 : BOOL;
 		Emisor AT %QX100.1 : BOOL;
		SensorInicio AT %IX100.0 : BOOL;
		SensorFin AT %IX100.1 : BOOL;
	END_VAR
	RE_INICIO(CLK:= SensorInicio);
	RE_SALE(CLK:= SensorFin);
	random(
		IN := True,
		OUT => random_num);
	IF state[0] = 0 & RE_INICIO.Q THEN
  		state[0] := 1;
  	ELSIF state[0] = 1 & RE_SALE.Q THEN
  		state[0] := 0;
  	ELSIF state[0] = 2 & RE_INICIO.Q THEN
  		state[0] := 4;
  	ELSIF state[0] = 3 & RE_SALE.Q THEN
  		state[0] := 5;
  	ELSIF state[0] = 4 & RE_SALE.Q THEN
  		state[0] := 6;
  	ELSIF state[0] = 5 & RE_INICIO.Q THEN
  		state[0] := 8;
  	ELSIF state[0] = 6 & RE_INICIO.Q THEN
  		state[0] := 8;
  	ELSIF state[0] = 7 & RE_SALE.Q THEN
  		state[0] := 0;
  	ELSIF state[0] = 8 & RE_SALE.Q THEN
  		state[0] := 6;
  	END_IF;


	CASE state[0] OF
  		0:
  			Emisor := 1;
		1:
  			Emisor := 1;
		4:
  			Emisor := 0;
  		6:
  			Emisor := 0;
  		8:
  			Emisor := 0;
  	END_CASE;
	IF state[0] = 0 & Emisor THEN
  		state[0] := 2;
  	ELSIF state[0] = 1 & Emisor THEN
  		state[0] := 3;
  	ELSIF state[0] = 4 & NOT Emisor THEN
  		state[0] := 7;
  	ELSIF state[0] = 6 & NOT Emisor THEN
  		state[0] := 0;
  	ELSIF state[0] = 8 & NOT Emisor THEN
  		state[0] := 1;
  	END_IF;

	Banda := TRUE;
 	Remover := TRUE;
 
END_PROGRAM

CONFIGURATION Config0

	RESOURCE Res0 ON PLC
		TASK task0(INTERVAL := T#20ms,PRIORITY := 0);
		PROGRAM instance0 WITH task0 : supcon;
	END_RESOURCE
END_CONFIGURATION