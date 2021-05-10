"""
The BaseFaultTolerance module contains base classes for Quantum Error Correction and Quantum Fault Tolerance. 
These classes are generic; they require the user to provide the relevant algorithms when they are initialized.
For specific quantum codes, see the Codes page. Note that only the Steane code is currently implemented.
"""

from qiskit.transpiler.basepasses import TransformationPass
from qiskit.transpiler.passes.basis.unroller import Unroller
from qiskit.dagcircuit import DAGCircuit
from qiskit.circuit import QuantumCircuit,QuantumRegister,ClassicalRegister,AncillaRegister,Qubit,Reset
from qiskit.converters import circuit_to_dag, dag_to_circuit
from abc import ABC, abstractmethod

def _checkNameCircuit(circuit,name):
    for register in circuit.qregs:
        if register.name == name:
            return False
    for register in circuit.cregs:
        if register.name == name:
            return False
    return True

def _checkNameDag(dag,name):
    for register in dag.qregs:
        if dag.qregs[register].name == name:
            return False
    for register in dag.cregs:
        if dag.cregs[register].name == name:
            return False
    return True

def _makeQregsCircuit(circuit, numRegs, numBits, name = "q"):
    qregs = []
    n=0
    for i in range(numRegs):
        while not _checkNameCircuit(circuit,name+str(i+n)):
            n+=1
        qregs.append(QuantumRegister(size=numBits,name=name+str(i+n)))
        circuit.add_register(qregs[-1])
    return qregs

def _makeQregsDag(dag, numRegs, numBits, name = "q"):
    qregs = []
    n=0
    for i in range(numRegs):
        while not _checkNameDag(dag,name+str(i+n)):
            n+=1
        qregs.append(QuantumRegister(size=numBits,name=name+str(i+n)))
        dag.add_qreg(qregs[-1])
    return qregs

def _makeAncillasCircuit(circuit, numRegs, numBits, name = "ancilla"):
    if numBits < 1:
        return [[] for i in range(numRegs)]
    ancillas = []
    n=0
    for i in range(numRegs):
        while not _checkNameCircuit(circuit,name+str(i+n)):
            n+=1
        ancillas.append(AncillaRegister(size=numBits,name=name+str(i+n)))
        circuit.add_register(ancillas[-1])
    return ancillas

def _makeAncillasDag(dag, numRegs, numBits, name = "ancilla"):
    if numBits < 1:
        return [[] for i in range(numRegs)]
    ancillas = []
    n=0
    for i in range(numRegs):
        while not _checkNameDag(dag,name+str(i+n)):
            n+=1
        ancillas.append(AncillaRegister(size=numBits,name=name+str(i+n)))
        dag.add_qreg(ancillas[-1])
    return ancillas

def _makeCregsCircuit(circuit, numRegs, numBits, name = "measure"):
    if numBits < 1:
        return [[] for i in range(numRegs)]
    cregs = []
    n=0
    for i in range(numRegs):
        while not _checkNameCircuit(circuit,name+str(i+n)):
            n+=1
        cregs.append(ClassicalRegister(size=numBits,name=name+str(i+n)))
        circuit.add_register(cregs[-1])
    return cregs

def _makeCregsDag(dag, numRegs, numBits, name = "measure"):
    if numBits < 1:
        return [[] for i in range(numRegs)]
    cregs = []
    n=0
    for i in range(numRegs):
        while not _checkNameDag(dag,name+str(i+n)):
            n+=1
        cregs.append(ClassicalRegister(size=numBits,name=name+str(i+n)))
        dag.add_creg(cregs[-1])
    return cregs

def _combineQregsAncillas(qregs,ancillas,singleQbit=True):
    if singleQbit:
        qbits = []
        for i in range(len(qregs)):
            qbits.append([qbit for qbit in qregs[i]]+[ancilla for ancilla in ancillas[i]])
        return qbits

    qbits = []
    for j in range(len(qregs[0])):
        qbitList = [ancilla for ancilla in ancillas[j]]
        for i in range(len(qregs)):
            qbitList += [qbit for qbit in qregs[i][j]]
        qbits.append(qbitList)
    return qbits


class FaultTolerance(TransformationPass):
    """
    A Transpiler pass that converts a given quantum computation into an equivalent one with error correction. NOT YET IMPLEMENTED
    """
    def __init__(self, encoder, syndromeDetector, gates, measurement):
        super().__init__()
        self._encoder = encoder
        self._syndromeDetector = syndromeDetector
        self._gates = gates
        self._measurement = measurement

    def run(dag):
        if self._encoder == None or self._syndromeDetector == None or self._gates == None or self._measurement == None:
            return None

        dag = Unroller(self._gates.gates).run(dag)


