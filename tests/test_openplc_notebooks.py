"""Checks for the notebooks in notebooks/factory_io that generate OpenPLC ST.

The notebooks' own cells are executed (without the Colab setup and drawings). The small
factory programs (with one supervisor, and with two modular supervisors and breakdowns) and
the transfer line program are simulated scan by scan with stations that follow the notebooks'
interface contracts; the assembly line program must equal the one generated with TCT by
TCT_Proyect.
"""

import hashlib
import json
import random
import re
from pathlib import Path

import pytest

import deslab
from test_factory_st_runtime import FactoryST

NOTEBOOKS = Path(__file__).resolve().parents[1] / "notebooks" / "factory_io"


def run_cells(name, prefix, indices, tmp_path, monkeypatch):
    notebook = NOTEBOOKS / name
    cells = {cell["id"]: "".join(cell["source"])
             for cell in json.loads(notebook.read_text(encoding="utf-8"))["cells"]}
    namespace = {key: getattr(deslab, key) for key in dir(deslab) if not key.startswith("_")}
    namespace["draw"] = lambda *models, **options: None
    monkeypatch.chdir(tmp_path)
    for index in indices:
        exec(compile(cells[f"{prefix}-{index:02d}"], str(notebook), "exec"), namespace)
    return namespace


# ---------------------------------------------------------------------------------------
# Small factory without failures: one supervisor and two rearm automata
# ---------------------------------------------------------------------------------------

class LatchedMachine:
    """Machine of section 5.1 of LCS_pequena_factoria_st.

    A rising edge of Cmd starts a cycle of `cycle()` scans, with Cmd held high. At the end Fin
    goes high and stays high until Cmd is low; `rearm()` scans after seeing Cmd low the machine
    drops Fin and is ready again.
    """

    def __init__(self, cycle, rearm):
        self.cycle, self.rearm = cycle, rearm
        self.state, self.count, self.fin = "ready", 0, False

    def before_scan(self, cmd, finish_allowed):
        """Update Fin from the previous outputs; return True when the machine finishes."""
        if self.state == "working":
            assert cmd, "command dropped while the machine works"
            self.count -= 1
            if self.count <= 0:
                if not finish_allowed:
                    self.count = 1  # the notebook assumes one finish per scan
                    return False
                self.state, self.fin = "finished", True
                return True
        elif self.state == "finished" and not cmd:
            self.state, self.count = "rearming", self.rearm()
        elif self.state == "rearming":
            assert not cmd, "command raised while Fin is high"
            self.count -= 1
            if self.count <= 0:
                self.state, self.fin = "ready", False
        return False

    def after_scan(self, cmd, previous):
        """A rising edge of the command starts a cycle; return True on a start."""
        if cmd and not previous:
            assert self.state == "ready", f"start command while the machine is {self.state}"
            self.state, self.count = "working", self.cycle()
            return True
        return False


def factory_scans(plc, machines, scans):
    """Run the PLC with the machines; yield (scan, Fin inputs, abstract events, PLC values)."""
    commands = [False, False]
    for scan in range(1, scans + 1):
        events = []
        for i, machine in enumerate(machines):
            if machine.before_scan(commands[i], not events):
                events.append(f"t{i + 1}")
        fins = [machine.fin for machine in machines]
        plc.scan(Fin_M1=fins[0], Fin_M2=fins[1])
        new = [bool(plc.values["Cmd_M1"]), bool(plc.values["Cmd_M2"])]
        for i, machine in enumerate(machines):
            if machine.after_scan(new[i], commands[i]):
                events.append(f"e{i + 1}")
        commands = new
        yield scan, fins, events, plc.values


