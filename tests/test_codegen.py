"""Public OpenPLC code generation and scan protocol checks."""

import re

import pytest

from deslab import fsa, generate_ST_OPENPLC
from deslab.toolboxes.codegen import generate_ST_OPENPLC as module_generate
from test_factory_st_runtime import FactoryST


def machine():
    return fsa(["idle", "busy"], ["start", "done"],
               [("idle", "start", "busy"), ("busy", "done", "idle")],
               ["idle"], ["idle"], Sigcon=["start"])


def signals():
    return {"start": "Motor:ON:%QX0.0", "done": "RE_Done:Done:%IX0.0"}


def test_public_entry_point_saves_and_returns_program(tmp_path):
    assert module_generate is generate_ST_OPENPLC
    source = generate_ST_OPENPLC([machine()], actuators=signals(),
                                namest="example", output_dir=tmp_path)
    assert (tmp_path / "example.st").read_text(encoding="utf-8") == source
    assert "RE_Done : R_TRIG;" in source
    assert "RE_Done(CLK:= Done);" in source
    assert "state[0] = 1 & RE_Done.Q" in source
    assert "Motor := 1;" in source
    assert "TASK task0(INTERVAL := T#20ms" in source


def emitter_and_box():
    """An emitter that is switched off once a box has gone past a retroreflective sensor (1 while
    nothing cuts its beam): the box has gone past at the rising edge."""
    return fsa([0, 1, 2], ["on", "past", "off"], [(0, "on", 1), (1, "past", 2), (2, "off", 0)],
               [0], [0], Sigcon=["on", "off"])


@pytest.mark.parametrize("polls", [0, 1, 10, 49])
def test_startup_delay_hides_the_first_poll_of_a_sensor_high_at_rest(tmp_path, polls):
    """OpenPLC reads a slave device's input as 0 until its first poll: a sensor that is 1 at rest
    then rises, which without the delay would be a box that never went past."""
    mapping = {"on": "Emitter:ON:%QX0.0", "off": "Emitter:OFF", "past": "RE_Past:Sensor:%IX0.0"}
    source = generate_ST_OPENPLC([emitter_and_box()], actuators=mapping, output_dir=tmp_path)
    assert source.count("startup_delay(IN := TRUE, PT := T#1s);") == 1
    assert source.index("RE_Past(CLK:= Sensor);") < source.index("startup_delay(IN") < source.index("RETURN;")
    plc = FactoryST(source)
    for scan in range(50):  # the input is 0 until the poll, then 1: nothing happens
        plc.scan(Sensor=scan >= polls)
        assert plc.values["state"][0] == 0 and not plc.values["Emitter"]
    plc.scan(Sensor=True)       # first scan of the controller: the emitter switches on and waits
    assert plc.values["state"][0] == 1 and plc.values["Emitter"]
    for _ in range(5):
        plc.scan(Sensor=True)
        assert plc.values["state"][0] == 1 and plc.values["Emitter"]
    plc.scan(Sensor=False)      # a box cuts the beam
    plc.scan(Sensor=True)       # and goes past: rising edge, the emitter switches off
    assert plc.values["state"][0] == 0 and not plc.values["Emitter"]


def test_a_signal_cannot_be_named_like_the_startup_timer(tmp_path):
    mapping = {"start": "startup_delay:ON:%QX0.0", "done": "RE_Done:Done:%IX0.0"}
    with pytest.raises(ValueError, match="startup timer"):
        generate_ST_OPENPLC([machine()], actuators=mapping, output_dir=tmp_path)
    assert not list(tmp_path.iterdir())


def test_plant_controllability_overrides_supervisor_defaults(tmp_path):
    plant = machine()
    supervisor = plant.setpar(Sigcon=plant.Sigma)
    source = generate_ST_OPENPLC([supervisor], plants=[plant],
                                actuators=signals(), output_dir=tmp_path)
    assert "RE_Done.Q" in source
    assert "RE_Done :=" not in source


def test_auxiliary_holds_command_off_until_completion_signal_clears(tmp_path):
    reset = fsa([0, 1], ["done", "off", "clear"],
                [(0, "done", 1), (1, "off", 1), (1, "clear", 0)],
                [0], [0, 1], Sigcon=["off"])
    mapping = dict(signals(), off="Motor:OFF", clear="Done:OFF:%IX0.0")
    source = generate_ST_OPENPLC([machine()], actuators=mapping,
                                Isolated=[reset], output_dir=tmp_path)
    assert source.index("Motor := 1;") < source.index("Motor := 0;")
    assert "state[1] = 0 & RE_Done.Q" in source
    assert "state[1] = 1 & NOT Done" in source
    assert "CASE state[1] OF" in source
    # An OFF self-loop emits its output each scan, without changing state.
    assert "state[1] = 1 & NOT Motor" not in source