class Encoder():
    """
    A class for implementing the non-fault tolerant ecoding of the Steane :math:`|0\\rangle` state.

    Methods
    -------
    createEncoderCircuit :
        Creates a circuit encoding the :math:`|0\\rangle` state
    createEncoderDag :
        Creates a DAG encoding the :math:`|0\\rangle` state
    getEncoderCircuit :
        Adds gates encoding the :math:`|0\\rangle` state to a circuit
    getEncoderDag :
        Adds gates encoding the :math:`|0\\rangle` state to a DAG
    """
    def __init__(self, encoderCircuit, numAncillas):
        super().__init__()
        self._encoderCircuit = encoderCircuit
        self._encoderDag = circuit_to_dag(encoderCircuit)
        self._numAncillas = numAncillas

    def createEncoderCircuit(self, numQubits):
        """
        Creates a circuit encoding the specified number of qubits to the encoded :math:`|0\\rangle` state.

        Parameters
        ----------
        numQubits : int
            The number of qubits to initialize to the encoded :math:`|0\\rangle` state.
        """
        if type(self._encoderCircuit) == type(None):
            return None

        circuit = QuantumCircuit()

        qregs = _makeQregsCircuit(circuit,numQubits,self._encoderCircuit.num_qubits-self._numAncillas)
        ancillas = _makeAncillasCircuit(circuit, numQubits, self._numAncillas)
        cregs = _makeCregsCircuit(circuit, numQubits, self._encoderCircuit.num_clbits)
        qbits = _combineQregsAncillas(qregs,ancillas)

        for i in range(numQubits):
            circuit = circuit.compose(self._encoderCircuit, qbits[i], cregs[i])

        return circuit

    def createEncoderDag(self, numQubits):
        """
        Creates a DAG encoding the specified number of qubits to the encoded :math:`|0\\rangle` state.

        Parameters
        ----------
        numQubits : int
            The number of qubits to initialize to the encoded :math:`|0\\rangle` state.
        """

        if type(self._encoderCircuit) == type(None):
            return None

        dag = DAGCircuit()

        qregs = _makeQregsDag(dag,numQubits,self._encoderDag.num_qubits()-self._numAncillas)
        ancillas = _makeAncillasDag(dag, numQubits, self._numAncillas)
        cregs = _makeCregsDag(dag, numQubits, self._encoderDag.num_clbits())
        qbits = _combineQregsAncillas(qregs,ancillas)
        
        for i in range(numQubits):
            dag.compose(self._encoderDag, qubits = qbits[i], clbits = cregs[i])

        return dag

    def getEncoderCircuit(self, circuit, qregs, cregs = None, ancillas = None):
        """
        Encodes the specified Quantum Registers to the encoded :math:`|0\\rangle` state for the given circuit.

        Parameters
        ----------
        dag : DAGCircuit
            The circuit for which to create the encoding.
        qregs : list(QuantumRegister)
            The Quantum Registers to encode to the :math:`|0\\rangle`.
        cregs : list(ClassicalRegister), Optional
            The Classical Registers used to encode to the :math:`|0\\rangle`, if classical registers are needed. If ``cregs`` is provided, it must satisfy ``len(cregs) == len(qregs)`` and the encoding process for the ``qregs[i]`` quantum register will use the ``cregs[i]`` classical register.
        ancillas : list(AncillaRegister), list(QuantumRegister), Optional
            The Ancilla Registers used to encode to the :math:`|0\\rangle`, if ancilla registers are needed. If ``ancillas`` is provided, it must satisfy ``len(ancillas) == len(cregs) == len(qregs)`` and the encoding process for the ``qregs[i]`` quantum register will use the ``ancillas[i]`` ancilla register.
        """
        if type(self._encoderCircuit) == type(None):
            return None

        if ancillas == None:
            ancillas = _makeAncillasCircuit(circuit, numQubits, self._numAncillas)

        if cregs == None:
            cregs = _makeCregsCircuit(circuit, numQubits, self._encoderCircuit.num_clbits)
        
        qbits = _combineQregsAncillas(qregs,ancillas)

        for i in range(len(qregs)):
            circuit = circuit.compose(self._encoderCircuit, qbits[i], cregs[i])

        return circuit

    def getEncoderDag(self, dag, qregs, cregs = None, ancillas = None):
        """
        Encodes the specified Quantum Registers to the encoded :math:`|0\\rangle` state for the given DAG.

        Parameters
        ----------
        dag : DAGCircuit
            The circuit for which to create the encoding.
        qregs : list(QuantumRegister)
            The Quantum Registers to encode to the :math:`|0\\rangle`.
        cregs : list(ClassicalRegister), Optional
            The Classical Registers used to encode to the :math:`|0\\rangle`, if classical registers are needed. If ``cregs`` is provided, it must satisfy ``len(cregs) == len(qregs)`` and the encoding process for the ``qregs[i]`` quantum register will use the ``cregs[i]`` classical register.
        ancillas : list(AncillaRegister), list(QuantumRegister), Optional
            The Ancilla Registers used to encode to the :math:`|0\\rangle`, if ancilla registers are needed. If ``ancillas`` is provided, it must satisfy ``len(ancillas) == len(cregs) == len(qregs)`` and the encoding process for the ``qregs[i]`` quantum register will use the ``ancillas[i]`` ancilla register.
        """

        if type(self._encoderCircuit) == type(None):
            return None

        if ancillas == None:
            ancillas = _makeAncillasDag(dag, numQubits, self._numAncillas)
        
        if cregs == None:
            cregs = _makeCregsDag(dag, numQubits, self._encoderDag.num_clbits())
        
        qbits = _combineQregsAncillas(qregs,ancillas)
        
        for i in range(len(qregs)):
            dag.compose(self._encoderDag, qubits = qbits[i], clbits = cregs[i])

        return dag