def trace_rows(names):
    """Rows of the scan-by-scan table in section 7 of LCS_pequena_factoria_st."""
    machines = [LatchedMachine(lambda: 2, lambda: 1), LatchedMachine(lambda: 3, lambda: 1)]
    state_of = {number: state for state, number in names["numero"].items()}
    rows = []
    for scan, fins, events, values in factory_scans(FactoryST(names["st"]), machines, 14):
        label = ", ".join(f"${event[0]}_{event[1]}$" for event in events) or "—"
        sup = "(" + ", ".join(state_of[values["state"][0]]) + ")"
        rows.append(f"| {scan} | {int(fins[0])} | {int(fins[1])} | {label} | {values['state'][0]} | {sup} | "
                    f"{values['state'][1]} | {values['state'][2]} | {int(values['Cmd_M1'])} | "
                    f"{int(values['Cmd_M2'])} |")
    return rows


@pytest.fixture
def pequena_factoria(tmp_path, monkeypatch):
    return run_cells("LCS_pequena_factoria_st.ipynb", "pf",
                     (4, 6, 7, 9, 14, 18, 20, 22, 26), tmp_path, monkeypatch)


@pytest.mark.parametrize("seed, cycle, rearm", [
    (0, (1, 6), (1, 3)),
    (1, (1, 1), (1, 1)),
    (2, (2, 15), (1, 8)),
    (3, (5, 6), (3, 3)),
    (4, (1, 30), (1, 2)),
])
def test_pequena_factoria_st_follows_the_supervisor(pequena_factoria, seed, cycle, rearm):
    sup, number = pequena_factoria["SUP"], pequena_factoria["numero"]
    rng = random.Random(seed)
    machines = [LatchedMachine(lambda: rng.randint(*cycle), lambda: rng.randint(*rearm)) for _ in range(2)]
    expected = next(iter(sup.X0))
    buffer = 0
    count = dict.fromkeys(("e1", "t1", "e2", "t2"), 0)

    for scan, fins, events, values in factory_scans(FactoryST(pequena_factoria["st"]), machines, 1000):
        for event in events:
            assert event in sup.Gamma(expected), (scan, expected, event)
            expected = sup.delta(expected, event)
            count[event] += 1
            if event == "t1":
                buffer += 1
                assert buffer <= 1, (scan, "M1 finished into a full buffer")
            elif event == "e2":
                assert buffer == 1, (scan, "M2 started with an empty buffer")
                buffer -= 1
        assert values["state"][0] == number[expected], (scan, "ST state", expected)
        # each rearm automaton is in `rearme` (1) exactly while its machine holds Fin high
        assert values["state"][1:3] == [int(fins[0]), int(fins[1])], (scan, "rearm states")

    assert min(count.values()) >= 20, count


def test_pequena_factoria_trace_matches_the_notebook(pequena_factoria):
    cells = {cell["id"]: "".join(cell["source"]) for cell in json.loads(
        (NOTEBOOKS / "LCS_pequena_factoria_st.ipynb").read_text(encoding="utf-8"))["cells"]}
    table = [line for line in cells["pf-27"].splitlines() if re.match(r"\| \d+ \|", line)]
    assert table == trace_rows(pequena_factoria)


def test_pequena_factoria_program(pequena_factoria):
    source = pequena_factoria["st"]
    assert len(source.splitlines()) == 103
    assert "slt0" not in source            # SUP never enables two controllable events at once
    assert "Cmd_M1 := 0;" in source and "Cmd_M2 := 0;" in source


# ---------------------------------------------------------------------------------------
# Small factory with breakdowns: two modular supervisors
# ---------------------------------------------------------------------------------------

class Machine:
    """Machine i of the notebook's contract.

    It starts when ready (Fin and Falla low) and Cmd is high, and reports Ocup=1. At the end
    of the cycle it drops Ocup and either pulses Fin for `pulse` scans or breaks down: Falla
    stays high until the PLC orders the reset (Rep=1), which takes `reset` scans.
    """

    def __init__(self, rng, cycle, reset, pulse, p_fail):
        self.rng, self.cycle, self.reset, self.pulse, self.p_fail = rng, cycle, reset, pulse, p_fail
        self.state, self.count, self.pulse_left = "ready", 0, 0
        self.ocup = self.fin = self.falla = False

    def step(self, cmd, rep, uncontrollable_allowed):
        event = None
        if self.pulse_left:
            self.pulse_left -= 1
            self.fin = self.pulse_left > 0
        if self.state == "ready" and cmd and not self.fin and not self.falla:
            self.state, self.count, self.ocup, event = "working", self.rng.randint(*self.cycle), True, "start"
        elif self.state == "working":
            self.count -= 1
            if self.count <= 0 and not uncontrollable_allowed:
                self.count = 1  # the notebook assumes distinct scans for fins and breakdowns
            elif self.count <= 0:
                self.ocup = False
                if self.rng.random() < self.p_fail:
                    self.state, self.falla, event = "broken", True, "fail"
                else:
                    self.state, self.fin, self.pulse_left, event = "ready", True, self.pulse, "finish"
        elif self.state == "broken" and rep:
            self.state, self.count = "resetting", self.rng.randint(*self.reset)
        elif self.state == "resetting":
            self.count -= 1
            if self.count <= 0:
                self.state, self.falla = "ready", False
        return event


