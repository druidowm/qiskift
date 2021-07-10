"""
The Steane Module implements Quantum Error Correction and Quantum Fault Tolerance using the Steane 7-qubit code. 
The 7-qubit code encodes the state :math:`|\\phi\\rangle` as 
$$|\\tilde{\\phi}\\rangle = (1+X_0X_4X_5X_6)(1+X_1X_3X_5X_6)(1+X_2X_3X_4X_6)|\\phi\\rangle.$$
For Syndrome Detection, the Steane code measures 6 operators:
$$M_a = X_0X_4X_5X_6,$$
$$M_b = X_1X_3X_5X_6,$$
$$M_c = X_2X_3X_4X_6,$$
$$N_a = Z_0Z_4Z_5Z_6,$$
$$N_b = Z_1Z_3Z_5Z_6,$$
and
$$N_c = Z_2Z_3Z_4Z_6.$$
More details about each aspect of the Steane code are provided below.
"""

from BaseFaultTolerance import Encoder,FaultTolerantEncoder,SyndromeDetector,SyndromeCorrector,ErrorCorrector,FaultTolerantGates
from qiskit.circuit import QuantumCircuit,QuantumRegister,AncillaRegister,ClassicalRegister,Qubit
from qiskit.converters import circuit_to_dag, dag_to_circuit
from qiskit.circuit.library import CXGate,HGate,XGate,SGate

class SteaneEncoder(Encoder):
    """
    A class for implementing non-fault tolerant preparation of the Steane $|0\\rangle$ state.
    As described at the top of this page, the $|0\\rangle$ state is encoded as 
    $$|\\tilde{0}\\rangle = (1+X_0X_4X_5X_6)(1+X_1X_3X_5X_6)(1+X_2X_3X_4X_6)|0\\rangle.$$
    The circuit representation of the initialization process is:
    
    .. figure:: Images/SteaneEncoding.png

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
    def __init__(self):
        qregister = QuantumRegister(size = 7)
        encoder = QuantumCircuit(qregister,name = "Steane Encoder")

        encoder.h(qregister[:3])

        encoder.cx(qregister[2],qregister[3])
        encoder.cx(qregister[2],qregister[4])
        encoder.cx(qregister[2],qregister[6])
        encoder.cx(qregister[1],qregister[3])
        encoder.cx(qregister[1],qregister[5])
        encoder.cx(qregister[1],qregister[6])
        encoder.cx(qregister[0],qregister[4])
        encoder.cx(qregister[0],qregister[5])
        encoder.cx(qregister[0],qregister[6])

        qregister = QuantumRegister(size = 7)
        encoderCircuit = QuantumCircuit(qregister)
        encoderCircuit.append(encoder.to_gate(),qargs = qregister)

        super().__init__(encoderCircuit, 0)


class SteaneFaultTolerantEncoder(FaultTolerantEncoder):
    """
    A class for implementing fault tolerant ecoding of the Steane encoded $|0\\rangle$ state.
    NOT FINISHED.

    Parameters
    ----------
    numRepeats : int
        The number of times to try to create the $|0\\rangle$ state before giving up.

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
    def __init__(self, numRepeats):
        qreg = QuantumRegister(7)
        areg = AncillaRegister(1)

        c = QuantumCircuit(qreg,areg,name = "Checker")
        c.cx(qreg[3],areg[0])
        c.cx(qreg[4],areg[0])
        c.cx(qreg[5],areg[0])

        qreg = QuantumRegister(7)
        areg = AncillaRegister(1)
        creg = ClassicalRegister(1)
        checker = QuantumCircuit(qreg,areg,creg)
        checker.append(c.to_gate(),qargs=[qbit for qbit in qreg]+[areg[0]])
        checker.measure(areg[0],creg[0])

        super().__init__(SteaneEncoder(),checker,1,[0],numRepeats)