class FaultTolerantEncoder:
    """
    A class for implementing an fault tolerant ecoding of the :math:`|0\\rangle` state for an arbitrary quantum code.

    Parameters
    ----------
    encoder : Encoder
        An Encoder object representing the :math:`|0\\rangle` state non-fault tolerant encoding process. 
    checkerCircuit : QuantumCircuit
        A circuit for determining whether the :math:`|0\\rangle` state has been encoded properly.
    numAncillas : int
        The number of ancilla qubits used to check the encoded effect. 
        Note: the ancilla qubits must be at the end of the list of qubits for the circuit.
    correctVal : int
        The classical register value corresponding to the correct initialization of the encoded :math:`|0\\rangle` state.
    numRepeats : int
        The number of times to attempt to create the encoded :math:`|0\\rangle` state.

    Methods
    -------
    createEncoderCircuit :
        Creates a circuit encoding the :math:`|0\\rangle` state
    createEncoderDag :
        Creates a DAG encoding the :math:`|0\\rangle` state
    getEncoderCircuit :
        Adds gates encoding the :math:`|0\\rangle` state to a circuit
    getEncoderDag :
        Adds gates encoding the :math:`|0\\rangle` state to a DAG
    """
    def __init__(self, encoder, checkerCircuit, numAncillas, correctVal, numRepeats):
        self._encoder = encoder
        self._checkerCircuit = checkerCircuit
        self._checkerDag = circuit_to_dag(checkerCircuit)
        self._numAncillas = numAncillas
        self._correctVal = correctVal
        self._numRepeats = numRepeats

    def createEncoderCircuit(self, numQubits):
        """
        Creates a circuit fault-tolerantly encoding the specified number of qubits to the encoded :math:`|0\\rangle` state.

        Parameters
        ----------
        numQubits : int
            The number of qubits to initialize to the encoded :math:`|0\\rangle` state.
        """
        circuit = QuantumCircuit()

        qregs = _makeQregsCircuit(circuit,numQubits,self._encoder._encoderCircuit.num_qubits()-self._encoder._numAncillas)
        ancillas1 = _makeAncillasCircuit(circuit, numQubits, self._encoder._numAncillas)
        cregs1 = _makeCregsCircuit(circuit, numQubits, self._encoder._encoderCircuit.num_clbits())
        
        ancillas2 = _makeAncillasCircuit(circuit, numQubits, self._numAncillas)
        cregs2 = _makeCregsCircuit(circuit, numQubits, self._checkerCircuit.num_clbits())

        qbits1 = _combineQregsAncillas(qregs,ancillas1)
        qbits2 = _combineQregsAncillas(qregs,ancillas2)

        circuit = self._encoder.getEncoderCircuit(circuit, qregs, cregs1, ancillas1)
        for i in range(self._numRepeats-1):
            for j in range(len(qregs)):
                circuit = circuit.compose(self._checkerCircuit, qbits2[j], cregs2[j])
                for k in range(2**self._checkerCircuit.num_clbits()):
                    if k != self._correctVal:
                        circuit.reset(qbits1[j]).c_if(cregs2[j],k)
                        circuit = circuit.compose(self._encoder._encoderCircuit.c_if(cregs2[j],k), qbits1[j], cregs1[j])
        
        for j in range(len(qregs)):
            circuit = circuit.compose(self._checkerCircuit, qbits2[j], cregs2[j])

        return circuit

    def createEncoderDag(self, numQubits):
        """
        Creates a DAG fault-tolerantly encoding the specified number of qubits to the encoded :math:`|0\\rangle` state.

        Parameters
        ----------
        numQubits : int
            The number of qubits to initialize to the encoded :math:`|0\\rangle` state.
        """
        dag = DAGCircuit()

        qregs = _makeQregsDag(dag,numQubits,self._encoder._encoderDag.num_qubits()-self._encoder._numAncillas)
        ancillas1 = _makeAncillasDag(dag, numQubits, self._encoder._numAncillas)
        cregs1 = _makeCregsDag(dag, numQubits, self._encoder._encoderDag.num_clbits())

        ancillas2 = _makeAncillasDag(dag, numQubits, self._numAncillas)
        cregs2 = _makeCregsDag(dag, numQubits, self._checkerDag.num_clbits())

        qbits1 = _combineQregsAncillas(qregs,ancillas1)
        qbits2 = _combineQregsAncillas(qregs,ancillas2)

        dag = self._encoder.getEncoderDag(dag, qregs, cregs1, ancillas1)
        for i in range(self._numRepeats-1):
            for j in range(len(qregs)):
                dag.compose(self._checkerDag, qubits = qbits2[j], clbits = cregs2[j])
                for k in range(2**self._checkerDag.num_clbits()):
                    if k != self._correctVal:
                        dag.apply_operation_back(Reset().c_if(cregs2[j],k),qbits1[j])
                        dag.apply_operation_back(self._encoder._encoderCircuit.to_instruction().c_if(cregs2[j],k), qbits1[j], cregs1[j])
        
        for j in range(len(qregs)):
            dag.compose(self._checkerDag, qubits = qbits2[j], clbits = cregs2[j])

        return dag

    def getEncoderCircuit(self, circuit, qregs, cregs1 = None, ancillas1 = None, cregs2 = None, ancillas2 = None):
        """
        Fault-tolerantly encodes the specified Quantum Registers to the encoded :math:`|0\\rangle` state for the given circuit.

        Parameters
        ----------
        dag : DAGCircuit
            The circuit for which to create the encoding.
        qregs : list(QuantumRegister)
            The Quantum Registers to encode to the :math:`|0\\rangle`.
        cregs : list(ClassicalRegister), Optional
            The Classical Registers used to encode to the :math:`|0\\rangle`, if classical registers are needed. If ``cregs`` is provided, it must satisfy ``len(cregs) == len(qregs)`` and the encoding process for the ``qregs[i]`` quantum register will use the ``cregs[i]`` classical register.
        ancillas : list(AncillaRegister), list(QuantumRegister), Optional
            The Ancilla Registers used to encode to the :math:`|0\\rangle`, if ancilla registers are needed. If ``ancillas`` is provided, it must satisfy ``len(ancillas) == len(cregs) == len(qregs)`` and the encoding process for the ``qregs[i]`` quantum register will use the ``ancillas[i]`` ancilla register.
        """
        circuit = QuantumCircuit()

        if ancillas1 == None:
            ancillas1 = _makeAncillasCircuit(circuit, numQubits, self._encoder._numAncillas)
        
        if cregs1 == None:
            cregs1 = _makeCregsCircuit(circuit, numQubits, self._encoder._encoderCircuit.num_clbits())
        
        if ancillas2 == None:
            ancillas2 = _makeAncillasCircuit(circuit, numQubits, self._numAncillas)
        
        if cregs2 == None:
            cregs2 = _makeCregsCircuit(circuit, numQubits, self._checkerCircuit.num_clbits())

        qbits1 = _combineQregsAncillas(qregs,ancillas1)
        qbits2 = _combineQregsAncillas(qregs,ancillas2)

        circuit = self._encoder.getEncoderCircuit(circuit, qregs, cregs1, ancillas1)
        for i in range(self._numRepeats-1):
            for j in range(len(qregs)):
                circuit = circuit.compose(self._checkerCircuit, qbits2[j], cregs2[j])
                for k in range(2**self._checkerCircuit.num_clbits()):
                    if k != self._correctVal:
                        circuit.reset(qbits1[j]).c_if(cregs2[j],k)
                        circuit = circuit.compose(self._encoder._encoderCircuit.c_if(cregs2[j],k), qbits1[j], cregs1[j])
        
        for j in range(len(qregs)):
            circuit = circuit.compose(self._checkerCircuit, qbits2[j], cregs2[j])

        return circuit

    def getEncoderDag(self, dag, qregs, cregs1 = None, ancillas1 = None, cregs2 = None, ancillas2 = None):
        """
        Fault-tolerantly encodes the specified Quantum Registers to the encoded :math:`|0\\rangle` state for the given DAG.

        Parameters
        ----------
        dag : DAGCircuit
            The circuit for which to create the encoding.
        qregs : list(QuantumRegister)
            The Quantum Registers to encode to the :math:`|0\\rangle`.
        cregs : list(ClassicalRegister), Optional
            The Classical Registers used to encode to the :math:`|0\\rangle`, if classical registers are needed. If ``cregs`` is provided, it must satisfy ``len(cregs) == len(qregs)`` and the encoding process for the ``qregs[i]`` quantum register will use the ``cregs[i]`` classical register.
        ancillas : list(AncillaRegister), list(QuantumRegister), Optional
            The Ancilla Registers used to encode to the :math:`|0\\rangle`, if ancilla registers are needed. If ``ancillas`` is provided, it must satisfy ``len(ancillas) == len(cregs) == len(qregs)`` and the encoding process for the ``qregs[i]`` quantum register will use the ``ancillas[i]`` ancilla register.
        """
        if ancillas1 == None:
            ancillas1 = _makeAncillasDag(dag, numQubits, self._encoder._numAncillas)
        
        if cregs1 == None:
            cregs1 = _makeCregsDag(dag, numQubits, self._encoder._encoderDag.num_clbits())
        
        if ancillas2 == None:
            ancillas2 = _makeAncillasDag(dag, numQubits, self._numAncillas)
        
        if cregs2 == None:
            cregs2 = _makeCregsDag(dag, numQubits, self._checkerDag.num_clbits())

        qbits1 = _combineQregsAncillas(qregs,ancillas1)
        qbits2 = _combineQregsAncillas(qregs,ancillas2)

        dag = self._encoder.getEncoderDag(dag, qregs, cregs1, ancillas1)
        for i in range(self._numRepeats-1):
            for j in range(len(qregs)):
                dag.compose(self._checkerDag, qubits = qbits2[j], clbits = cregs2[j])
                for k in range(2**self._checkerDag.num_clbits()):
                    if k != self._correctVal:
                        dag.apply_operation_back(Reset().c_if(cregs2[j],k),qbits1[j])
                        dag.compose(self._encoder._encoderCircuit.to_instruction().c_if(cregs2[j],k), qbits1[j], cregs1[j])
        
        for j in range(len(qregs)):
            dag.compose(self._checkerDag, qubits = qbits2[j], clbits = cregs2[j])

        return dag