OUTPUTS = ("Cmd_M1", "Cmd_M2", "Rep_M1", "Rep_M2")


@pytest.fixture
def small_factory(tmp_path, monkeypatch):
    names = run_cells("LCS_modular_control_small_factory_openplc.ipynb", "sf",
                      (5, 7, 10, 12, 14), tmp_path, monkeypatch)
    events = {key: names[key] for key in ("e1", "t1", "f1", "r1", "e2", "t2", "f2", "r2")}
    return names["SUP1"], names["SUP2"], events, names["st"]


@pytest.mark.parametrize("seed, cycle, reset, pulse, p_fail", [
    (0, (5, 30), (1, 3), 2, 0.3),
    (1, (5, 8), (1, 2), 1, 0.5),
    (2, (10, 60), (1, 4), 3, 0.1),
    (3, (5, 6), (1, 1), 1, 0.0),
    (4, (6, 9), (1, 4), 1, 0.6),
])
def test_small_factory_st_follows_both_supervisors(small_factory, seed, cycle, reset, pulse, p_fail):
    sup1, sup2, events, source = small_factory
    rng = random.Random(seed)
    plc = FactoryST(source)
    machines = [Machine(rng, cycle, reset, pulse, p_fail) for _ in range(2)]
    supervisors = (sup1, sup2)
    expected = [next(iter(S.X0)) for S in supervisors]
    numbering = [{}, {}]
    outputs = dict.fromkeys(OUTPUTS, False)
    buffer = 0
    m2_waiting_reset = False
    count = dict.fromkeys(("start", "finish", "fail"), 0)

    for scan in range(1000):
        uncontrollable = None
        for i, machine in enumerate(machines, 1):
            event = machine.step(outputs[f"Cmd_M{i}"], outputs[f"Rep_M{i}"], uncontrollable is None)
            if event:
                count[event] += 1
            if event == "start" and i == 2:
                assert buffer > 0, (scan, "M2 started with an empty buffer")
                buffer -= 1
            elif event in ("finish", "fail"):
                uncontrollable = (i, event)
                assert not outputs[f"Cmd_M{i}"], (scan, i, "start command still high at the end of the cycle")
                if event == "finish" and i == 1:
                    buffer += 1
                    assert buffer <= 2, (scan, "buffer overflow")
                if event == "fail" and i == 2:
                    m2_waiting_reset = True

        inputs = {}
        for i, machine in enumerate(machines, 1):
            inputs.update({f"Ocup_M{i}": machine.ocup, f"Fin_M{i}": machine.fin, f"Falla_M{i}": machine.falla})
        plc.random_value = rng.randrange(1 << 15)
        plc.scan(**inputs)
        new = {key: bool(plc.values[key]) for key in OUTPUTS}

        # Abstract events of this scan: the uncontrollable one first, then the new command.
        abstract = []
        if uncontrollable:
            i, event = uncontrollable
            abstract.append(events[("t" if event == "finish" else "f") + str(i)])
        rising = [key for key in OUTPUTS if new[key] and not outputs[key]]
        assert len(rising) <= 1, (scan, "two commands in one scan", rising)
        for key in rising:
            i = int(key[-1])
            if key.startswith("Cmd"):
                assert machines[i - 1].state != "working", (scan, i, "start command while working")
                abstract.append(events[f"e{i}"])
            else:
                assert machines[i - 1].state == "broken", (scan, i, "reset command without a breakdown")
                if i == 1:
                    assert not m2_waiting_reset, (scan, "M1 reset while M2 waits for its reset")
                m2_waiting_reset = m2_waiting_reset and i != 2
                abstract.append(events[f"r{i}"])
        for event in abstract:
            for k, supervisor in enumerate(supervisors):
                assert event in supervisor.Gamma(expected[k]), (scan, k, expected[k], event)
                expected[k] = supervisor.delta(expected[k], event)
        for k in range(2):
            actual = plc.values["state"][k]
            assert numbering[k].setdefault(actual, expected[k]) == expected[k], (scan, k, "ST state")
        assert expected[0][:2] == expected[1][:2], (scan, "supervisors disagree on the plant state")
        outputs = new

    assert count["start"] >= 30 and count["finish"] >= 25
    if p_fail:
        assert count["fail"] >= 5


