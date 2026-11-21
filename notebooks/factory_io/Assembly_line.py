import STSupervisorTCT as stst

actuators = dict([])
actuators['lids_conveyor_on'] = 'GD_OUT_2:ON:%QX100.2'
actuators['lids_conveyor_off'] = 'GD_OUT_2:OFF'
actuators['bases_conveyor_on'] = 'GD_OUT_3:ON:%QX100.3'
actuators['bases_conveyor_off'] = 'GD_OUT_3:OFF'
actuators['Lid_clamp_on'] = 'GD_OUT_4:ON:%QX100.4'
actuators['Lid_clamp_off'] = 'GD_OUT_4:OFF'
actuators['Base_clamp_on'] = 'GD_OUT_5:ON:%QX100.5'
actuators['Base_clamp_off'] = 'GD_OUT_5:OFF'
actuators['z_axis_on'] = 'GD_OUT_6:ON:%QX100.6'
actuators['z_axis_off'] = 'GD_OUT_6:OFF'
actuators['grab_on'] = 'GD_OUT_7:ON:%QX100.7'
actuators['grab_off'] = 'GD_OUT_7:OFF'
actuators['x_axis_on'] = 'GD_OUT_8:ON:%QX101.0'
actuators['x_axis_off'] = 'GD_OUT_8:OFF'
actuators['blade_on'] = 'GD_OUT_9:ON:%QX101.1'
actuators['blade_off'] = 'GD_OUT_9:OFF'

actuators['start_on'] = 'GD_IN_15:ON:%IX100.15'  # %IX100.15 %IX102.7'

actuators['lid_at_place_FE'] = 'FE_LaP:GD_IN_2:%IX100.2'
actuators['lid_clampled'] = "GD_IN_4:ON:%IX100.4"
actuators['base_at_place_FE'] = 'FE_BaP:GD_IN_3:%IX100.3'
actuators['part_leaving_FE'] = 'FE_PaL:GD_IN_9:%IX101.1'
actuators['base_clampled'] = "GD_IN_5:ON:%IX100.5"
actuators['z_movement_finish'] = 'FE_Zag:GD_IN_6:%IX100.6'
actuators['x_movement_finish'] = 'FE_Xag:GD_IN_7:%IX100.7'
actuators['blade_pos_limit_on'] = 'GD_IN_8:ON:%IX101.0'

actuators['gen_base'] = 'GD_IN_10:ON:%IX102.5'
actuators['gen_lid'] = 'GD_IN_11:ON:%IX102.6'

Mask = dict([])
Mask['GD_IN_10'] = [('GD_OUT_12', '%QX101.2')]
Mask['GD_IN_11'] = [('GD_OUT_13', '%QX101.3')]

new_process = stst.process('Assembly_line')

Lids_conveyor = new_process.new_automaton('lids_conveyor')
new_process.add_state(Lids_conveyor, 2, ['lids_on', 'lids_off'], marked=[True, True])
new_process.add_transition(Lids_conveyor, [(0, 1), (1, 0)], ['lids_conveyor_on', 'lids_conveyor_off'],
                           uncontrollable=[])

start_lid_conveyor = new_process.new_automaton('start')
new_process.add_state(start_lid_conveyor, 2, ["waiting", 'start'], [False, True])
new_process.add_transition(start_lid_conveyor, [(0, 1), (1, 1)], ['start_on', 'lids_conveyor_on'],
                           ['start_on'])
new_process.add_self_event(Lids_conveyor, 'start_on')

Lid_clamp = new_process.new_automaton('Lid_clamp')
new_process.add_state(Lid_clamp, 2, names=["Lid_clamp_off", "Lid_clamp_on"], marked=[True, True])
new_process.add_transition(Lid_clamp, [(0, 1), (1, 0)], ["Lid_clamp_on", "Lid_clamp_off"], uncontrollable=[])

Lid_clamp_REQ = new_process.new_automaton('Lid_clamp_REQ')
new_process.add_state(Lid_clamp_REQ, 3, names=["on", "waiting", "off"], marked=[True, False, False])
new_process.add_transition(Lid_clamp_REQ, [(0, 1), (1, 2), (2, 0)],
                           ["Lid_clamp_on", "lid_clampled", "Lid_clamp_off"],
                           uncontrollable=['lid_clampled'])
new_process.add_self_event(Lid_clamp, 'lid_clampled')

buffer_lid = new_process.new_automaton('buffer_lid')
new_process.add_state(buffer_lid, 5,
                      ["On", "waiting", "Lid_arrived", "Stop_conveyor", "Turn_on_clamp"], [True])
new_process.add_transition(buffer_lid, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)],
                           ['lids_conveyor_on', 'lid_at_place_FE', "lids_conveyor_off", 'Lid_clamp_on',
                            'Lid_clamp_off'], ['lid_at_place_FE'])

new_process.add_self_event(Lid_clamp, 'lid_at_place_FE')
new_process.add_self_event(Lids_conveyor, 'lid_at_place_FE')