class SyndromeDetector:
    """
    A class for implementing non-fault tolerant syndrome detection for an arbitrary error correction scheme.

    Parameters
    ----------
    detectorCircuit : QuantumCircuit
        A Quantum Circuit implementing non-fault tolerant syndrome detection.
    numAncillas : int
        The number of ancilla qubits used in the syndrome detection.

    Methods
    -------
    syndromeDetectCircuit :
        Implements syndrome detection for the given circuit.
    syndromeDetectDag :
        Implements syndrome detection for the given DAG.
    """
    def __init__(self, detectorCircuit, numAncillas):
        self._detectorCircuit = detectorCircuit
        self._detectorDag = circuit_to_dag(detectorCircuit)
        self._numMeasurements = detectorCircuit.num_clbits
        self._numAncillas = numAncillas

    def syndromeDetectCircuit(self, circuit, qregs, cregs=None, ancillas=None):
        """
        Creates gates implementing non-fault tolerant syndrome detection for the given qubits in the given circuit.

        Parameters
        ----------
        circuit : QuantumCircuit
            The circuit for which to perform syndrome detection.
        qregs : list(QuantumRegister)
            The Quantum Registers to on which to perform syndrome detection.
        cregs : list(ClassicalRegister), Optional
            The Classical Registers used to perform syndrome detection, if classical registers are needed. If ``cregs`` is provided, it must satisfy ``len(cregs) == len(qregs)`` and the syndrome detection process for the ``qregs[i]`` quantum register will use the ``cregs[i]`` classical register.
        ancillas : list(AncillaRegister), list(QuantumRegister), Optional
            The Ancilla Registers used to perform syndrome detection,, if ancilla registers are needed. If ``ancillas`` is provided, it must satisfy ``len(ancillas) == len(cregs) == len(qregs)`` and the syndrome detection process for the ``qregs[i]`` quantum register will use the ``ancillas[i]`` ancilla register.
        """
        if type(self._detectorCircuit) == type(None):
            return None

        circuit = circuit.copy()

        if cregs == None:
            cregs = _makeCregsCircuit(circuit,len(qregs),self._numMeasurements)
        
        if ancillas == None:
            ancillas = _makeAncillasCircuit(circuit,len(qregs),self._numAncillas)
        
        qbits = _combineQregsAncillas(qregs,ancillas)

        for i in range(len(qregs)):
            circuit = circuit.compose(self._detectorCircuit, qbits[i], cregs[i])

        for i in range(len(ancillas)):
            circuit.reset(ancillas[i])
        
        return circuit

    def syndromeDetectDag(self, dag, qregs, cregs=None, ancillas=None):
        """
        Creates gates implementing non-fault tolerant syndrome detection for the given qubits in the given DAG.

        Parameters
        ----------
        dag : DAGCircuit
            The DAG for which to perform syndrome detection.
        qregs : list(QuantumRegister)
            The Quantum Registers to on which to perform syndrome detection.
        cregs : list(ClassicalRegister), Optional
            The Classical Registers used to perform syndrome detection, if classical registers are needed. If ``cregs`` is provided, it must satisfy ``len(cregs) == len(qregs)`` and the syndrome detection process for the ``qregs[i]`` quantum register will use the ``cregs[i]`` classical register.
        ancillas : list(AncillaRegister), list(QuantumRegister), Optional
            The Ancilla Registers used to perform syndrome detection,, if ancilla registers are needed. If ``ancillas`` is provided, it must satisfy ``len(ancillas) == len(cregs) == len(qregs)`` and the syndrome detection process for the ``qregs[i]`` quantum register will use the ``ancillas[i]`` ancilla register.
        """

        if type(self._detectorDag) == type(None):
            return None

        #dag = dag.copy()

        if cregs == None:
            cregs = _makeCregsDag(dag,len(qregs),self._numMeasurements)

        if ancillas == None:
            ancillas = _makeAncillasDag(dag,len(qregs),self._numAncillas)

        qbits = _combineQregsAncillas(qregs,ancillas)

        for i in range(len(qregs)):
            dag.compose(self._detectorDag, qubits = qbits[i], clbits = cregs[i])
        
        for i in range(len(ancillas)):
            dag.apply_operation_back(Reset(),ancillas[i])
        
        return dag
            
