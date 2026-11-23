"""Checks for the notebooks in notebooks/factory_io that generate OpenPLC ST.

The notebooks' own cells are executed (without the Colab setup and drawings). The program of
the small factory with one supervisor is simulated scan by scan with machines that follow the
notebook's contract. The programs of the small factory with breakdowns, the transfer line and
the assembly line must equal the ones generated with TCT by TCT_Proyect, and every self-loop
of their models must be needed.
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
# Small factory with breakdowns and transfer line: same programs as TCT_Proyect
# ---------------------------------------------------------------------------------------

# SHA-256 of the programs generated with TCT by TCT_Proyect/Small_factory.py and by
# TCT_Proyect/Transfer_line.py (with its generate_ST_OPENPLC call taken out of the comment).
# TCT visits the requests shared by the transfer line supervisors in Python set order, so it
# writes one of two programs depending on PYTHONHASHSEED; DESlab's is the one of PYTHONHASHSEED=2.
TCT_SMALL_FACTORY_SHA256 = "582689a29b0551e9d76f1f26906075c45b790cdd5defcfc1e97696c72b687b40"
TCT_TRANSFER_LINE_SHA256 = "fd43dd2a774fb4144f180e979153a34896969d0e77fdd498129cc106d6a26fcb"

# supervisor: (plant components, specifications), as in the notebooks
SMALL_FACTORY_MODELS = {"SUP": (["model_M1", "model_M2"], ["REQ_Buffer", "REQ_start", "REQ_repair"]),
                        "sup_BA": (["B_A"], ["start"])}
TRANSFER_LINE_MODELS = {"sup_M1": (["Conveyor_M1"], ["M1_piece"]),
                        "sup_B1": (["Conveyor_buffer", "Clamp", "Blade"], ["event_2", "Buffer_join", "Camp_REQ"]),
                        "sup_B2": (["Conveyor_buffer2"], ["Buffer2_join"]),
                        "sup_TU": (["Conveyor_TU", "ARM_TU"], ["TU_Function"]),
                        "sup_2": (["M1_REQ", "M2_REQ", "TU_REQ"], ["start", "B1SP"]),
                        "sup2_2": (["M2_REQ", "TU_REQ"], ["B2SP"])}


def size(S):
    return len(S), sum(len(S.Gamma(x)) for x in S.X)


def sha256(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def compose(models):
    result = models[0]
    for model in models[1:]:
        result = result // model
    return result


def same_language(S, R):
    if S.empty or R.empty:
        return S.empty == R.empty
    S = deslab.invproj(S, R.Sigma) if S.Sigma != R.Sigma else S
    R = deslab.invproj(R, S.Sigma) if R.Sigma != S.Sigma else R
    return deslab.are_langequiv(S, R)


def rerun(names, cell, **changes):
    """Execute a generation cell again with some models replaced."""
    namespace = {**names, **changes}
    exec(compile(names["cells"][cell], cell, "exec"), namespace)
    return namespace["st"]


def check_self_loops(names, table):
    """Every uncontrollable event of a specification is in its plant; every sensor self-loop of
    a specification changes its supervisor; every event that a component has only as self-loops
    reaches the plant only through it and is used by a specification of that plant."""
    models = {m: names[m] for components, specs in table.values() for m in components + specs}

    def supervisor(name, models):
        components, specs = table[name]
        plant = compose([models[c] for c in components])
        return deslab.supcontrollable(compose([plant] + [models[s] for s in specs]), plant)

    for name, (components, specs) in table.items():
        plant = compose([models[c] for c in components])
        assert same_language(supervisor(name, models), names[name]), name
        for spec in specs:
            assert models[spec].Sigma - models[spec].Sigcon <= plant.Sigma, (name, spec)

    loops = 0
    for spec in {s for _, specs in table.values() for s in specs}:
        E = models[spec]
        affected = [n for n, (_, specs) in table.items() if spec in specs]
        for x, y, e in E.Graph.edges(keys=True):
            if x == y and e not in E.Sigcon:
                loops += 1
                changed = {**models, spec: E.deletetransition((x, e, x))}
                assert any(not same_language(supervisor(n, changed), names[n]) for n in affected), (spec, x, e)

    shared = 0
    for component in {c for components, _ in table.values() for c in components}:
        C = models[component]
        edges = list(C.Graph.edges(keys=True))
        for e in {e for x, y, e in edges if x == y}:
            if any(x != y for x, y, f in edges if f == e):
                continue
            shared += 1
            affected = [n for n, (components, _) in table.items() if component in components]
            reduced = {**models, component: C.deletevent(e)}
            assert any(e not in compose([reduced[c] for c in table[n][0]]).Sigma
                       and any(e in models[s].Sigma for s in table[n][1]) for n in affected), (component, e)
    return loops, shared


@pytest.fixture
def small_factory(tmp_path, monkeypatch):
    names = run_cells("LCS_modular_control_small_factory_openplc.ipynb", "sf",
                      (5, 7, 9, 11, 13, 15, 17), tmp_path, monkeypatch)
    names["cells"] = {cell["id"]: "".join(cell["source"]) for cell in json.loads(
        (NOTEBOOKS / "LCS_modular_control_small_factory_openplc.ipynb").read_text(encoding="utf-8"))["cells"]}
    names["tmp_path"] = tmp_path
    return names


def test_small_factory_matches_tct(small_factory):
    names = small_factory
    assert size(names["SUP"]) == (36, 119) and size(names["sup_BA"]) == (5, 9)
    # REQ_repair's repair events r1, r2 are not plant events: the supervisor never uses them
    assert {e for x in names["SUP"].X for e in names["SUP"].Gamma(x)} == names["SUP"].Sigma - {"r1", "r2"}
    source = names["st"]
    assert (names["tmp_path"] / "ST_Generated" / "Small_factory.st").read_text(encoding="utf-8") == source
    assert sha256(source) == TCT_SMALL_FACTORY_SHA256
    assert source == (NOTEBOOKS / "ST_generated" / "Small_factory.st").read_text(encoding="utf-8")


def test_small_factory_self_loops_are_all_needed(small_factory):
    assert check_self_loops(small_factory, SMALL_FACTORY_MODELS) == (3, 2)


def test_small_factory_self_loops_left_out_do_not_change_the_program(small_factory):
    names = small_factory
    M1 = names["M1"]
    for e in ("M1-ON", "M1-Busy", "M1-END"):        # the self-loops of TCT's M1
        for x in sorted(M1.X):
            if e not in M1.Gamma(x):
                M1 = M1.addselfloop(x, e)
    auxiliary = [M1 if A is names["M1"] else A for A in names["auxiliares"]]
    assert sha256(rerun(names, "sf-17", auxiliares=auxiliary)) == TCT_SMALL_FACTORY_SHA256


@pytest.fixture
def transfer_line(tmp_path, monkeypatch):
    names = run_cells("LCS_modular_control_transfer_line_openplc.ipynb", "tl",
                      (5, 7, 9, 11, 13, 15, 17), tmp_path, monkeypatch)
    names["cells"] = {cell["id"]: "".join(cell["source"]) for cell in json.loads(
        (NOTEBOOKS / "LCS_modular_control_transfer_line_openplc.ipynb").read_text(encoding="utf-8"))["cells"]}
    names["tmp_path"] = tmp_path
    return names


def test_transfer_line_matches_tct(transfer_line):
    names = transfer_line
    assert [size(names[n]) for n in TRANSFER_LINE_MODELS] == \
        [(4, 7), (33, 189), (5, 17), (9, 50), (9, 24), (6, 17)]
    assert not deslab.nonconflict(names["sup_2"], names["sup2_2"])
    source = names["st"]
    assert "aux : BOOL := 0;" in source and "INTERN_1_C[1] := 1;" in source
    assert (names["tmp_path"] / "ST_Generated" / "transfer_line.st").read_text(encoding="utf-8") == source
    assert sha256(source) == TCT_TRANSFER_LINE_SHA256
    assert source == (NOTEBOOKS / "ST_generated" / "transfer_line.st").read_text(encoding="utf-8")
    # BLADE_LIMIT is controllable in Transfer_line.py, so the program writes that input
    assert "GD_IN_4 := 1;" in source


def test_transfer_line_self_loops_are_all_needed(transfer_line):
    assert check_self_loops(transfer_line, TRANSFER_LINE_MODELS) == (84, 16)


def test_transfer_line_self_loops_left_out_do_not_change_the_program(transfer_line):
    names = transfer_line
    TU_Function = names["TU_Function"]
    for x in range(1, 9):                                # TCT's TU_Conveyor_ON self-loops
        TU_Function = TU_Function.addselfloop(x, "TU-Conveyor-ON")
    sup_TU = names["local"](names["P_TU"], TU_Function, "sup_TU")
    assert same_language(sup_TU, names["sup_TU"])
    auxiliary = [sup_TU if A is names["sup_TU"] else A for A in names["auxiliares"]]
    assert sha256(rerun(names, "tl-17", auxiliares=auxiliary)) == TCT_TRANSFER_LINE_SHA256


# ---------------------------------------------------------------------------------------
# Assembly line: five local supervisors, same program as TCT_Proyect
# ---------------------------------------------------------------------------------------

# SHA-256 of ST_Generated/Assembly_line.st generated with TCT by TCT_Proyect/Assembly_line.py
TCT_ASSEMBLY_LINE_SHA256 = "b2ccd55d83dccfa7e500059f84b5938e015a8dbc4ffaca21bd02a1f73d5f3fbc"


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
    assert source == (NOTEBOOKS / "ST_generated" / "Assembly_line.st").read_text(encoding="utf-8")


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


# ---------------------------------------------------------------------------------------
# Small factory with one monolithic supervisor instead of TCT's SUP and sup_BA
# ---------------------------------------------------------------------------------------

# the monolithic notebook gives the start commands M1-ON and M2-ON where TCT used the requests
# e1 and e2, which pairs turn into those commands
REQUESTS = {"e1": "M1-ON", "e2": "M2-ON"}


def as_commands(model):
    """The model with the requests e1, e2 renamed as the commands M1-ON, M2-ON."""
    mapping = {e: c for e, c in REQUESTS.items() if e in model.Sigma}
    return model.renamevents(mapping) if mapping else model


@pytest.fixture
def monolithic_small_factory(tmp_path, monkeypatch):
    names = run_cells("LCS_monolithic_control_small_factory_openplc.ipynb", "sm",
                      (5, 7, 9, 13, 15, 17), tmp_path, monkeypatch)
    names["tmp_path"] = tmp_path
    return names


def notebook_cells(name):
    return {cell["id"]: "".join(cell["source"]) for cell in json.loads(
        (NOTEBOOKS / name).read_text(encoding="utf-8"))["cells"]}


def test_monolithic_small_factory_equals_both_tct_supervisors(monolithic_small_factory, tmp_path, monkeypatch):
    names = monolithic_small_factory
    S = names["SUP"]
    assert size(S) == (141, 613)
    assert deslab.iscontrollable(S, names["G"]) and deslab.coac(S).X == S.X
    # the supervisor gives the start commands itself
    assert {"M1-ON", "M2-ON"} <= S.Sigcon and not set(REQUESTS) & S.Sigma
    # start comes from the push button, not from self-loops in the machines and the feeder
    assert all("start" not in names[m].Sigma for m in ("model_M1", "model_M2", "B_A"))
    assert size(names["pulsador"]) == (1, 1) and names["pulsador"].Sigma == {"start"}
    # without it start is not a plant event and the supervisor never leaves its initial state
    G = names["model_M1"] // names["model_M2"] // names["B_A"]
    E = names["REQ_Buffer"] // names["REQ_start"] // names["REQ_repair"]
    assert size(deslab.supcontrollable(G // E, G)) == (1, 0)
    # same plant and supervisor as the TCT version, where start is a self-loop and REQ_start and
    # start are two specifications of two supervisors
    tct = run_cells("LCS_modular_control_small_factory_openplc.ipynb", "sf", (5, 7, 9, 11),
                    tmp_path, monkeypatch)
    plant = as_commands(tct["model_M1"] // tct["model_M2"] // tct["B_A"])
    assert deslab.are_isomorphic(names["G"], plant) and names["G"].Sigcon == plant.Sigcon
    assert deslab.are_isomorphic(S, as_commands(tct["SUP"] // tct["sup_BA"]))


def test_monolithic_small_factory_program(monolithic_small_factory):
    names = monolithic_small_factory
    source = names["st"]
    assert (names["tmp_path"] / "ST_Generated" / "Small_factory_monolitico.st").read_text(encoding="utf-8") == source
    assert source == (NOTEBOOKS / "ST_generated" / "Small_factory_monolitico.st").read_text(encoding="utf-8")
    assert "_C :" not in source and "state : ARRAY [0..7] OF DINT;" in source
    # SUP writes the start commands; the auxiliary automata M1 and M2 switch them off
    def case(k):
        start = source.index(f"CASE state[{k}] OF")
        return source[start:source.index("CASE state[", start + 1)]

    assert "GD_OUT_0 := 1;" in case(0) and "GD_OUT_1 := 1;" in case(0)
    assert "GD_OUT_0 := 0;" in case(1) and "GD_OUT_1 := 0;" in case(2)
    # without requests there are no internal request variables nor handshake pairs
    assert "INTERN_0" not in source and "INTERN_1" not in source
    assert "IF NOT GD_OUT_0 &" not in source and "IF NOT GD_OUT_1 &" not in source


# ---------------------------------------------------------------------------------------
# Small factory with local modular control: two supervisors equal to the monolithic one
# ---------------------------------------------------------------------------------------

@pytest.fixture
def local_modular_small_factory(tmp_path, monkeypatch):
    names = run_cells("LCS_local_modular_control_small_factory_openplc.ipynb", "lm",
                      (5, 7, 9, 11, 13, 15, 17), tmp_path, monkeypatch)
    names["tmp_path"] = tmp_path
    return names


def test_local_modular_small_factory_equals_the_monolithic_supervisor(local_modular_small_factory,
                                                                     tmp_path, monkeypatch):
    names = local_modular_small_factory
    S1, S2 = names["S1"], names["S2"]
    assert size(S1) == (35, 83) and size(S2) == (37, 169) and size(names["SUP"]) == (141, 613)
    for S, plant in ((S1, names["G1"]), (S2, names["G2"])):
        assert deslab.iscontrollable(S, plant) and deslab.coac(S).X == S.X
    # local plants: the components that share events with the specifications
    assert deslab.are_isomorphic(names["G1"], names["model_M1"] // names["model_M2"])
    assert deslab.are_isomorphic(names["G2"], names["G"])
    assert deslab.nonconflict(S1, S2)
    assert deslab.are_isomorphic(S1 // S2, names["SUP"])
    # the models and signal map of the monolithic notebook, with the requests e1 and e2 in place
    # of the commands M1-ON and M2-ON, which the pairs give; the same auxiliary automata
    mono = run_cells("LCS_monolithic_control_small_factory_openplc.ipynb", "sm", (5, 7, 9, 13, 15),
                     tmp_path, monkeypatch)
    for model in ("model_M1", "model_M2", "B_A", "pulsador", "REQ_Buffer", "REQ_start", "REQ_repair"):
        renamed = as_commands(names[model])
        assert deslab.are_isomorphic(renamed, mono[model]) and renamed.Sigcon == mono[model].Sigcon, model
    assert deslab.are_isomorphic(as_commands(names["SUP"]), mono["SUP"])
    assert notebook_cells("LCS_local_modular_control_small_factory_openplc.ipynb")["lm-13"] == \
        notebook_cells("LCS_monolithic_control_small_factory_openplc.ipynb")["sm-13"]
    assert {e: s for e, s in names["actuators"].items() if e not in REQUESTS} == mono["actuators"]
    assert names["Mask"] == mono["Mask"] and names["parejas"] == [("e2", "M2-ON"), ("e1", "M1-ON")]


def test_local_modular_small_factory_program(local_modular_small_factory):
    names = local_modular_small_factory
    source = names["st"]
    assert (names["tmp_path"] / "ST_Generated" / "Small_factory_modular_local.st").read_text(encoding="utf-8") == source
    assert source == (NOTEBOOKS / "ST_generated" / "Small_factory_modular_local.st").read_text(encoding="utf-8")
    # two supervisors and six auxiliary automata, without coordinator
    assert "_C :" not in source and "state : ARRAY [0..8] OF DINT;" in source
    # the shared requests e1 and e2 change only when both supervisors propose them
    for signal in ("INTERN_0", "INTERN_1"):
        assert f"{signal}_G : ARRAY [0..2] OF BOOL;" in source
        assert (f"\tIF {signal}_G[0] <> {signal}_G[1] THEN\n\t\t\t{signal}_G[0] := {signal};\n"
                f"\t\t\t{signal}_G[1] := {signal};\n") in source
        assert f"{signal}_G[0] := 1;" in source and f"{signal}_G[1] := 1;" in source