def test_event_pairs_turn_a_request_into_a_command(tmp_path):
    request = fsa(["idle", "busy"], ["ask", "done"],
                  [("idle", "ask", "busy"), ("busy", "done", "idle")],
                  ["idle"], ["idle"], Sigcon=["ask"])
    mapping = dict(signals(), ask="INTERN_0:ON")
    source = generate_ST_OPENPLC([request], actuators=mapping, event_pairs=[("ask", "start")],
                                output_dir=tmp_path)
    assert "INTERN_0 := 1;" in source and "state[0] = 0 & INTERN_0" in source
    assert "IF NOT Motor & INTERN_0 THEN\n\t\tMotor := 1;\n" in source
    assert "ELSIF Motor & INTERN_0 THEN\n\t\tINTERN_0 := 0;\n" in source
    without = generate_ST_OPENPLC([request], actuators=mapping, namest="sin", output_dir=tmp_path)
    assert "Motor := 1;" not in without


def test_isolated_lists_only_automata(tmp_path):
    reset = fsa([0], ["off"], [(0, "off", 0)], [0], [0], Sigcon=["off"])
    with pytest.raises(ValueError, match="event_pairs="):
        generate_ST_OPENPLC([machine()], actuators=dict(signals(), off="Motor:OFF"),
                            Isolated=[[reset], []], output_dir=tmp_path)
    with pytest.raises(ValueError, match="pairs"):
        generate_ST_OPENPLC([machine()], actuators=signals(), event_pairs=[("start",)],
                            output_dir=tmp_path)
    assert list(tmp_path.iterdir()) == []


def test_comments_explain_the_program_and_can_be_removed(tmp_path):
    reset = fsa([0, 1], ["done", "off", "clear"],
                [(0, "done", 1), (1, "off", 1), (1, "clear", 0)],
                [0], [0, 1], Sigcon=["off"], name="Rearme")
    mapping = dict(signals(), off="Motor:OFF", clear="Done:OFF:%IX0.0", enable="Enable:ON:%IX0.1")
    arguments = dict(actuators=mapping, Isolated=[reset], initial="enable", output_dir=tmp_path)
    source = generate_ST_OPENPLC([machine().setpar(name="M")], **arguments)
    plain = generate_ST_OPENPLC([machine().setpar(name="M")], namest="plain", comments=False, **arguments)
    assert "(*" not in plain
    # which automaton each state variable is, what each variable holds, the event of each line
    assert "(* state[0]: supervisor M *)" in source
    assert "(* state[1]: auxiliary automaton Rearme *)" in source
    assert "Motor AT %QX0.0 : BOOL; (* output; 1 for start; 0 for off *)" in source
    assert "& RE_Done.Q THEN (* done *)" in source and "Motor := 1; (* start *)" in source
    assert "(* supervisor M (state[0]): orders of each state *)" in source
    # each comment is a whole line or a line end: deleting them gives the program without comments
    assert re.sub(r"(?m)^[ \t]*\(\*.*\*\)\n| \(\*.*?\*\)$", "", source) == plain


def test_startup_preserves_original_held_level_protocol(tmp_path):
    supervisor = fsa([0, 1, 2], ["enable", "start", "done"],
                     [(0, "enable", 1), (1, "start", 2), (2, "done", 1)],
                     [0], [0, 1], Sigcon=["start"])
    mapping = dict(signals(), enable="Enable:ON:%IX0.1")
    source = generate_ST_OPENPLC([supervisor], actuators=mapping,
                                initial="enable", output_dir=tmp_path)
    plc = FactoryST(source)
    # during the startup delay (50 scans of 20 ms) the start signal is not read and nothing moves
    assert plc.startup(Enable=True, Done=False) == 50
    assert not plc.values["initial"] and not plc.values["Motor"]
    plc.scan(Enable=False, Done=False)
    assert plc.started()
    assert plc.values["state"][0] == 0
    assert not plc.values["Motor"]
    plc.scan(Enable=True, Done=False)
    assert plc.values["initial"]
    assert plc.values["state"][0] == 0
    assert not plc.values["Motor"]
    # The original latch enables the controller body on the following scan.
    plc.scan(Enable=True, Done=False)
    assert plc.values["state"][0] == 2
    assert plc.values["Motor"]


@pytest.mark.parametrize("models, mapping, message", [
    ([], {}, "At least one supervisor"),
    ([machine()], {"start": "Motor:ON:%QX0.0"}, "Missing PLC signal"),
    ([machine()], dict(signals(), start="Motor"), "Invalid PLC mapping"),
    ([machine()], dict(signals(), start="RE_Start:Start:%IX0.1"), "Controllable event"),
])
def test_invalid_requests_fail_before_writing(tmp_path, models, mapping, message):
    with pytest.raises(ValueError, match=message):
        generate_ST_OPENPLC(models, actuators=mapping, output_dir=tmp_path)
    assert list(tmp_path.iterdir()) == []