class SyndromeCorrector:
    """
    A class for implementing fault tolerant syndrome correction for an arbitrary error correction scheme.

    Parameters
    ----------
    correctorCircuit : QuantumCircuit
        A Quantum Circuit implementing fault tolerant syndrome correction for a single qubit.

    Methods
    -------
    syndromeCorrectCircuit :
        Implements syndrome correction for the given circuit.
    syndromeCorrectDag :
        Implements syndrome correction for the given DAG.
    """
    def __init__(self, correctorCircuit):
        self._correctorCircuit = correctorCircuit
        self._correctorDag = circuit_to_dag(correctorCircuit)

    def syndromeCorrectCircuit(self, circuit, qregs, cregs):
        """
        Creates gates implementing fault tolerant syndrome correction for the given qubits in the given circuit.

        Parameters
        ----------
        circuit : QuantumCircuit
            The circuit for which to perform syndrome correction.
        qregs : list(QuantumRegister)
            The Quantum Registers to on which to perform syndrome correction.
        cregs : list(ClassicalRegister)
            The Classical Registers used to perform syndrome correction, if classical registers are needed. If ``cregs`` is provided, it must satisfy ``len(cregs) == len(qregs)`` and the syndrome correction process for the ``qregs[i]`` quantum register will use the ``cregs[i]`` classical register.
        """

        if type(self._correctorCircuit) == type(None):
            return None

        circuit = circuit.copy()

        for i in range(len(qregs)):
            circuit = circuit.compose(self._correctorCircuit, qregs[i], cregs[i])

        return circuit

    def syndromeCorrectDag(self, dag, qregs, cregs):
        """
        Creates gates implementing fault tolerant syndrome correction for the given qubits in the given DAG.

        Parameters
        ----------
        dag : DAGCircuit
            The dag for which to perform syndrome correction.
        qregs : list(QuantumRegister)
            The Quantum Registers to on which to perform syndrome correction.
        cregs : list(ClassicalRegister)
            The Classical Registers used to perform syndrome correction, if classical registers are needed. If ``cregs`` is provided, it must satisfy ``len(cregs) == len(qregs)`` and the syndrome correction process for the ``qregs[i]`` quantum register will use the ``cregs[i]`` classical register.
        """
        if type(self._correctorDag) == type(None):
            return None

        #dag = dag.copy()

        for i in range(len(qregs)):
            dag.compose(self._correctorDag, qubits = qregs[i], clbits = cregs[i])
        return dag

