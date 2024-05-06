import pygsti
from pygsti.extras import idletomography as idt
from qiskit import *
from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit
import os
from qiskit import IBMQ
from qiskit_ibm_provider import IBMProvider
IBMProvider.save_account(token='d4ac1539cf158ed2438538c021bf4993b0f29c0b9e20aafdf3b3a865d3e8bfa4f5e1e3185b6a923d4f526cf71e34176ff0559c1f1bc02d12043ac382aa448a68',overwrite=True)

# enabling IBM Q account

provider = IBMQ.enable_account(token='d4ac1539cf158ed2438538c021bf4993b0f29c0b9e20aafdf3b3a865d3e8bfa4f5e1e3185b6a923d4f526cf71e34176ff0559c1f1bc02d12043ac382aa448a68')
backend = provider.get_backend('ibmq_quito')


def run_idt_cnot( cnotQubits, _run, totalnQubits):
    """Executes idle tomography experiments on an IBM device.
    args:
        cnotQubits: Qubit pair as a list On which repeated CNOT drive
                    will be applied.
        _run:   Run number as an integer. IDT data is collected for 
                   multiple runs.
        totalnQubits:   Total number of qubits in the quantum computer.
                        For `ibmq_quito` it is 5. 
    """

    # Creating necessary directories to save results
    print("#### Run -- ", _run, " ####")
    run_number = "/run-" + str(_run)
    run_numberr = "/runn-" + str(_run)
    run = "./cnot_" + str(cnotQubits[0]) + str(cnotQubits[1]) + run_number + '/' # uncomment this line for short sequence run
    runn = "./cnot_" + str(cnotQubits[0]) + str(cnotQubits[1]) + run_numberr + '/'
    try:
        os.mkdir( "./cnot_" + str(cnotQubits[0]) + str(cnotQubits[1]) )
    except:
        pass

    try:
        os.mkdir(run)
        os.mkdir(runn)
    except:
        pass

    # preparing IBM compatible quantum circuits list
    nQubits = totalnQubits 
    maxLengths = [1,2,4,8]

    mdl_target = pygsti.construction.build_localnoise_model(nQubits, ["Gx","Gy","Gcnot"])
   
    paulidicts = idt.determine_paulidicts(mdl_target)
    listOfExperiments = idt.make_idle_tomography_list(nQubits, maxLengths, paulidicts)
    print(len(listOfExperiments))
    pygsti.io.write_circuit_list('ckt.txt', listOfExperiments, header=None)
    print(len(listOfExperiments), "Idle Tomography experiments for {} qubits".format(nQubits))

    new = list(range(totalnQubits))
   

    circ = []
    norc=[]

    for kk in range(len(listOfExperiments)):
        c = listOfExperiments[kk].convert_to_openqasm(gatename_conversion=
                                                      {'Gy': 'ry(1.5707963267948966)',
                                                       'Gx': 'rx(1.5707963267948966)',
                                                       'Gcnot': 'cx'})
        f = open('circuit.txt', 'w')
        f.write(c)
        f.close()

        
        with open("circuit.txt", "r") as input:
            with open("temp.txt", "w") as output:
       
              for line in input:
           
                if "q[3]"  not in line.strip("\n"):
                  output.write(line)
           

        os.replace('temp.txt', 'circuit.txt')
        with open("circuit.txt", "r") as input:
            with open("temp.txt", "w") as output:
       
              for line in input:
           
                if "q[4]"  not in line.strip("\n"):
                  output.write(line)
           

        os.replace('temp.txt', 'circuit.txt')
        f = open('circuit.txt', 'r')
        g=f.read()
        norc.append( QuantumCircuit.from_qasm_str(g) )
        f.close()

        f = open('circuit.txt', 'r')
        fnew = open('circuit_cnotdelay_added.txt', 'w')
        fnew.write('OPENQASM 2.0;\n')
        fnew.write('include "qelib1.inc";\n')
     
        fnew.write('opaque delay(time) q;\n')
        
        for line in f:
            if line[0:2] == 'OP' or line[0:2] == 'in' or line[0:2] == 'op' or line[0:2] == 'me':
                pass
            else:
                fnew.write(line)
        for i in range(20):
            fnew.write('cx '+ 'q[' + str(cnotQubits[0]) + '],' + 'q[' + str(cnotQubits[1]) + '];\n' )
            fnew.write('delay(1)'+ 'q[' + str(cnotQubits[0]) + '];\n')
        fnew.write('barrier q[0],q[1],q[2],q[3],q[4];\n')
        
        fnew.write('measure q[0] -> cr[0];\n')
        fnew.write('measure q[1] -> cr[1];\n')
        fnew.write('measure q[2] -> cr[2];\n')
                 
        
        fnew.close()   
        fnew = open('circuit_cnotdelay_added.txt', 'r')
        d = fnew.read()

        circ.append( QuantumCircuit.from_qasm_str(d) )
        f.close()
        fnew.close()

    # Execution on IBMQ machines
    batch_size = 75 # All the Idle Tomography circuits cannot be
                    # executed on IBM machine at the same time.
                    # Therefore, the circuit list is broken into 
                    # `batches` and scheduled on the IBM quantum comp.
                    # Max. number of circuits IBM allows in 75.
    if len(listOfExperiments) % batch_size == 0:
        _range = int( len(listOfExperiments) / batch_size )
    else:
        _range = int( len(listOfExperiments) / batch_size ) + 1

    shots = 8192          

    for kk in range( _range ):
        if kk == _range - 1:
            end = len( listOfExperiments)
            fileWriteRange = int( len( listOfExperiments)%batch_size ) # hardcoded for the time being 372 total circuit - 9 * 40 = 12
        else:
            end = (kk + 1) * batch_size
            fileWriteRange = batch_size

        transpiled_circ = transpile(circ[kk*batch_size:end], backend,scheduling_method='alap')
        job_exp = backend.run(transpiled_circ,shots=shots)
        print("job finished")
        result_exp = job_exp.result()
        print(kk + 1, "batch jobs finished")

        for ii in range( fileWriteRange ):

            file_number = kk * batch_size + ii + 1
           
            fc = open(run + str(file_number) + '.txt', 'w')
            
            counts_exp = result_exp.get_counts(circ[file_number-1])
            fc.write( str(counts_exp) )
            fc.close()

        print(kk + 1, "batch write to file finished of run ", _run)
    for kk in range( _range ):
        if kk == _range - 1:
            end = len( listOfExperiments)
            fileWriteRange = int( len( listOfExperiments)%batch_size ) # hardcoded for the time being 372 total circuit - 9 * 40 = 12
        else:
            end = (kk + 1) * batch_size
            fileWriteRange = batch_size

        transpiled_circ = transpile(norc[kk*batch_size:end], backend,scheduling_method='alap')
        job_exp = backend.run(transpiled_circ,shots=shots)
        
       
        print("job finished")
        result_exp = job_exp.result()
        print(kk + 1, "batch jobs finished")

        for ii in range( fileWriteRange ):

            file_number = kk * batch_size + ii + 1
            
            fc = open(runn + str(file_number) + '.txt', 'w')
            
            counts_exp = result_exp.get_counts(norc[file_number-1])
            fc.write( str(counts_exp) )
            fc.close()

        print(kk + 1, "batch write to file finished of run ", _run)