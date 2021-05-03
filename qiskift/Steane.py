from BaseFaultTolerance import Encoder,SyndromeDetector
from qiskit.circuit import QuantumCircuit,QuantumRegister,ClassicalRegister,Qubit
from qiskit.converters import circuit_to_dag, dag_to_circuit

class SteaneEncoder(Encoder):
    def __init__(self):
        qregister = QuantumRegister(size = 7)
        encoderCircuit = QuantumCircuit(qregister,name = "Steane Encoder")

        encoderCircuit.h(qregister[1:4])

        encoderCircuit.cx(qregister[1],qregister[0])
        encoderCircuit.cx(qregister[3],qregister[5])
        encoderCircuit.cx(qregister[2],qregister[6])
        encoderCircuit.cx(qregister[1],qregister[4])
        encoderCircuit.cx(qregister[2],qregister[0])
        encoderCircuit.cx(qregister[3],qregister[6])
        encoderCircuit.cx(qregister[1],qregister[5])
        encoderCircuit.cx(qregister[6],qregister[4])

        super().__init__(encoderCircuit)


class SteaneSyndromeDetector(SyndromeDetector):
    def __init__(self):
        qreg = QuantumRegister(size = 7)
        ancilla = QuantumRegister(size = 6)
        creg = ClassicalRegister(size = 6)

        detectorCircuit = QuantumCircuit(qreg,ancilla,name = "Steane Syndrome Detection")

        detectorCircuit.h(ancilla)

        detectorCircuit.cx(ancilla[0],qreg[0])
        detectorCircuit.cx(ancilla[0],qreg[4])
        detectorCircuit.cx(ancilla[0],qreg[5])
        detectorCircuit.cx(ancilla[0],qreg[6])

        detectorCircuit.cx(ancilla[1],qreg[1])
        detectorCircuit.cx(ancilla[1],qreg[3])
        detectorCircuit.cx(ancilla[1],qreg[5])
        detectorCircuit.cx(ancilla[1],qreg[6])

        detectorCircuit.cx(ancilla[2],qreg[2])
        detectorCircuit.cx(ancilla[2],qreg[3])
        detectorCircuit.cx(ancilla[2],qreg[4])
        detectorCircuit.cx(ancilla[2],qreg[5])



        detectorCircuit.cz(ancilla[3],qreg[0])
        detectorCircuit.cz(ancilla[3],qreg[4])
        detectorCircuit.cz(ancilla[3],qreg[5])
        detectorCircuit.cz(ancilla[3],qreg[6])

        detectorCircuit.cz(ancilla[4],qreg[1])
        detectorCircuit.cz(ancilla[4],qreg[3])
        detectorCircuit.cz(ancilla[4],qreg[5])
        detectorCircuit.cz(ancilla[4],qreg[6])

        detectorCircuit.cz(ancilla[5],qreg[2])
        detectorCircuit.cz(ancilla[5],qreg[3])
        detectorCircuit.cz(ancilla[5],qreg[4])
        detectorCircuit.cz(ancilla[5],qreg[5])

        detectorCircuit.h(ancilla)
        
        measureCircuit = QuantumCircuit(qreg,ancilla,creg)
        measureCircuit.append(detectorCircuit.to_gate(),[qbit for qbit in qreg]+[a for a in ancilla])
        measureCircuit.measure(ancilla,creg)

        super().__init__(measureCircuit, 6, 6)