class SteaneSyndromeDetector(SyndromeDetector):
    """
    A class for implementing non-fault tolerant syndrome detection for the Steane Code.
    Syndrome detection works by measuring six stabilizer operators, $M_a,$ $M_b,$ $M_c,$ $N_a,$ $N_b,$ and $N_c,$ defined at the top of this page.
    The circuit representation of the syndrome detection process is:

    .. figure:: Images/SteaneSyndromeDetection.png

    Methods
    -------
    syndromeDetectCircuit :
        Implements syndrome detection for the given circuit.
    syndromeDetectDag :
        Implements syndrome detection for the given DAG.
    """
    def __init__(self):
        qreg = QuantumRegister(size = 7)
        ancilla = QuantumRegister(size = 6)
        creg = ClassicalRegister(size = 6)

        detectorCircuit = QuantumCircuit(qreg,ancilla,name = "Steane Syndrome Detection")

        detectorCircuit.h(ancilla)

        detectorCircuit.cz(ancilla[5],qreg[0])
        detectorCircuit.cz(ancilla[5],qreg[4])
        detectorCircuit.cz(ancilla[5],qreg[5])
        detectorCircuit.cz(ancilla[5],qreg[6])

        detectorCircuit.cz(ancilla[4],qreg[1])
        detectorCircuit.cz(ancilla[4],qreg[3])
        detectorCircuit.cz(ancilla[4],qreg[5])
        detectorCircuit.cz(ancilla[4],qreg[6])

        detectorCircuit.cz(ancilla[3],qreg[2])
        detectorCircuit.cz(ancilla[3],qreg[3])
        detectorCircuit.cz(ancilla[3],qreg[4])
        detectorCircuit.cz(ancilla[3],qreg[6])




        detectorCircuit.cx(ancilla[2],qreg[0])
        detectorCircuit.cx(ancilla[2],qreg[4])
        detectorCircuit.cx(ancilla[2],qreg[5])
        detectorCircuit.cx(ancilla[2],qreg[6])

        detectorCircuit.cx(ancilla[1],qreg[1])
        detectorCircuit.cx(ancilla[1],qreg[3])
        detectorCircuit.cx(ancilla[1],qreg[5])
        detectorCircuit.cx(ancilla[1],qreg[6])

        detectorCircuit.cx(ancilla[0],qreg[2])
        detectorCircuit.cx(ancilla[0],qreg[3])
        detectorCircuit.cx(ancilla[0],qreg[4])
        detectorCircuit.cx(ancilla[0],qreg[6])

        detectorCircuit.h(ancilla)
        
        measureCircuit = QuantumCircuit(qreg,ancilla,creg)
        measureCircuit.append(detectorCircuit.to_gate(),[qbit for qbit in qreg]+[a for a in ancilla])
        measureCircuit.measure(ancilla,creg)

        super().__init__(measureCircuit, 6)

class SteaneSyndromeCorrector(SyndromeCorrector):
    """
    A class for implementing fault tolerant syndrome correction for the Steane code.
    The circuit representation for Syndrome Correction is shown below:

    .. figure:: Images/SteaneSyndromeCorrection.png

    Methods
    -------
    syndromeCorrectCircuit :
        Implements syndrome correction for the given circuit.
    syndromeCorrectDag :
        Implements syndrome correction for the given DAG.
    """
    def __init__(self):
        qreg = QuantumRegister(size = 7)
        creg = ClassicalRegister(size = 6)

        correctorCircuit = QuantumCircuit(qreg,creg,name="Steane Syndrome Correction")

        correctorCircuit.x(qreg[0]).c_if(creg,32)
        correctorCircuit.x(qreg[1]).c_if(creg,16)
        correctorCircuit.x(qreg[2]).c_if(creg,8)
        correctorCircuit.x(qreg[3]).c_if(creg,24)
        correctorCircuit.x(qreg[4]).c_if(creg,40)
        correctorCircuit.x(qreg[5]).c_if(creg,48)
        correctorCircuit.x(qreg[6]).c_if(creg,56)

        correctorCircuit.z(qreg[0]).c_if(creg,4)
        correctorCircuit.z(qreg[1]).c_if(creg,2)
        correctorCircuit.z(qreg[2]).c_if(creg,1)
        correctorCircuit.z(qreg[3]).c_if(creg,3)
        correctorCircuit.z(qreg[4]).c_if(creg,5)
        correctorCircuit.z(qreg[5]).c_if(creg,6)
        correctorCircuit.z(qreg[6]).c_if(creg,7)

        correctorCircuit.z(qreg[0]).c_if(creg,36)
        correctorCircuit.z(qreg[1]).c_if(creg,18)
        correctorCircuit.z(qreg[2]).c_if(creg,9)
        correctorCircuit.z(qreg[3]).c_if(creg,27)
        correctorCircuit.z(qreg[4]).c_if(creg,45)
        correctorCircuit.z(qreg[5]).c_if(creg,54)
        correctorCircuit.z(qreg[6]).c_if(creg,63)
        
        correctorCircuit.x(qreg[0]).c_if(creg,36)
        correctorCircuit.x(qreg[1]).c_if(creg,18)
        correctorCircuit.x(qreg[2]).c_if(creg,9)
        correctorCircuit.x(qreg[3]).c_if(creg,27)
        correctorCircuit.x(qreg[4]).c_if(creg,45)
        correctorCircuit.x(qreg[5]).c_if(creg,54)
        correctorCircuit.x(qreg[6]).c_if(creg,63)

        super().__init__(correctorCircuit)