Grab = new_process.new_automaton('grab')
new_process.add_state(Grab, 2, names=["grab_off", "grab_on"], marked=[True, True])
new_process.add_transition(Grab, [(0, 1), (1, 0)], ["grab_on", "grab_off"], uncontrollable=[])

z_axis = new_process.new_automaton('z_axis')
new_process.add_state(z_axis, 4, names=["Retracted", '1', "Extended", '0'], marked=[True, True, True, True])
new_process.add_transition(z_axis, [(0, 1), (1, 2), (2, 3), (3, 0)],
                           ["z_axis_on", 'z_movement_finish', "z_axis_off", 'z_movement_finish'],
                           uncontrollable=['z_movement_finish'])

x_axis = new_process.new_automaton('x_axis')
new_process.add_state(x_axis, 4, names=["Retracted", '1', "Extended", '0'], marked=[True, True, True, True])
new_process.add_transition(x_axis, [(0, 1), (1, 2), (2, 3), (3, 0)],
                           ["x_axis_on", 'x_movement_finish', "x_axis_off", 'x_movement_finish'],
                           uncontrollable=['x_movement_finish'])

arm_behaviour = new_process.new_automaton('buffer_arm')
new_process.add_state(arm_behaviour, 16, list(range(0, 16)), [True, False, False, False, False, False, False])
new_process.add_transition(arm_behaviour, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8), (8, 9),
                                           (9, 10), (10, 11), (11, 12), (12, 13), (13, 14), (14, 15), (15, 0)],
                           ['lid_clampled', 'z_axis_on', 'z_movement_finish', 'grab_on', 'Lid_clamp_off', 'z_axis_off',
                            'z_movement_finish', 'x_axis_on', 'x_movement_finish', 'z_axis_on', 'z_movement_finish',
                            'grab_off', 'z_axis_off', 'z_movement_finish', 'x_axis_off', 'x_movement_finish'],
                           ['lid_clampled', 'z_movement_finish', 'x_movement_finish'])

Base_conveyor = new_process.new_automaton('Base_conveyor')
new_process.add_state(Base_conveyor, 2, ['lids_on', 'lids_off'], marked=[True, True])
new_process.add_transition(Base_conveyor, [(0, 1), (1, 0)], ['bases_conveyor_on', 'bases_conveyor_off'],
                           uncontrollable=[])

Base_clamp = new_process.new_automaton('Base_clamp')
new_process.add_state(Base_clamp, 2, names=["Base_clamp_off", "Base_clamp_on"], marked=[True, True])
new_process.add_transition(Base_clamp, [(0, 1), (1, 0)], ["Base_clamp_on", "Base_clamp_off"], uncontrollable=[])

Base_clamp_REQ = new_process.new_automaton('Base_clamp_REQ')
new_process.add_state(Base_clamp_REQ, 3, names=["On", "waiting", "Off"], marked=[True, False, False])
new_process.add_transition(Base_clamp_REQ, [(0, 1), (1, 2), (2, 0)],
                           ["Base_clamp_on", "base_clampled", "Base_clamp_off"], uncontrollable=['base_clampled'])
new_process.add_self_event(Base_clamp, 'base_clampled')

start_base_conveyor = new_process.new_automaton('start_2')
new_process.add_state(start_base_conveyor, 2, ["waiting", 'start'], [False, True])
new_process.add_transition(start_base_conveyor, [(0, 1), (1, 1)], ['start_on', 'bases_conveyor_on'], ['start_on'])
new_process.add_self_event(Base_conveyor, 'start_on')

buffer_base = new_process.new_automaton('buffer_base')
new_process.add_state(buffer_base, 5,
                      ["On", "waiting", " Lid_arrived", "Stop_conveyor", "Turn_on_clamp"], [True])
new_process.add_transition(buffer_base, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)],
                           ['bases_conveyor_on', 'base_at_place_FE', "bases_conveyor_off", 'Base_clamp_on',
                            'Base_clamp_off'], ['base_at_place_FE'])

new_process.add_self_event(Base_clamp, 'base_at_place_FE')
new_process.add_self_event(Base_conveyor, 'base_at_place_FE')

Blade = new_process.new_automaton('blade')
new_process.add_state(Blade, 2, names=["knife_off", "knife_on"], marked=[True, True])
new_process.add_transition(Blade, [(0, 1), (1, 0)], ["blade_on", "blade_off"], uncontrollable=[])

complete_piece = new_process.new_automaton('complete_piece')
new_process.add_state(complete_piece, 5, [], marked=[True, False, False, False])
new_process.add_transition(complete_piece, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)],
                           ['Base_clamp_on', 'base_clampled', 'x_axis_on', 'grab_off', 'Base_clamp_off'],
                           ['base_clampled'])

leave = new_process.new_automaton('leave')
new_process.add_state(leave, 6, [], marked=[True, False, False, False])
new_process.add_transition(leave, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0)],
                           ['Base_clamp_on', 'Base_clamp_off', 'blade_on', 'blade_pos_limit_on', 'part_leaving_FE',
                            'blade_off', 'blade_pos_limit_on'], ['blade_pos_limit_on', 'part_leaving_FE'])