def test_unreachable_supervisor_is_rejected(tmp_path):
    unreachable = fsa([0, 1], ["go"], [(0, "go", 0)], [0], [0, 1], Sigcon=["go"])
    with pytest.raises(ValueError, match="reachable"):
        generate_ST_OPENPLC([unreachable], actuators={"go": "Motor:ON:%QX0.0"},
                            output_dir=tmp_path)


def test_multiple_supervisors_need_one_plant_each(tmp_path):
    with pytest.raises(ValueError, match="one plant per supervisor"):
        generate_ST_OPENPLC([machine(), machine()], actuators=signals(), output_dir=tmp_path)


def branching():
    """From idle, either a job (go, done) or a fault (fail, fixed); fixed is controllable."""
    return fsa(["idle", "busy", "down"], ["go", "done", "fail", "fixed"],
               [("idle", "go", "busy"), ("busy", "done", "idle"),
                ("idle", "fail", "down"), ("down", "fixed", "idle")],
               ["idle"], ["idle"], Sigcon=["go", "fixed"])


def branching_signals():
    return {"go": "Motor:ON:%QX0.0", "done": "RE_Done:Done:%IX0.0",
            "fail": "RE_Fail:Fail:%IX0.1", "fixed": "Reset:ON:%QX0.1"}


def test_state_order_fixes_the_numbering(tmp_path):
    S = branching()
    # breadth-first with this event order: idle 0, down 1, busy 2
    default = generate_ST_OPENPLC([S], actuators=branching_signals(), output_dir=tmp_path,
                                  event_order=["fail", "go"], comments=False)
    assert "state[0] = 0 & RE_Fail.Q THEN\n  \t\tstate[0] := 1;" in default
    listed = generate_ST_OPENPLC([S], actuators=branching_signals(), output_dir=tmp_path,
                                 event_order=["fail", "go"], state_order={S: ["idle", "busy", "down"]},
                                 comments=False)
    assert "state[0] = 0 & RE_Fail.Q THEN\n  \t\tstate[0] := 2;" in listed
    # an automaton as source: its breadth-first order, restricted to the supervisor's states
    source = fsa(["idle", "extra", "busy", "down"], ["go", "skip", "done", "fail", "fixed"],
                 [("idle", "skip", "extra"), ("idle", "go", "busy"), ("busy", "done", "idle"),
                  ("extra", "fail", "down"), ("down", "fixed", "idle")],
                 ["idle"], ["idle"], Sigcon=["go", "fixed"])
    from_source = generate_ST_OPENPLC([S], actuators=branching_signals(), output_dir=tmp_path,
                                      event_order=["skip", "go"], state_order={S: source}, comments=False)
    assert from_source == listed


def test_transition_order_sets_the_branch_order(tmp_path):
    S = branching()
    transitions = [("down", "fixed", "idle"), ("busy", "done", "idle"),
                   ("idle", "fail", "down"), ("idle", "go", "busy")]
    source = generate_ST_OPENPLC([S], actuators=branching_signals(), output_dir=tmp_path,
                                 state_order={S: ["idle", "busy", "down"]},
                                 transition_order={S: transitions})
    assert source.index("state[0] = 1 & RE_Done.Q") < source.index("state[0] = 0 & RE_Fail.Q")
    default = generate_ST_OPENPLC([S], actuators=branching_signals(), output_dir=tmp_path,
                                  state_order={S: ["idle", "busy", "down"]})
    assert default.index("state[0] = 0 & RE_Fail.Q") < default.index("state[0] = 1 & RE_Done.Q")


@pytest.mark.parametrize("option, message", [
    ({"state_order": {"S": ["idle", "busy"]}}, "each of its states once"),
    ({"state_order": {"S": ["busy", "idle", "down"]}}, "start with its initial state"),
    ({"state_order": {"other": ["idle"]}}, "keys must be supervisors"),
    ({"transition_order": {"S": [("idle", "go", "busy")]}}, "each of its transitions once"),
])
def test_invalid_orders_fail_before_writing(tmp_path, option, message):
    S = branching()
    models = {"S": S, "other": machine()}
    option = {name: {models[key]: value for key, value in order.items()} for name, order in option.items()}
    with pytest.raises(ValueError, match=message):
        generate_ST_OPENPLC([S], actuators=branching_signals(), output_dir=tmp_path, **option)
    assert list(tmp_path.iterdir()) == []