class ErrorCorrector:
    """
    A class for implementing non-fault tolerant error correction (syndrome detection and correction) for an arbitrary error correction scheme.
    This class combines :class:`SyndromeDetection` and :class:`SyndromeCorrection` into a single class for ease of use.

    Parameters
    ----------
    syndromeDetector : SyndromeDetector
        An object representing syndrome detection.
    syndromeCorrector : SyndromeCorrector
        An object representing syndrome correction.

    Methods
    -------
    errorCorrectCircuit :
        Implements error correction for the given circuit.
    errorCorrecDag :
        Implements error correction for the given DAG.
    """
    def __init__(self,syndromeDetector,syndromeCorrector):
        self._syndromeDetector = syndromeDetector
        self._syndromeCorrector = syndromeCorrector
        self._numMeasurements = syndromeDetector._numMeasurements
        self._numAncillas = syndromeDetector._numAncillas

    def errorCorrectCircuit(self, circuit, qregs, cregs=None, ancillas=None):
        """
        Creates gates implementing fault tolerant error correction for the given qubits in the given circuit.

        Parameters
        ----------
        circuit : QuantumCircuit
            The circuit for which to perform error correction.
        qregs : list(QuantumRegister)
            The Quantum Registers to on which to perform error correction.
        cregs : list(ClassicalRegister)
            The Classical Registers used to perform error correction, if classical registers are needed. If ``cregs`` is provided, it must satisfy ``len(cregs) == len(qregs)`` and the syndrome correction process for the ``qregs[i]`` quantum register will use the ``cregs[i]`` classical register.
        """
        if type(self._syndromeDetector) == type(None) or type(self._syndromeCorrector) == type(None):
            return None

        circuit = circuit.copy()

        if cregs == None:
            cregs = _makeCregsCircuit(circuit,len(qregs),self._numMeasurements)
        
        if ancillas == None:
            ancillas = _makeAncillasCircuit(circuit,len(qregs),self._numAncillas)

        circuit = self._syndromeDetector.syndromeDetectCircuit(circuit,qregs,cregs,ancillas)
        circuit = self._syndromeCorrector.syndromeCorrectCircuit(circuit,qregs,cregs)

        return circuit

    def errorCorrectDag(self, dag, qregs, cregs=None, ancillas=None):
        """
        Creates gates implementing non-fault tolerant error correction for the given qubits in the given DAG.

        Parameters
        ----------
        dag : DAGCircuit
            The dag for which to perform error correction.
        qregs : list(QuantumRegister)
            The Quantum Registers to on which to perform error correction.
        cregs : list(ClassicalRegister)
            The Classical Registers used to perform error correction, if classical registers are needed. If ``cregs`` is provided, it must satisfy ``len(cregs) == len(qregs)`` and the syndrome correction process for the ``qregs[i]`` quantum register will use the ``cregs[i]`` classical register.
        """
        if type(self._syndromeDetector) == type(None) or type(self._syndromeCorrector) == type(None):
            return None

        if cregs == None:
            cregs = _makeCregsDag(dag,len(qregs),self._numMeasurements)

        if ancillas == None:
            ancillas = _makeAncillasDag(dag,len(qregs),self._numAncillas)

        dag = self._syndromeDetector.syndromeDetectDag(dag,qregs,cregs,ancillas)
        dag = self._syndromeCorrector.syndromeCorrectDag(dag,qregs,cregs)
        
        return dag

