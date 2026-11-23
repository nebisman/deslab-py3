"""Scan regressions for the notebook's actual ST, not an IEC/OpenPLC compiler.

The deliberately small interpreter rejects constructs outside this factory's
IF/CASE/Boolean-assignment/R_TRIG subset. The physical machines are independent
of the generator and implement the documented command/latched-finish protocol.
"""

import ast
import json
from pathlib import Path
import re

import pytest

from deslab import fsa, generate_ST_OPENPLC, iscontrollable, product, supcontrollable, trim


class FactoryST:
    def __init__(self, source, random_value=0):
        source = re.sub(r"\(\*.*?\*\)", "", source, flags=re.S)   # comments
        program = re.search(r"\bPROGRAM\s+\w+\s*\n(.*?)\bEND_PROGRAM\b", source, re.S)[1]
        self.values = {}
        for declarations in re.findall(r"\bVAR\s+(.*?)\bEND_VAR\b", program, re.S):
            for line in declarations.splitlines():
                if not line.strip():
                    continue
                match = re.fullmatch(r"\s*(\w+)\s*(?:AT\s+\S+\s*)?:\s*(.*);\s*", line)
                assert match, line
                name, kind = match.groups()
                array = re.fullmatch(r"ARRAY\s*\[0\.\.(\d+)\]\s+OF (?:DINT|BOOL)", kind)
                assert array or kind in ("BOOL", "DINT", "BOOL := 0", "R_TRIG", "random_number"), kind
                self.values[name] = [0] * (int(array[1]) + 1) if array else 0
        self.random_value = random_value
        body = re.sub(r"\bVAR\s+.*?\bEND_VAR\b", "", program, flags=re.S)
        self.lines = [line.strip() for line in body.splitlines() if line.strip()]
        self.position = 0
        self.nodes = self._block(())
        assert self.position == len(self.lines)
        self.edge_memory = {}

    def _block(self, stops):
        nodes = []
        while self.position < len(self.lines):
            line = self.lines[self.position]
            if any(re.match(stop, line) for stop in stops):
                break
            self.position += 1
            if line.startswith("IF "):
                branches = []
                condition = line[3:].removesuffix("THEN").strip()
                while True:
                    branches.append((condition, self._block((r"ELSIF ", r"ELSE$", r"END_IF;?$"))))
                    end = self.lines[self.position]
                    self.position += 1
                    if end.startswith("ELSIF "):
                        condition = end[6:].removesuffix("THEN").strip()
                        continue
                    if end == "ELSE":
                        branches.append((None, self._block((r"END_IF;?$",))))
                        self.position += 1
                    break
                nodes.append(("if", branches))
            elif line.startswith("CASE "):
                selector = line[5:].removesuffix("OF").strip()
                choices = {}
                while not self.lines[self.position].startswith("END_CASE"):
                    label = self.lines[self.position]
                    self.position += 1
                    assert re.fullmatch(r"\d+:", label), label
                    choices[int(label[:-1])] = self._block((r"\d+:$", r"END_CASE;?$"))
                self.position += 1
                nodes.append(("case", selector, choices))
            elif match := re.fullmatch(r"(\w+)\(CLK:=\s*(\w+)\);", line):
                nodes.append(("edge", *match.groups()))
            elif line == "random(":
                assert self.lines[self.position:self.position + 2] == ["IN := True,", "OUT => random_num);"]
                self.position += 2
                nodes.append(("random",))
            elif match := re.fullmatch(r"(\w+(?:\[\d+\])?)\s*:=\s*(.*);", line):
                nodes.append(("assign", *match.groups()))
            else:
                raise AssertionError(f"Unsupported factory ST statement: {line}")
        return nodes

    def _evaluate(self, source):
        if "XOR" in source:
            # The emitter uses XOR only to compare two Boolean command levels.
            left, right = source.split("XOR")
            return bool(self._evaluate(left)) != bool(self._evaluate(right))
        source = source.replace(".Q", "_Q").replace("&", " and ")
        source = source.replace("<>", "!=")
        source = re.sub(r"\bNOT\b", " not ", source)
        source = re.sub(r"\bAND\b", " and ", source)
        source = re.sub(r"\bOR\b", " or ", source)
        source = re.sub(r"\bMOD\b", " % ", source)
        source = re.sub(r"\bTRUE\b", "True", source)
        source = re.sub(r"\bFALSE\b", "False", source)
        source = re.sub(r"(?<![<>=!:])=(?!=)", "==", source).strip()
        tree = ast.parse(source, mode="eval")
        allowed = (ast.Expression, ast.BoolOp, ast.And, ast.Or, ast.UnaryOp, ast.Not,
                   ast.BinOp, ast.Add, ast.Sub, ast.Mod, ast.Compare, ast.Eq, ast.NotEq,
                   ast.Name, ast.Load, ast.Constant, ast.Subscript)
        assert all(isinstance(node, allowed) for node in ast.walk(tree)), source
        return eval(compile(tree, "<factory-st>", "eval"), {"__builtins__": {}}, self.values)

    def _run(self, nodes):
        for kind, *args in nodes:
            if kind == "if":
                for condition, body in args[0]:
                    if condition is None or self._evaluate(condition):
                        self._run(body)
                        break
            elif kind == "case":
                selector, choices = args
                self._run(choices.get(self._evaluate(selector), ()))
            elif kind == "assign":
                target, expression = args
                value = self._evaluate(expression)
                if match := re.fullmatch(r"(\w+)\[(\d+)\]", target):
                    self.values[match[1]][int(match[2])] = value
                else:
                    self.values[target] = value
            elif kind == "edge":
                instance, signal = args
                current = bool(self.values[signal])
                self.values[instance + "_Q"] = current and not self.edge_memory.get(instance, False)
                self.edge_memory[instance] = current
            elif kind == "random":
                self.values["random_num"] = self.random_value
            else:
                raise AssertionError(kind)

    def scan(self, **inputs):
        self.values.update(inputs)
        self._run(self.nodes)
        return tuple(bool(self.values.get(f"Cmd_M{i}", False)) for i in (1, 2))


