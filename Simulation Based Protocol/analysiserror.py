import pygsti
from pygsti.extras import idletomography as idt
import ast
from typing import Tuple, List

def reduce_pauli_op_str(pauli_op: str) -> Tuple[str, List[int]]:
    """Removes Identity operator from a Pauli operator string.
    Returns a new string with non-trivial Pauli terms (i.e., X, Y or Z terms) along with
    the indices of the non-trivial terms in the original string.
    """
    reduced_pauli_str = "".join(ltr for ltr in pauli_op if ltr != "I")
    non_trivial_op_indices = [idx for idx, ltr in enumerate(pauli_op) if ltr != "I"]

    return reduced_pauli_str, non_trivial_op_indices

def analysis(readFile, writeFile, dirName, nQubits,book):
    """This file reads experimental data from IBM.
    Prepares pyGSTi compatible dataset and analyze the dataset to extract error-rates.
    Args:
      readFile: experiment data file name as counts from IBM device
      writeFile: pyGSTi dataset
      dirName: directory of the experimental data
      nQubits: total number of qubits on which IDT was run
      book: text file to write error values
    """

    f = open(readFile, 'r')
    ds = open(writeFile, 'w')

    # preparing pyGSTi compatible dataset for IDT analysis
    w = ['0']*(2**(nQubits) + 1)
    w[0] = "## Columns ="
    for k in range(2**(nQubits)):
        if k == 2**(nQubits)-1:
            w[k+1] = format(k, "0"+str(nQubits)+"b") + " count\n"
        else:
            w[k+1] = format(k, "0"+str(nQubits)+"b") + " count,"
    ds.write(" ".join(w))

    k = 1

    for line in f:
        toWrite = ['0']*(2**nQubits + 1)
        toWrite[0] = line[0:len(line)-1]
        fIbmData = open( dirName + str(k)+'.txt', 'r' )

        for lineIbm in fIbmData:
            _dict = ast.literal_eval(lineIbm)

        # reversing the count string to make it pyGSTi compatible
        for key in _dict:
            keyReverse = key[::-1]
            toWrite[ int(keyReverse, 2) + 1 ] = str( _dict[key] )

        linew = '  '.join(toWrite)
        linew = linew + '\n'

        ds.write(linew)
        if k<252:
           k = k + 1
        
    f.close()
    ds.close()

    f = open(writeFile, 'r')

    ds = pygsti.io.load_dataset(writeFile)
    maxLengths = [1,2,4,8]

    mdl_target = pygsti.construction.build_localnoise_model(nQubits, ["Gx","Gy","Gcnot"])
    paulidicts = idt.determine_paulidicts(mdl_target)

    # IDT results object that contains all error rates
    results = idt.do_idle_tomography(nQubits, ds, maxLengths, paulidicts)
    error_type_to_prefix = {
        "hamiltonian": "H",
        "stochastic": "S",
        "affine": "A"
    }

    all_error_dict = {}
    for error_type in ["hamiltonian", "stochastic", "affine"]:
        error_prefix = error_type_to_prefix[error_type]
        for pauli_op_obj, error_rate in zip(results.error_list, results.intrinsic_rates[error_type]):
            op, qubits = reduce_pauli_op_str(pauli_op=pauli_op_obj.rep)
            if len(qubits) == 1:
                key = f"{error_prefix}{op}:{qubits[0]}"
            elif len(qubits) == 2:
                key = f"{error_prefix}{op}:{qubits[0]},{qubits[1]}"
            else:
                raise ValueError(f"qubits {qubits} must have max 2 items")

            if error_prefix == "S" and error_rate < 0:
                error_rate = 0 # forcing -ve stochastic error rates to 0


            all_error_dict[key] = error_rate
    fnew = open(book, 'w') 
    fnn=open('diffbook.txt','w')
    for key, val in all_error_dict.items():
        fnew.write(f"{val:.4f}\n")
        fnn.write(f"{key}:\n")
        print(f"{key}: {val:.4f}")
    fnew.close()
    OUTPUT=idt.create_idletomography_report(results,'OUTN+A.html')
   
    
    
#analysis('cktn.txt','Out.txt',r'C:/Users/91940/OneDrive/Desktop/Documents/ProjectWPA/run-1/result/count/',5,'book2.txt')
analysis('ckt.txt','VICTIM+ATTACKER.txt',r'C:/Users/91940/OneDrive/Desktop/Documents/ProjectWPA/cnot_34/run-1/',5,'book3.txt')