def test_small_factory_program_has_no_coordinator(small_factory):
    sup1, sup2, _, source = small_factory
    assert deslab.nonconflict(sup1, sup2)
    assert "_C :" not in source
    assert len(source.splitlines()) == 453


# ---------------------------------------------------------------------------------------
# Transfer line: two conflicting supervisors and the coordinator added by the generator
# ---------------------------------------------------------------------------------------

class Station:
    """M1, M2 or TU of the notebook's contract: starts when ready and Cmd is high (Ocup=1);
    at the end drops Ocup and pulses one of its finish inputs for `pulse` scans."""

    def __init__(self, rng, cycle, pulse, finishes, weights):
        self.rng, self.cycle, self.pulse, self.finishes, self.weights = rng, cycle, pulse, finishes, weights
        self.state, self.count, self.ocup = "ready", 0, False
        self.pulses = dict.fromkeys(finishes, 0)

    def step(self, cmd, uncontrollable_allowed):
        event = None
        for name in self.pulses:
            self.pulses[name] = max(0, self.pulses[name] - 1)
        if self.state == "ready" and cmd and not any(self.pulses.values()):
            self.state, self.count, self.ocup, event = "working", self.rng.randint(*self.cycle), True, "start"
        elif self.state == "working":
            self.count -= 1
            if self.count <= 0 and not uncontrollable_allowed:
                self.count = 1  # the notebook assumes distinct scans for finishes
            elif self.count <= 0:
                event = self.rng.choices(self.finishes, self.weights)[0]
                self.state, self.ocup, self.pulses[event] = "ready", False, self.pulse + 1
        return event


@pytest.fixture
def transfer_line(tmp_path, monkeypatch):
    names = run_cells("LCS_modular_control_transfer_line_openplc.ipynb", "tl",
                      (5, 7, 10, 12, 14), tmp_path, monkeypatch)
    events = {key: names[key] for key in ("e1", "t1", "e2", "t2", "e3", "t3", "r")}
    return names["SUP1"], names["SUP2"], names["SUP_MONO"], events, names["st"]