@pytest.fixture
def factory(tmp_path):
    """Use the notebook's own definitions and generation call, without its setup/UI."""
    notebook = Path(__file__).resolve().parents[1] / "notebooks" / "pequena_factoria_sin_fallas.ipynb"
    cells = {cell["id"]: "".join(cell["source"]) for cell in json.loads(notebook.read_text(encoding="utf-8"))["cells"]}
    namespace = dict(fsa=fsa, generate_ST_OPENPLC=generate_ST_OPENPLC, iscontrollable=iscontrollable,
                     product=product, supcontrollable=supcontrollable, trim=trim,
                     mostrar=lambda *models: None, draw=lambda *models, **options: None,
                     repo_local=tmp_path, Path=Path)
    for index in (4, 6, 8, 12, 18, 20, 22):
        exec(compile(cells[f"factory-{index:02d}"], str(notebook), "exec"), namespace)
    return namespace["S"], namespace["st"]


@pytest.mark.parametrize("durations, clear_delay", [
    ((1, 1), 1), ((2, 3), 4), ((3, 5), 4), ((7, 2), 9), ((11, 13), 2),
])
def test_emitted_factory_st_tracks_physical_events_and_latched_rearm(factory, durations, clear_delay):
    supervisor, source = factory
    plc = FactoryST(source)
    expected = next(iter(supervisor.X0))
    commands = (False, False)
    finish = [False, False]
    remaining = [None, None]
    low_scans = [0, 0]
    starts = [0, 0]
    completions = [0, 0]
    buffer = 0
    abstract_states = {0: expected}
    numeric_states = {expected: 0}
    previous_completion = None
    adjacent_completions = 0

    for scan in range(400):
        due = []
        for machine in range(2):
            if remaining[machine] is not None:
                remaining[machine] -= 1
                if remaining[machine] <= 0:
                    due.append(machine)
            elif finish[machine] and not commands[machine]:
                low_scans[machine] += 1
                if low_scans[machine] >= clear_delay:
                    finish[machine] = False
        # The notebook explicitly assumes distinct scans for independent finishes.
        # Retain the second completion for the next scan rather than losing it.
        if due:
            machine = due[0]
            finish[machine] = True
            remaining[machine] = None
            low_scans[machine] = 0
            completions[machine] += 1
            event = f"e{machine + 1}"
            assert event in supervisor.Gamma(expected), (scan, expected, event)
            expected = supervisor.delta(expected, event)
            if machine == 0:
                buffer += 1
                assert buffer <= 1, "M1 completed into a full buffer"
            adjacent_completions += previous_completion == scan - 1
            previous_completion = scan

        outputs = plc.scan(Fin_M1=finish[0], Fin_M2=finish[1])
        rising = [machine for machine in range(2) if outputs[machine] and not commands[machine]]
        assert len(rising) <= 1, "A single supervisor counted multiple control events in one scan"
        for machine in range(2):
            assert not (finish[machine] and outputs[machine]), "Command reactivated before finish cleared"
            if remaining[machine] is not None:
                assert outputs[machine], "Command dropped before the physical cycle ended"
        for machine in rising:
            assert remaining[machine] is None and not finish[machine], "Machine restarted while busy/rearming"
            event = f"s{machine + 1}"
            assert event in supervisor.Gamma(expected), (scan, expected, event)
            expected = supervisor.delta(expected, event)
            starts[machine] += 1
            remaining[machine] = durations[machine]
            if machine == 1:
                assert buffer == 1, "M2 started with an empty buffer"
                buffer -= 1
        assert 0 <= buffer <= 1
        actual = plc.values["state"][0]
        assert abstract_states.setdefault(actual, expected) == expected, "ST advanced without the matching physical event"
        assert numeric_states.setdefault(expected, actual) == actual, "ST state does not represent the event trace"
        commands = outputs

    assert min(starts) >= 15 and min(completions) >= 14
    # Some states can be traversed between the input and output phases of a
    # single scan. The 3/5 schedule additionally reaches all six at scan ends.
    if durations == (3, 5):
        assert len(abstract_states) == len(supervisor.X)
    # At least one schedule exercises consecutive input-event scans.
    if durations == (1, 1):
        assert adjacent_completions > 0