class FaultTolerantGates:
    """
    A class for implementing fault tolerant gates for an arbitrary quantum error correction code.

    Parameters
    ----------
    gatesToCircuit : map(str, (QuantumCircuit, int))
        A map representing conversions between gates and circuits implementing fault tolerant versions of those gates. 
        The keys of the map are the QASM label for the gate in question, given by ``gate.qasm()``.
        The outputs of the map are tuples of the form ``(circuit, numAncillas)``, where ``circuit`` is a fault-tolerant implementation of a gate and ``numAncillas`` is the number of ancillas qubits used in the fault-tolerant implementation of the gate.

    Methods
    -------
    addGateCircuit :
        Adds a fault tolerant gate to the given circuit.
    addGateDag :
        Adds a fault tolerant gate to the given DAG.
    """
    def __init__(self, gatesToCircuit):
        self._gatesToCircuit = gatesToCircuit
        self._gatesToDag = {}

        for gate in gatesToCircuit:
            self._gatesToDag[gate] = (circuit_to_dag(gatesToCircuit[gate][0]),gatesToCircuit[gate][1])

        self._gates = [gate for gate in gatesToCircuit]

    def addGateCircuit(self, circuit, gate, qregs, cregs = None, ancillas = None):
        """
        Adds the specified number of fault tolerant implementations of a quantum gate to the given circuit.

        Parameters
        ----------
        circuit : QuantumCircuit
            The circuit on which to perform the fault tolerant gate.
        gate : Gate
            The non-fault tolerant gate for which to implement a fault tolerant version.
        qregs : list(list(QuantumRegister))
            The Quantum Registers to on which to perform the fault tolerant gate. Each ``qregs[i]`` represents the list of quantum registers which correspond to the ith input to the non-fault tolerant version of the gate in question. Note that each ``qregs[i]`` must have the same length.
        cregs : list(list(ClassicalRegister)), Optional
            The Classical Registers used to perform syndrome detection, if classical registers are needed. If ``cregs`` is provided, it must satisfy ``len(cregs) == len(qregs[0])`` and the syndrome detection process for the ``qregs[i][j]`` quantum register will use the ``cregs[j]`` classical register.
        ancillas : list(list(AncillaRegister)), list(list(QuantumRegister)), Optional
            The Ancilla Registers used to perform syndrome detection,, if ancilla registers are needed. If ``ancillas`` is provided, it must satisfy ``len(ancillas) == len(qregs[0])`` and the syndrome detection process for the ``qregs[i][j]`` quantum register will use the ``ancillas[j]`` ancilla register.
        """
        if self._gates == None or self._gatesToCircuit == None:
            return None

        gate = self._gatesToCircuit[gate.qasm()]
        
        circuit = circuit.copy()

        if cregs == None:
            cregs = _makeCregsCircuit(circuit,len(qregs[0]),gate[0].num_clbits,name="classical")
        
        if ancillas == None:
            ancillas = _makeAncillasCircuit(circuit,len(qregs[0]),gate[1])
        
        qbits = _combineQregsAncillas(qregs,ancillas,singleQbit=False)

        for i in range(len(qbits)):
            if gate[0].num_clbits > 0:
                circuit = circuit.compose(gate[0], qbits[i], cregs[i])
            else:
                circuit = circuit.compose(gate[0], qbits[i])

        return circuit

    def addGateDag(self, dag, gate, qregs, cregs = None, ancillas = None):
        """
        Adds the specified number of fault tolerant implementations of a quantum gate to the given DAG.

        Parameters
        ----------
        dag : DAGCircuit
            The dag on which to perform the fault tolerant gate.
        gate : Gate
            The non-fault tolerant gate for which to implement a fault tolerant version.
        qregs : list(list(QuantumRegister))
            The Quantum Registers to on which to perform the fault tolerant gate. Each ``qregs[i]`` represents the list of quantum registers which correspond to the ith input to the non-fault tolerant version of the gate in question. Note that each ``qregs[i]`` must have the same length.
        cregs : list(list(ClassicalRegister)), Optional
            The Classical Registers used to perform syndrome detection, if classical registers are needed. If ``cregs`` is provided, it must satisfy ``len(cregs) == len(qregs[0])`` and the syndrome detection process for the ``qregs[i][j]`` quantum register will use the ``cregs[j]`` classical register.
        ancillas : list(list(AncillaRegister)), list(list(QuantumRegister)), Optional
            The Ancilla Registers used to perform syndrome detection,, if ancilla registers are needed. If ``ancillas`` is provided, it must satisfy ``len(ancillas) == len(qregs[0])`` and the syndrome detection process for the ``qregs[i][j]`` quantum register will use the ``ancillas[j]`` ancilla register.
        """
        if self._gates == None or self._gatesToDag == None:
            return None
        
        gate = self._gatesToDag[gate.qasm()]

        if cregs == None:
            cregs = _makeCregsDag(dag,len(qregs[0]),gate[0].num_clbits(),name="classical")
        
        if ancillas == None:
            ancillas = _makeAncillasDag(dag,len(qregs[0]),gate[1])
        
        qbits = _combineQregsAncillas(qregs,ancillas,singleQbit=False)

        for i in range(len(qbits)):
            if gate[0].num_clbits() > 0:
                dag.compose(gate[0], qubits = qbits[i], clbits = cregs[i])
            else:
                dag.compose(gate[0], qubits = qbits[i])

        return dag
        

class BaseFaultTolerantMeasurement(TransformationPass):
    """
    A class for implementing fault-tolerant measurement. NOT YET IMPLEMENTED.
    """
    pass