@pytest.mark.parametrize("seed, cycle, pulse, p_reject", [
    (0, (5, 20), 2, 0.3),
    (1, (5, 6), 1, 0.5),
    (2, (8, 40), 3, 0.1),
    (3, (5, 9), 1, 0.0),
    (4, (5, 12), 2, 0.8),
])
def test_transfer_line_st_behaves_like_the_monolithic_supervisor(transfer_line, seed, cycle, pulse, p_reject):
    sup1, sup2, mono, events, source = transfer_line
    rng = random.Random(seed)
    plc = FactoryST(source)
    stations = {"M1": Station(rng, cycle, pulse, ["Fin_M1"], [1]),
                "M2": Station(rng, cycle, pulse, ["Fin_M2"], [1]),
                "TU": Station(rng, cycle, pulse, ["Acepta", "Rechaza"], [1 - p_reject, p_reject])}
    command = {"M1": "Cmd_M1", "M2": "Cmd_M2", "TU": "Cmd_TU"}
    start_event = {"Cmd_M1": events["e1"], "Cmd_M2": events["e2"], "Cmd_TU": events["e3"]}
    finish_event = {"Fin_M1": events["t1"], "Fin_M2": events["t2"],
                    "Acepta": events["t3"], "Rechaza": events["r"]}
    # the coordinator's CASE block is the one that writes the _C flags
    coordinator = int(re.search(r"CASE state\[(\d+)\] OF\s+\d+:\s+\w+_C\[", source)[1])
    supervisors = (sup1, sup2)
    expected = [next(iter(S.X0)) for S in supervisors]
    x_mono = next(iter(mono.X0))
    numbering = [{}, {}]
    coordinator_states = {}
    outputs = dict.fromkeys(command.values(), False)
    b1 = b2 = 0
    count = {"start": 0, "Acepta": 0, "Rechaza": 0}

    for scan in range(1000):
        uncontrollable = None
        for name, station in stations.items():
            event = station.step(outputs[command[name]], uncontrollable is None)
            if event == "start":
                count["start"] += 1
                if name == "M2":
                    assert b1 == 1, (scan, "M2 started with B1 empty")
                    b1 -= 1
                elif name == "TU":
                    assert b2 == 1, (scan, "TU started with B2 empty")
                    b2 -= 1
            elif event:
                uncontrollable = event
                assert not outputs[command[name]], (scan, name, "start command still high at the end")
                if event in ("Fin_M1", "Rechaza"):
                    b1 += 1
                    assert b1 <= 1, (scan, "B1 overflow")
                elif event == "Fin_M2":
                    b2 += 1
                    assert b2 <= 1, (scan, "B2 overflow")
                count[event] = count.get(event, 0) + 1

        plc.random_value = rng.randrange(1 << 15)
        plc.scan(Ocup_M1=stations["M1"].ocup, Ocup_M2=stations["M2"].ocup, Ocup_TU=stations["TU"].ocup,
                 Fin_M1=stations["M1"].pulses["Fin_M1"] > 0, Fin_M2=stations["M2"].pulses["Fin_M2"] > 0,
                 Acepta=stations["TU"].pulses["Acepta"] > 0, Rechaza=stations["TU"].pulses["Rechaza"] > 0)
        new = {key: bool(plc.values[key]) for key in outputs}

        abstract = [finish_event[uncontrollable]] if uncontrollable else []
        rising = [key for key in outputs if new[key] and not outputs[key]]
        assert len(rising) <= 1, (scan, "two commands in one scan", rising)
        for key in rising:
            name = next(n for n, c in command.items() if c == key)
            assert stations[name].state != "working", (scan, name, "start command while working")
            abstract.append(start_event[key])
        for event in abstract:
            assert event in mono.Gamma(x_mono), (scan, "trace leaves the monolithic language", x_mono, event)
            x_mono = mono.delta(x_mono, event)
            for k, supervisor in enumerate(supervisors):
                assert event in supervisor.Gamma(expected[k]), (scan, k, expected[k], event)
                expected[k] = supervisor.delta(expected[k], event)
        for k in range(2):
            actual = plc.values["state"][k]
            assert numbering[k].setdefault(actual, expected[k]) == expected[k], (scan, k, "ST state")
        actual = plc.values["state"][coordinator]
        assert coordinator_states.setdefault(x_mono, actual) == actual, (scan, "coordinator state")
        outputs = new

    assert count["start"] >= 30 and count["Acepta"] >= 3
    if p_reject:
        assert count["Rechaza"] >= 1


def test_transfer_line_program_includes_the_coordinator(transfer_line):
    sup1, sup2, mono, _, source = transfer_line
    assert not deslab.nonconflict(sup1, sup2)
    assert "aux : BOOL := 0;" in source and "INTERN_0_C[1] := 1;" in source
    assert len(source.splitlines()) == 366


# ---------------------------------------------------------------------------------------
# Assembly line: five local supervisors, same program as TCT_Proyect
# ---------------------------------------------------------------------------------------