class SteaneErrorCorrector(ErrorCorrector):
    """
    A class for implementing non-fault tolerant error correction for the Steane Code.
    This class combines :class:`SteaneSyndromeDetection` and :class:`SteaneSyndromeCorrection` into a single class for ease of use.

    Methods
    -------
    errorCorrectCircuit :
        Implements error correction for the given circuit.
    errorCorrecDag :
        Implements error correction for the given DAG.
    """
    def __init__(self):
        super().__init__(SteaneSyndromeDetector(),SteaneSyndromeCorrector())


class SteaneFaultTolerantGates(FaultTolerantGates):
    """
    A class for implementing fault tolerant gates for the Steane Code.
    The current implemented gates are $X,$ $H,$ $S,$ and CNOT. These gates can all be implemented bitwise.
    The figures below show the implementations for these four gates.
    
    .. list-table::

       * - .. figure:: Images/SteaneX.png
              :height: 300

              The fault tolerant X gate.
         - .. figure:: Images/SteaneH.png
              :height: 300

              The fault tolerant H gate.
         - .. figure:: Images/SteaneS.png
              :height: 300

              The fault tolerant S gate.
         - .. figure:: Images/SteaneCNOT.png
              :height: 300

              The fault tolerant CNOT gate.

    Methods
    -------
    addGateCircuit :
        Adds a fault tolerant gate to the given circuit.
    addGateDag :
        Adds a fault tolerant gate to the given DAG.
    """
    def __init__(self):
        cnotGateQ1 = QuantumRegister(7)
        cnotGateQ2 = QuantumRegister(7)
        cnotGate = QuantumCircuit(cnotGateQ1,cnotGateQ2,name = "CNOT")
        cnotGate.cx(cnotGateQ1,cnotGateQ2)

        cnotQ1 = QuantumRegister(7)
        cnotQ2 = QuantumRegister(7)
        cnot = QuantumCircuit(cnotQ1,cnotQ2)
        cnot.append(cnotGate.to_gate(), qargs = [qbit for qbit in cnotQ1]+[qbit for qbit in cnotQ2])


        hGateQ = QuantumRegister(7)
        hGate = QuantumCircuit(hGateQ,name = "H")
        hGate.h(hGateQ)
        hQ = QuantumRegister(7)
        h = QuantumCircuit(hQ)
        h.append(hGate, qargs = hQ)

        xGateQ = QuantumRegister(7)
        xGate = QuantumCircuit(xGateQ,name = "X")
        xGate.x(xGateQ)
        xQ = QuantumRegister(7)
        x = QuantumCircuit(xQ)
        x.append(xGate, qargs = xQ)

        sGateQ = QuantumRegister(7)
        sGate = QuantumCircuit(sGateQ,name = "S")
        sGate.s(sGateQ)
        sGate.z(sGateQ)
        sQ = QuantumRegister(7)
        s = QuantumCircuit(sQ)
        s.append(sGate, qargs = sQ)

        super().__init__({CXGate().qasm(): (cnot,0), HGate().qasm(): (h,0), XGate().qasm(): (x,0), SGate().qasm(): (s,0)})




        