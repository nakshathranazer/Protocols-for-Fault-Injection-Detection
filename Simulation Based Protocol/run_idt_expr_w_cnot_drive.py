from idt_experiments_w_cnot_drives import run_idt_cnot

r = [1]
cnots = [[3,4]] # allowed cnot on ibmq_quito
totalnQubits = 5

for run in r:
    for cnotQubits in cnots:
        run_idt_cnot(cnotQubits, run, totalnQubits)
