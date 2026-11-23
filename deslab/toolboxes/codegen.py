"""Code generation toolbox: OpenPLC Structured Text from DESlab automata.

Only :func:`generate_ST_OPENPLC` is public. Modeling, synthesis and drawing
remain in their existing DESlab modules; this module adds no dependencies.
"""
#    DESLab v2 Copyright (C) 2026 by
#    Leonardo Bermeo <lbermeoc@unal.edu.co>
#    Mateo Rodríguez <atarodriguezper@unal.edu.co>
#    Edgar Sepulveda <ehsepulvedao@unal.edu.co>
#    MIT license (see LICENSE).

from collections import deque
from pathlib import Path

from ..src.automatadefs import fsa
from ..src.algorithms import dfs, parallel, product
from .supervisory import allevents, supcontrollable

__all__ = ["generate_ST_OPENPLC"]


class _STEmitter:
    """Private graph coordination and ST emission for one generation call."""

    def _coordinator(self, supervisors, plants, name):
        first, second = supervisors
        combined = parallel(self.models[first], self.models[second])
        if self._all_states_can_reach_marker(combined):
            return None

        controlled = self.controllable[first] | self.controllable[second]
        if combined.Sigcon != controlled:
            combined = combined.setpar(Sigcon=controlled)
        plant = parallel(*(self.models[plant] for plant in plants))
        required = parallel(combined, allevents(plant))
        # State identities are private to the coordinator. Numbering also
        # avoids projecting flat prefix-closed result states as (H, G) pairs.
        supervisor = supcontrollable(required, combined, renamestates=True)
        controlled |= required.Sigcon - combined.Sigma
        self.models[name] = self._reduce_supervisor(combined, supervisor, controlled)
        self.controllable[name] = controlled
        self._prepare_emission(name)
        return name

    @staticmethod
    def _all_states_can_reach_marker(model):
        # Parallel composition constructs only reachable states.
        return dfs(model.Graph.reverse(copy=False), model.Xm) == model.X

    def _reduce_supervisor(self, plant, supervisor, controlled):
        """Build a deterministic control congruence relative to the given plant."""
        self._require_deterministic("Coordinator", supervisor)
        states = list(self._breadth_first_states(supervisor))
        disabled = {state: set() for state in states}
        plant_marked = set()
        for sup_state, plant_state in product(supervisor, plant).X:
            disabled[sup_state].update(plant.Gamma(plant_state) - supervisor.Gamma(sup_state))
            if plant_state in plant.Xm:
                plant_marked.add(sup_state)

        partition = {state: frozenset({state}) for state in states}
        for index, left in enumerate(states):
            for right in states[index + 1:]:
                if partition[left] == partition[right]:
                    continue
                candidate = self._merge_control_cells(
                    partition, supervisor, disabled, plant_marked, left, right
                )
                if candidate is not None:
                    partition = candidate

        numbering = {
            cell: index for index, cell in enumerate(dict.fromkeys(partition.values()))
        }
        transitions = {
            (
                numbering[partition[state]],
                event,
                numbering[partition[supervisor.delta(state, event)]],
            )
            for state in states
            for event in supervisor.Gamma(state)
        }
        marked = {numbering[partition[state]] for state in supervisor.Xm}
        return fsa(range(len(numbering)), supervisor.Sigma, transitions, [0], marked,
                   Sigcon=controlled & supervisor.Sigma)

    @staticmethod
    def _merge_control_cells(partition, supervisor, disabled, plant_marked, left, right):
        candidate = partition.copy()
        pending = [(left, right)]
        while pending:
            left, right = pending.pop()
            left_cell, right_cell = candidate[left], candidate[right]
            if left_cell == right_cell:
                continue
            for first in left_cell:
                for second in right_cell:
                    if (
                        supervisor.Gamma(first) & disabled[second]
                        or supervisor.Gamma(second) & disabled[first]
                        or (
                            (first in plant_marked) == (second in plant_marked)
                            and (first in supervisor.Xm) != (second in supervisor.Xm)
                        )
                    ):
                        return None

            merged = left_cell | right_cell
            targets = {}
            for state in merged:
                candidate[state] = merged
                for event in supervisor.Gamma(state):
                    target = supervisor.delta(state, event)
                    previous = targets.setdefault(event, target)
                    if candidate[target] != candidate[previous]:
                        pending.append((target, previous))
        return candidate

    @staticmethod
    def _require_deterministic(name, model):
        if model.empty or len(model.X0) != 1 or not model.is_dfa() or model.has_epsilon():
            raise ValueError(
                f"{name!r} must be a nonempty deterministic automaton without epsilon events"
            )

    def _ordered_events(self, model, state):
        def event_order(event):
            if event in self.dict_events:
                return (0, int(self.dict_events[event]))
            return (1, str(event))

        return sorted(model.Gamma(state), key=event_order)

    def _breadth_first_states(self, model):
        initial = next(iter(model.X0))
        pending = deque([initial])
        seen = {initial}
        while pending:
            state = pending.popleft()
            yield state
            for event in self._ordered_events(model, state):
                target = model.delta(state, event)
                if target not in seen:
                    seen.add(target)
                    pending.append(target)

    def __init__(self, output_dir, event_order, state_order=None, transition_order=None):
        self.output_dir = Path(output_dir)
        self.models = {}
        self.dict_events = {event: index for index, event in enumerate(event_order or ())}
        self.controllable = {}
        self.numbering = {}
        self.event_lists = {}
        # keyed by id(model): requested numbering and transition listing
        self.state_order = state_order or {}
        self.transition_order = transition_order or {}
        self.transition_lists = {}

    def _prepare_emission(self, name):
        model = self.models[name]
        self._require_deterministic(name, model)
        ordered = list(self._breadth_first_states(model))
        if set(ordered) != model.X:
            raise ValueError(f"{name!r} must have only reachable states")
        source = self.state_order.get(id(model))
        if source is not None:
            if hasattr(source, "Gamma"):
                self._require_deterministic(f"state_order source of {name!r}", source)
                ordered = [state for state in self._breadth_first_states(source) if state in model.X]
            else:
                ordered = list(source)
            if len(ordered) != len(model.X) or set(ordered) != model.X:
                raise ValueError(f"state_order of {name!r} must list each of its states once")
            if ordered[0] not in model.X0:
                raise ValueError(f"state_order of {name!r} must start with its initial state")
        self.numbering[name] = {state: index for index, state in enumerate(ordered)}
        listed = self.transition_order.get(id(model))
        if listed is not None:
            listed = [tuple(transition) for transition in listed]
            existing = {(state, event, model.delta(state, event))
                        for state in model.X for event in model.Gamma(state)}
            if len(listed) != len(set(listed)) or set(listed) != existing:
                raise ValueError(f"transition_order of {name!r} must list each of its transitions once")
            self.transition_lists[name] = listed
        enabled = dict.fromkeys(event for _, event, _, _ in self._transitions(name))
        controlled = self.controllable.get(name, model.Sigcon)
        self.event_lists[name] = (
            [event for event in enabled if event in controlled],
            [event for event in enabled if event not in controlled],
        )

    def _events(self, name):
        return self.event_lists[name]

    def _transitions(self, name):
        model = self.models[name]
        numbering = self.numbering[name]
        controlled = self.controllable.get(name, model.Sigcon)
        listed = self.transition_lists.get(name)
        if listed is None:
            pairs = ((state, event) for state in numbering for event in self._ordered_events(model, state))
        else:
            pairs = ((state, event) for state, event, _ in listed)
        for state, event in pairs:
            yield numbering[state], event, numbering[model.delta(state, event)], event in controlled

    def _states(self, name):
        model = self.models[name]
        listed = self.transition_lists.get(name)
        if listed is None:
            for state, index in self.numbering[name].items():
                yield index, self._ordered_events(model, state)
            return
        events = {state: [] for state in self.numbering[name]}
        for state, event, _ in listed:
            events[state].append(event)
        for state, index in self.numbering[name].items():
            yield index, events[state]

    @staticmethod
    def _condition(mapping):
        variable, kind, *_ = mapping.split(":")
        if kind == "OFF":
            return "NOT " + variable
        return variable if kind == "ON" else variable + ".Q"

    def _emit_event_pairs(self, aislated, actuators, interseccion):
        # Generate direct handshake logic for auxiliary event pairs.
        out = ""
        for a in aislated:
            add = ""
            if len(actuators[a[0]].split(':')) > 1:
                add = "NOT " if actuators[a[0]].split(':')[1] == 'OFF' else ''
            out += "\tIF NOT " + actuators[a[1]].split(':')[0] + " & " + add + actuators[a[0]].split(':')[
                0] + " THEN\n\t\t"
            out += actuators[a[1]].split(':')[0] + " := 1;\n"
            out += "\tELSIF " + actuators[a[1]].split(':')[0] + " & " + add + actuators[a[0]].split(':')[
                0] + " THEN\n\t\t"
            out += actuators[a[0]].split(':')[0] + " := 0;\n\t"
            if actuators[a[0]].split(':')[0] in interseccion.keys():
                out += "\t" + actuators[a[0]].split(':')[0] + "_G[0] := 0;\n"
            out += "END_IF;\n"
        return out


    def _emit(self, supervisors, plants, actuators, namest, Mask, auxiliary, event_pairs, initial):
        # Generate the full ST code
        if not supervisors:
            raise ValueError("At least one supervisor is required")
        if len(supervisors) > 1 and len(plants) != len(supervisors):
            raise ValueError("Supply one plant per supervisor, in the same order")
        names = [*supervisors, *auxiliary]
        required = set()
        for name in names:
            controlled, uncontrolled = self._events(name)
            required.update(controlled)
            required.update(uncontrolled)
        for first, second in event_pairs:
            required.update((first, second))
        if initial != "null":
            required.add(initial)
        missing = required.difference(actuators)
        if missing:
            raise ValueError("Missing PLC signal mappings for: " + ", ".join(sorted(map(str, missing))))
        signals = set()
        for event, mapping in actuators.items():
            fields = mapping.split(":") if isinstance(mapping, str) else []
            if (len(fields) == 2 and all(fields) and fields[1] in ("ON", "OFF")
                    and ("INTERN" in fields[0] or fields[0] in signals)):
                continue
            if len(fields) == 3 and all(fields):
                if fields[1] in ("ON", "OFF"):
                    signals.add(fields[0])
                    continue
                if fields[0].startswith(("RE", "FE")):
                    signals.add(fields[1])
                    continue
            raise ValueError(f"Invalid PLC mapping for {event!r}: {mapping!r}")
        for name in names:
            for event in self._events(name)[0]:
                if actuators[event].split(":")[1] not in ("ON", "OFF"):
                    raise ValueError(f"Controllable event {event!r} requires an ON/OFF signal mapping")

        RANDOM = "FUNCTION_BLOCK random_number\n\tVAR_INPUT\n\t\tIN : BOOL;\n\tEND_VAR\n\tVAR\n\t\tM : BOOL;"
        RANDOM += "\n\t\tINIT : BOOL;\n\tEND_VAR\n\tVAR_OUTPUT\n\t\tOUT : DINT;\n\tEND_VAR\n"
        RANDOM += "\n\tIF INIT = 0 THEN\n\t\t{#include <stdio.h>}\n\t\t{#include <stdlib.h>}\n\t\tIN := 1;\n\tEND_IF;"
        RANDOM += "\n\tIF M = 0 and IN = 1 THEN\n\t\t{SetFbVar(OUT,rand())}\n\tEND_IF;\nEND_FUNCTION_BLOCK\n"
        HEADER = "PROGRAM tesis0\n"
        END = "\nEND_PROGRAM\n\n"
        END += "CONFIGURATION Config0\n\n\tRESOURCE Res0 ON PLC\n\t\tTASK task0(INTERVAL := T#20ms,PRIORITY := 0);"
        END += "\n\t\tPROGRAM instance0 WITH task0 : tesis0;" + "\n\tEND_RESOURCE\nEND_CONFIGURATION"

        intersections = {}
        coordinators = []
        for i, first in enumerate(supervisors):
            for j in range(i + 1, len(supervisors)):
                second = supervisors[j]
                coordinator = self._coordinator((first, second), (plants[i], plants[j]), f"CO_{i}_{j}")
                if coordinator is not None:
                    coordinators.append((coordinator, i, j))
                shared = set(self._events(first)[0]) & set(self._events(second)[0])
                for signal in sorted({actuators[event].split(":")[0] for event in shared}):
                    participants = intersections.setdefault(signal, [])
                    for index in (i, j):
                        if index not in participants:
                            participants.append(index)

        for coordinator, i, j in coordinators:
            for event in self._events(coordinator)[0]:
                signal = actuators[event].split(":")[0]
                if signal not in intersections:
                    intersections[signal] = [
                        index for index in (i, j) if event in self._events(supervisors[index])[0]
                    ]

        controlled = []
        uncontrolled = []
        cases = []
        selections = []
        main_models = supervisors
        for index, model in enumerate([*main_models, *auxiliary]):
            guards_on, guards_off = self._guards(model, actuators, index)
            shared = intersections if index < len(main_models) else {}
            case, selection_count = self._state_cases(model, actuators, index, shared)
            controlled.append(guards_on + "\n")
            uncontrolled.append(guards_off + "\n")
            cases.append("\n" + case + "\n")
            selections.append(selection_count)

        coordinator_cases = []
        coordinator_on = []
        coordinator_off = []
        coordinator_names = [name for name, _, _ in coordinators]
        for name in coordinator_names:
            index = len(selections)
            coordinator_cases.append(self._coordinator_case(name, state_it=index, actuators=actuators))
            guards_on, guards_off = self._guards(name, actuators, index)
            coordinator_on.append(guards_on)
            coordinator_off.append(guards_off)
            selections.append(0)

        coordinated_signals = {
            actuators[event].split(":")[0]
            for name in coordinator_names for event in self._events(name)[0]
        }
        declaration = self._declarations(
            actuators, selections, intersections, coordinator_names, Mask, initial,
        )
        mask = "".join(
            f"\t{output} := {signal};\n " for signal, mirrors in Mask.items() for output, _ in mirrors
        )
        body = "".join([
            *uncontrolled, *coordinator_off, *cases, *coordinator_cases,
            self._emit_intersections(intersections, coordinated_signals), *coordinator_on, *controlled,
            self._emit_event_pairs(event_pairs, actuators, intersections), mask,
        ])
        if initial != "null":
            startup_signal = actuators[initial].split(":")[0]
            indented_body = "\n".join("\t" + line for line in body.splitlines())
            body = (
                f"\tIF NOT initial THEN\n\t\tIF {startup_signal} THEN\n"
                "\t\t\tinitial := 1;\n\t\tEND_IF;\n\tELSIF initial THEN\n"
                + indented_body + "\n\tEND_IF;"
            )
        out = RANDOM + HEADER + declaration + body + END
        self.output_dir.mkdir(parents=True, exist_ok=True)
        with (self.output_dir / f"{namest}.st").open("w", encoding="utf-8", newline="\n") as stream:
            stream.write(out)
        return out

    def _emit_intersections(self, intersection, coordinated_signals):
        addG, addC, name_intersection = "_G[", "_C[", "aux"
        # Generate the code for the intersection between supervisors and coordinators
        out = ""
        for inter in intersection.keys():
            coordinated = inter in coordinated_signals
            aux = ""
            coor = ""
            bandera = name_intersection if coordinated else inter
            guesses = []
            for act in range(len(intersection[inter])):
                guesses.append(inter + addG + str(act) + "]")

            if len(guesses) != 1:
                if len(guesses) == 2:
                    out += "\tIF "
                    out += guesses[0] + " <> " + guesses[1] + " THEN\n"
                    out += "\t\t" + guesses[0] + " := " + inter + ";\n"
                    out += "\t\t" + guesses[1] + " := " + inter + ";"
                else:
                    out += "\tIF "
                    i = 0
                    j = 1
                    while j < len(guesses):
                        aux += "\t\t" + guesses[i] + " := " + inter + ";\n"
                        out += "(" + guesses[i] + " <> " + guesses[j] + ")"
                        i += 1
                        j += 1
                        if j != len(guesses):
                            out += " OR "
                        else:
                            out += " THEN\n"
                    aux += "\t\t" + guesses[j - 1] + " := " + inter + ";\t\t\t"
            if coordinated:
                coor += "\tIF " + bandera + " XOR " + inter + " THEN\n\t\t"
                coor += "IF NOT " + bandera + " & " + inter + addC + "0] THEN\n\t\t\t"
                coor += inter + " := 0;\n\t\t"
                coor += "ELSIF " + bandera + " & " + inter + addC + "1] THEN\n\t\t\t"
                coor += inter + " := 1;"
                coor += "\n\t\tEND_IF;"
                coor += "\n\tEND_IF;\n"
                coor += "\t" + inter + addG + "0] := " + inter + ";\n"
            out += aux + '\n'
            if len(guesses) != 1:
                out += "\tEND_IF;\n"

            out += "\t" + bandera + " := " + guesses[0] + ";\n"
            out += coor
        return out


    def _declarations(self, actuators, n_state, intersetion, CO, mascara, initial):
        # Variable blocks for OPENPLC ST version

        declaration = "\tVAR\n"
        clocks = ""
        start = "\tVAR\n"
        start += '\t\trandom : random_number;\n'
        start += '\t\trandom_num : DINT;\n'
        if initial != 'null':
            start += '\t\tinitial : BOOL;\n'
        start += f"\t\tstate : ARRAY [0..{len(n_state)}] OF DINT;\n"
        if len(CO) != 0:
            declared = []
            start += "\t\taux : BOOL := 0;\n"
            for coor in CO:
                for i in self._events(coor)[0]:
                    aux = actuators[i].split(':')[0]
                    if aux not in declared:
                        start += "\t\t" + aux + "_C : ARRAY [0..1] OF BOOL;\n"
                        declared.append(aux)
        for index, count in enumerate(n_state):
            if count:
                start += f"\t\tslt{index} : ARRAY [0..{count}] OF DINT;\n"

        if len(intersetion.keys()) > 0:
            for inter in intersetion.keys():
                start += "\t\t" + inter + "_G : ARRAY [0.." + str(len(intersetion[inter])) + "] OF BOOL;\n"

        declared = []
        for msk in mascara.keys():
            for e in mascara[msk]:
                declaration += "\t\t" + e[0] + " AT " + e[1] + " : BOOL;\n "
        for act in actuators.values():
            aux = act.split(':')
            if 'INTERN' in aux[0]:
                if aux[0] not in declared:
                    start += "\t\t" + aux[0] + " : BOOL;\n"
                    declared.append(aux[0])
                    continue
            if aux[1] == 'ON' or aux[1] == 'OFF':
                if aux[0] in declared:
                    continue
                declaration += "\t\t" + aux[0] + " AT " + aux[2] + " : BOOL;\n"
                declared.append(aux[0])
            else:
                if aux[1] not in declared:
                    declared.append(aux[1])
                    declaration += "\t\t" + aux[1] + " AT " + aux[2] + " : BOOL;\n"
                start += "\t\t" + aux[0] + " : "

                if aux[0].startswith("FE"):
                    start += "F_TRIG;\n"
                if aux[0].startswith("RE"):
                    start += "R_TRIG;\n"

                clocks += "\t" + aux[0] + '(CLK:= ' + aux[1] + ');\n'
        ran = "\trandom(\n\t\tIN := True,\n\t\tOUT => random_num);\n"
        start += "\tEND_VAR\n"
        declaration += "\tEND_VAR\n"
        return start + declaration + clocks + ran


    def _guards(self, name, actuators, n_state):  # Generate the ST code for conditional sentences
        if_uncontrollable = "\t"
        if_controllable = "\t"
        for origin, event, destination, controllable in self._transitions(name):
            if origin == destination:
                continue
            name_event = self._condition(actuators[event])
            if controllable:
                if_controllable += "IF state[" + str(n_state) + "] = " + str(origin) \
                                   + " & " + name_event \
                                   + " THEN\n  " + "\t\t" + "state[" + str(n_state) + "] := " \
                                   + str(destination) + ";\n  " + "\tELS"
            else:
                if_uncontrollable += "IF state[" + str(n_state) + "] = " + str(origin) + " & "
                if_uncontrollable += name_event
                if_uncontrollable += " THEN\n  " + "\t\t" + "state[" + str(n_state) + "] := "
                if_uncontrollable += str(destination) + ";\n  " + "\tELS"
        if if_controllable == "\t": if_controllable = ""
        if if_uncontrollable == "\t": if_uncontrollable = ""
        if not if_controllable == "":
            if_controllable = if_controllable.rstrip("ELS") + "END_IF;\n"
        if not if_uncontrollable == "":
            if_uncontrollable = if_uncontrollable.rstrip("ELS") + "END_IF;\n"
        return if_controllable, if_uncontrollable


    def _state_cases(self, name, actuators, state_index, intersections):
        guesses = {
            signal: f"_G[{participants.index(state_index)}]"
            for signal, participants in intersections.items() if state_index in participants
        }
        outputs = {}
        for event in self._events(name)[0]:
            signal, level, *_ = actuators[event].split(":")
            value = int(level != "OFF")
            outputs[event] = (f"{signal}{guesses.get(signal, '')} := {value};", value)

        selections = 0
        case = f"\tCASE state[{state_index}] OF\n  "
        for state, active_events in self._states(name):
            assignments = [outputs[event] for event in active_events if event in outputs]
            if not assignments:
                continue
            case += f"\t\t{state}:\n  "
            if len(assignments) == 1:
                assignment, value = assignments[0]
                case += f"\t\t\t{assignment}\n"
                if value == 0:
                    case += "  "
                continue
            selector = f"slt{state_index}[{selections}]"
            case += f"\t\t\tCASE {selector} OF\n  "
            for option, (assignment, _) in enumerate(assignments):
                case += f"\t\t\t\t{option}:\n  \t\t\t\t\t{assignment}\n  "
            case += (
                "\t\t\tEND_CASE;\n  "
                f"\t\t\t{selector} := (random_num + {selector}) MOD {len(assignments)};\n  "
                f"\t\t\trandom_num := random_num - {selector};\n "
            )
            selections += 1
        return case + "\tEND_CASE;", selections

    def _coordinator_case(self, name, state_it, actuators):
        flags = {}
        for event in self._events(name)[0]:
            signal, level, *_ = actuators[event].split(":")
            flags[event] = f"{signal}_C[{int(level != 'OFF')}]"

        case = f"\tCASE state[{state_it}] OF\n  "
        if flags:
            for state, active_events in self._states(name):
                enabled = set(active_events)
                case += f"\t\t{state}:\n  "
                for event, flag in flags.items():
                    case += f"\t\t\t{flag} := {int(event in enabled)};\n"
        return case + "\tEND_CASE;\n  "