new_process.add_self_event(Blade, 'blade_pos_limit_on')
new_process.add_self_event(Blade, 'part_leaving_FE')

new_process.complete_spec(start_lid_conveyor)
new_process.complete_spec(buffer_lid)
new_process.complete_spec(Lid_clamp_REQ)

new_process.complete_spec(start_base_conveyor)
new_process.complete_spec(buffer_base)
new_process.complete_spec(Base_clamp_REQ)

new_process.complete_spec(arm_behaviour)
new_process.complete_spec(complete_piece)
new_process.complete_spec(leave)

new_process.generate_all_automata()

plant1 = new_process.automata_syncronize([Lids_conveyor, Lid_clamp], name_sync='Plant_M1')
all = new_process.all_events(plant1, 'ALL')
spec = new_process.automata_syncronize([buffer_lid, Lid_clamp_REQ, start_lid_conveyor, all], name_sync='SPEC')
sup1 = new_process.supcon(plant1, spec, 'SUP')
supdat = new_process.condat(plant1, sup1, 'SUPDAT')
simsup = new_process.supreduce(plant1, sup1, supdat, 'SIMSUP')

# new_ststprocess.plot_automatas([Lids_conveyor, Clamp, buffer_lid, Clamp_REQ, start, ALL, sup_M1, Plant_M1], 1, False)


plant2 = new_process.automata_syncronize([Lid_clamp, Grab, z_axis, x_axis], name_sync='plant2')
all2 = new_process.all_events(plant2, 'all2')
spec2 = new_process.automata_syncronize([arm_behaviour, all2], name_sync='spec2')
sup2 = new_process.supcon(plant2, spec2, 'sup2')
supdat2 = new_process.condat(plant2, sup2, 'supdat2')
simsup2 = new_process.supreduce(plant2, sup2, supdat2, 'simsup2')

# new_ststprocess.plot_automatas([Clamp, Grab, z_axis, x_axis, spec2, plant2, sup2], 1, True)

plant3 = new_process.automata_syncronize([Base_clamp, Grab, x_axis], name_sync='plant3')
all3 = new_process.all_events(plant3, 'all3')
spec3 = new_process.automata_syncronize([complete_piece, all3], name_sync='spec3')
sup3 = new_process.supcon(plant3, spec3, 'sup3')
supdat3 = new_process.condat(plant3, sup3, 'supdat3')
simsup3 = new_process.supreduce(plant3, sup3, supdat3, 'simsup3')

# new_ststprocess.plot_automatas([Base_clamp, Grab, x_axis, spec3, sup3, ALL, plant3], 1, False)

plant4 = new_process.automata_syncronize([Base_conveyor, Base_clamp], name_sync='plant4')
all4 = new_process.all_events(plant4, 'all4')
spec4 = new_process.automata_syncronize([buffer_base, Base_clamp_REQ, start_base_conveyor, all4], name_sync='spec4')
sup4 = new_process.supcon(plant4, spec4, 'sup4')
supdat4 = new_process.condat(plant4, sup4, 'supdat4')
simsup4 = new_process.supreduce(plant4, sup4, supdat4, 'simsup4')

# new_ststprocess.plot_automatas([Base_conveyor, Base_clamp, spec4, sup4, plant4, all4], 1, False)

plant5 = new_process.automata_syncronize([Base_clamp, Blade], name_sync='plant5')
all5 = new_process.all_events(plant5, 'all5')
spec5 = new_process.automata_syncronize([leave, all5], name_sync='spec5')
sup5 = new_process.supcon(plant5, spec5, 'sup5')
supdat5 = new_process.condat(plant5, sup5, 'supdat5')
simsup5 = new_process.supreduce(plant5, sup5, supdat5, 'simsup5')

#new_process.plot_automatas([Grab, Blade, spec5, sup5, plant5, all5], 1, False)

new_process.load_automata([sup1, sup2, sup3, sup4, sup5])
new_process.load_automata([simsup, simsup2, simsup3, simsup4, simsup5])
new_process.load_automata([plant1, plant2, plant3, plant4, plant5])

new_process.plot_automatas([sup1, sup2, sup3, sup4, sup5, Lids_conveyor, start_lid_conveyor], show=False)

print(new_process.get_automaton('SUP'))
print(new_process.get_automaton('sup2'))
print(new_process.get_automaton('sup3'))
print(new_process.get_automaton('sup4'))
print(new_process.get_automaton('sup5'),"\n")

print(new_process.get_automaton(plant1))
print(new_process.get_automaton(plant2))
print(new_process.get_automaton(plant3))
print(new_process.get_automaton(plant4))
print(new_process.get_automaton(plant5))

new_process.generate_ST_OPENPLC(supervisors=[sup1, sup2, sup3, sup4, sup5],
                                plants=[plant1, plant2, plant3, plant4, plant5],
                                actuators=actuators, namest='Assembly_line', Mask=Mask)
