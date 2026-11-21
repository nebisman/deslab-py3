"""Public OpenPLC code generation and scan protocol checks."""

import pytest

from deslab import fsa, generate_ST_OPENPLC
from deslab.codegen import generate_ST_OPENPLC as module_generate
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
                                Isolated=[[reset], []], output_dir=tmp_path)
    assert source.index("Motor := 1;") < source.index("Motor := 0;")
    assert "state[1] = 0 & RE_Done.Q" in source
    assert "state[1] = 1 & NOT Done" in source
    assert "CASE state[1] OF" in source
    # An OFF self-loop emits its output each scan, without changing state.
    assert "state[1] = 1 & NOT Motor" not in source


def test_startup_preserves_original_held_level_protocol(tmp_path):
    supervisor = fsa([0, 1, 2], ["enable", "start", "done"],
                     [(0, "enable", 1), (1, "start", 2), (2, "done", 1)],
                     [0], [0, 1], Sigcon=["start"])
    mapping = dict(signals(), enable="Enable:ON:%IX0.1")
    source = generate_ST_OPENPLC([supervisor], actuators=mapping,
                                initial="enable", output_dir=tmp_path)
    plc = FactoryST(source)
    plc.scan(Enable=False, Done=False)
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