def generate_ST_OPENPLC(supervisors, plants=(), actuators=None, namest="controller",
                        Mask=None, Isolated=None, initial="null", *,
                        output_dir="ST_Generated", event_pairs=(), event_order=None,
                        state_order=None, transition_order=None):
    """Generate, save and return an OpenPLC Structured Text program.

    Parameters
    ----------
    supervisors : iterable of fsa
        Deterministic, nonempty, reachable supervisors with exactly one initial
        state and no epsilon events. Each gets a separate ST state variable;
        the initial state is numbered zero.
    plants : iterable of fsa, optional
        One original plant per supervisor, in the same order. Plants supply the
        controllability of events in their alphabets. Required for multiple
        supervisors, whose conflicts are checked in pairs and coordinated when
        necessary. Pairwise checking does not prove global nonblocking.
    actuators : dict
        Event-to-PLC mapping, including sensor events and auxiliary events.
        Levels use ``"Motor:ON:%QX0.0"`` / ``"Motor:OFF:%QX0.0"``;
        inputs may likewise use ``%IX`` addresses. A subsequent alias such as
        ``"Motor:OFF"`` may omit an already declared address. Edges use
        ``"RE_Done:Sensor:%IX0.0"`` (rising) or an ``FE`` prefix (falling).
        Internal Boolean signals use ``"INTERN_0:ON"`` / ``"INTERN_0:OFF"``.
    namest : str, optional
        Output filename stem (default ``"controller"``).
    Mask : dict, optional
        PLC Boolean source or expression mapped to a list of
        ``(mirror_variable, address)`` pairs. Mirrors are assigned each scan.
    Isolated : iterable of fsa, optional
        Auxiliary automata. Each gets its own ST state variable, after the
        supervisors', and writes the outputs of its controllable events, but
        does not participate in supervisor coordination.
    initial : event, optional
        ON-level startup signal that latches controller enable; ``"null"``
        starts immediately. The controller body starts on the following scan,
        preserving the original generator's startup protocol. If this signal
        is also a supervisor event, keep it high until that event is consumed.
    output_dir : str or pathlib.Path, keyword-only
        Destination directory, created if needed (default ``"ST_Generated"``).
    event_pairs : iterable of pairs, optional, keyword-only
        ``(request_event, command_event)`` pairs of direct handshake logic, as
        in TCT's generator: while the request's condition holds, the command's
        signal is set to 1 if it is low; once it is high, the request's
        variable (and its shared-request proposal, if any) is reset to 0. Meant
        for internal request signals, for example a request that several
        supervisors share; a supervisor that alone gives a command can use the
        command event directly.
    event_order : iterable, optional, keyword-only
        Branch ordering; unspecified events follow in string order. Competing
        controllable choices use the emitted random selector, so this is not
        a deterministic scheduling policy.
    state_order : dict, optional, keyword-only
        ST state numbering of selected supervisors or auxiliary automata. Each
        value is the sequence of the automaton's states, starting with the
        initial one (number zero), or another automaton whose breadth-first
        order the states follow, such as the composition a supervisor was
        synthesized from. Other automata are numbered breadth-first from
        their initial state.
    transition_order : dict, optional, keyword-only
        For selected supervisors or auxiliary automata, the list of all their
        ``(state, event, next_state)`` transitions in the order their guards
        and output branches are written. By default each state's transitions
        follow the state numbering and ``event_order``.

    Returns
    -------
    str
        Complete ST source, also written to ``output_dir / (namest + ".st")``.

    Notes
    -----
    The target is OpenPLC with a 20 ms cyclic task and its C-extension syntax
    for random selection. Outputs retain their level until an explicit OFF
    action changes it; applications requiring command pulses must model the
    reset or supply an external pulse interface. Input edges must be observable
    at the scan rate. Each model processes at most one noncontrollable
    transition per scan; concurrent input events require external capture or
    serialization to avoid losing events. Compile and validate the resulting
    I/O protocol in OpenPLC before operating equipment.
    """
    supervisors = tuple(supervisors)
    plants = tuple(plants)
    if (plants or len(supervisors) > 1) and len(plants) != len(supervisors):
        raise ValueError("Supply one plant per supervisor, in the same order")
    auxiliary = tuple(Isolated or ())
    if any(not isinstance(model, fsa) for model in auxiliary):
        raise ValueError("Isolated must list auxiliary automata; pass event pairs with event_pairs=")
    event_pairs = [tuple(pair) for pair in event_pairs]
    if any(len(pair) != 2 for pair in event_pairs):
        raise ValueError("event_pairs must contain (request_event, command_event) pairs")
    targets = {id(model) for model in (*supervisors, *auxiliary)}

    def by_identity(option, label):
        option = dict(option or {})
        if any(id(model) not in targets for model in option):
            raise ValueError(f"{label} keys must be supervisors or auxiliary automata")
        return {id(model): value for model, value in option.items()}

    emitter = _STEmitter(output_dir, event_order, by_identity(state_order, "state_order"),
                         by_identity(transition_order, "transition_order"))
    supervisor_names = []
    plant_names = []
    for index, supervisor in enumerate(supervisors):
        emitter._require_deterministic(f"Supervisor {index}", supervisor)
        name = f"supervisor_{index}"
        emitter.models[name] = supervisor
        if plants:
            plant = plants[index]
            emitter._require_deterministic(f"Plant {index}", plant)
            plant_name = f"plant_{index}"
            emitter.models[plant_name] = plant
            plant_names.append(plant_name)
            emitter.controllable[name] = (plant.Sigcon & supervisor.Sigma) | (supervisor.Sigcon - plant.Sigma)
        else:
            emitter.controllable[name] = supervisor.Sigcon
        emitter._prepare_emission(name)
        supervisor_names.append(name)
    isolated_names = []
    for index, model in enumerate(auxiliary):
        name = f"isolated_{index}"
        emitter.models[name] = model
        emitter._prepare_emission(name)
        isolated_names.append(name)
    return emitter._emit(supervisor_names, plant_names, actuators or {}, namest,
                         Mask or {}, isolated_names, event_pairs, initial)