# SHA-256 of ST_Generated/Assembly_line.st generated with TCT by TCT_Proyect/Assembly_line.py
TCT_ASSEMBLY_LINE_SHA256 = "b2ccd55d83dccfa7e500059f84b5938e015a8dbc4ffaca21bd02a1f73d5f3fbc"


def size(S):
    return len(S), sum(len(S.Gamma(x)) for x in S.X)


@pytest.fixture
def assembly_line(tmp_path, monkeypatch):
    names = run_cells("LCS_assembly_line_openplc.ipynb", "al",
                      (5, 7, 9, 11, 13, 17, 19), tmp_path, monkeypatch)
    names["tmp_path"] = tmp_path
    return names


def test_assembly_line_matches_tct(assembly_line):
    supervisors = assembly_line["supervisores"]
    assert [size(S) for S in supervisors] == [(7, 25), (32, 77), (40, 112), (7, 25), (6, 22)]
    # TCT's sup2, sup3 and sup5 also self-loop the at-place sensor that reached them through a
    # clamp; with that self-loop they have the states and transitions computed by TCT
    extra = [set(), {"lid-at-place-FE"}, {"base-at-place-FE"}, set(), {"base-at-place-FE"}]
    assert [size(deslab.invproj(S, S.Sigma | e)) for S, e in zip(supervisors, extra)] == \
        [(7, 25), (32, 109), (40, 152), (7, 25), (6, 28)]
    source = assembly_line["st"]
    assert (assembly_line["tmp_path"] / "ST_Generated" / "Assembly_line.st").read_text(encoding="utf-8") == source
    assert hashlib.sha256(source.encode("utf-8")).hexdigest() == TCT_ASSEMBLY_LINE_SHA256


# local plants and specifications of the five supervisors, as in section 4 of the notebook
ASSEMBLY_PLANTS = [("Lids_conveyor", "Lid_clamp"), ("Lid_clamp", "Grab", "z_axis", "x_axis"),
                   ("Base_clamp", "Grab", "x_axis"), ("Base_conveyor", "Base_clamp"), ("Base_clamp", "Blade")]
ASSEMBLY_SPECS = [("buffer_lid", "Lid_clamp_REQ", "start"), ("buffer_arm",), ("complete_piece",),
                  ("buffer_base", "Base_clamp_REQ", "start_2"), ("leave",)]


def test_assembly_line_self_loops_are_all_needed(assembly_line):
    """Removing any sensor self-loop of a specification, or a shared sensor from a component,
    changes some supervisor."""
    names = assembly_line
    sensors = set(names["SENSORES"])

    def supervisor(k, models):
        plant = models[ASSEMBLY_PLANTS[k][0]]
        for component in ASSEMBLY_PLANTS[k][1:]:
            plant = plant // models[component]
        spec = plant
        for name in ASSEMBLY_SPECS[k]:
            spec = spec // models[name]
        return deslab.supcontrollable(spec, plant)

    def same(S, R):
        S = deslab.invproj(S, R.Sigma) if S.Sigma != R.Sigma else S
        return deslab.are_langequiv(S, R)

    models = {name: names[name] for k in range(5) for name in ASSEMBLY_PLANTS[k] + ASSEMBLY_SPECS[k]}
    reference = names["supervisores"]
    candidates = []
    for name in {n for k in range(5) for n in ASSEMBLY_SPECS[k]}:
        model = models[name]
        candidates += [(name, model.deletetransition((x, e, x)))
                       for x, y, e in model.Graph.edges(keys=True) if x == y and e in sensors]
    for name in {n for k in range(5) for n in ASSEMBLY_PLANTS[k]}:
        model = models[name]
        shared = {e for x, y, e in model.Graph.edges(keys=True) if x == y and e in sensors}
        candidates += [(name, model.deletevent(e)) for e in shared]
    assert len(candidates) == 43 + 8

    for name, smaller in candidates:
        affected = [k for k in range(5) if name in ASSEMBLY_PLANTS[k] + ASSEMBLY_SPECS[k]]
        changed = {**models, name: smaller}
        assert any(not same(supervisor(k, changed), reference[k]) for k in affected), name
