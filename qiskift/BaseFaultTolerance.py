from qiskit.transpiler.basepasses import TransformationPass
from qiskit.transpiler.passes.basis.unroller import Unroller
from qiskit.dagcircuit import DAGCircuit
from qiskit.circuit import QuantumCircuit,QuantumRegister,ClassicalRegister,Qubit
from qiskit.converters import circuit_to_dag, dag_to_circuit
from abc import ABC, abstractmethod

class FaultTolerance(TransformationPass):
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
    def __init__(self, encoderCircuit):
        super().__init__()
        self._encoderCircuit = encoderCircuit.to_gate()

    def getEncoderDag(self,numQubits):
        if type(self._encoderCircuit) == type(None):
            return None

        fullEncoderDag = DAGCircuit()

        registers = []
        for i in range(numQubits):
            registers.append(QuantumRegister(size=self._encoderCircuit.num_qubits,name="q"+str(i)))
            fullEncoderDag.add_qreg(registers[-1])
            fullEncoderDag.apply_operation_back(self._encoderCircuit, registers[-1])

        return fullEncoderDag

    def getEncoderCircuit(self,numQubits):
        if type(self._encoderCircuit) == type(None):
            return None

        registers = []
        for i in range(numQubits):
            registers.append(QuantumRegister(size=self._encoderCircuit.num_qubits,name="q"+str(i)))
        
        fullEncoder = QuantumCircuit(*registers)

        for i in range(numQubits):
            fullEncoder.append(self._encoderCircuit, registers[i])
            fullEncoder.draw()

        return fullEncoder



class SyndromeDetector:
    def __init__(self, detectorCircuit, numMeasurements, numAncillas):
        self._detectorCircuit = detectorCircuit
        self._detectorDag = circuit_to_dag(detectorCircuit)
        self._numMeasurements = numMeasurements
        self._numAncillas = numAncillas

    def syndromeDetectCircuit(self, circuit, qregs, cregs=None, ancillas=None):
        if type(self._detectorCircuit) == type(None):
            return None

        circuit = circuit.copy()

        if cregs == None:
            cregs = []
            for i in range(len(qregs)):
                cregs.append(ClassicalRegister(size = self._numMeasurements, name = "measure"+str(i)))

        if ancillas == None:
            ancillas = []
            for i in range(len(qregs)):
                ancillas.append(QuantumRegister(size = self._numAncillas, name = "ancilla"+str(i)))
        circuit.add_register(*(cregs+ancillas))

        for i in range(len(qregs)):
            circuit = circuit.compose(self._detectorCircuit, [qbit for qbit in qregs[i]]+[ancilla for ancilla in ancillas[i]], cregs[i])
        return circuit

    def syndromeDetectDag(self, dag, qregs, cregs=None, ancillas=None):
        if type(self._detectorDag) == type(None):
            return None

        dag = dag.copy()

        if cregs == None:
            cregs = []
            for i in range(len(qregs)):
                cregs.append(ClassicalRegister(size = self._numMeasurements, name = "measure"+str(i)))
                dag.add_creg(cregs[-1])

        if ancillas == None:
            ancillas = []
            for i in range(len(qregs)):
                ancillas.append(QuantumRegister(size = self._numAncillas, name = "ancilla"+str(i)))
                dag.add_qreg(ancillas[-1])

        for i in range(len(qregs)):
            dag.compose(self._detectorDag, [qbit for qbit in qregs[i]]+[ancilla for ancilla in ancillas[i]], cregs[i])
        return dag
            
            

class BaseFaultTolerantGates(TransformationPass):
    #self._gates = None
    #self._conversions = None

    def run(dag):
        if self._gates == None or self._conversions == None:
            return None
        

class BaseFaultTolerantMeasurement(TransformationPass):
    pass