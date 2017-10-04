#!/usr/bin/env python
import numpy
from pyscf import scf
from pyscf import gto
from pyscf import mcscf

'''
Scan HF molecule singlet state dissociation curve.

CASSCF initial guess are generated by two functions: sort_mo and
project_init_guess.  At beginning, we selected the active space instead of the
default canonical Hartree-Fock HOMO LUMO orbitals because of the orbital
symmetry.  It was done by sort_mo function.  In the following calculation for
each single point on the enregy curve, the CASSCF wavefunction may be sensitive
to the initial guess.  One method to provide the right initial guess is to
project the wavefunction from closed points.  It was done by project_init_guess
function.  Actually project_init_guess function allows transforming any
orbitals to the current system.
'''

ehf = []
emc = []

def run(b, dm, mo):
    mol = gto.Mole()
    mol.verbose = 5
    mol.output = 'out_hf-%2.1f' % b
    mol.atom = [
        ["F", (0., 0., 0.)],
        ["H", (0., 0., b)],]

    mol.basis = {'F': 'cc-pvdz',
                 'H': 'cc-pvdz',}
    mol.build()
    mf = scf.RHF(mol)
    ehf.append(mf.scf(dm))

    mc = mcscf.CASSCF(mf, 6, 6)
    if mo is None:
        # initial guess for b = 0.7
        mo = mcscf.sort_mo(mc, mf.mo_coeff, [3,4,5,6,8,9])
    else:
        mo = mcscf.project_init_guess(mc, mo)
    e1 = mc.mc1step(mo)[0]
    emc.append(e1)
    return mf.make_rdm1(), mc.mo_coeff

dm = mo = None
for b in numpy.arange(0.7, 4.01, 0.1):
    dm, mo = run(b, dm, mo)

for b in reversed(numpy.arange(0.7, 4.01, 0.1)):
    dm, mo = run(b, dm, mo)

x = numpy.arange(0.7, 4.01, .1)
ehf1 = ehf[:len(x)]
ehf2 = ehf[len(x):]
emc1 = emc[:len(x)]
emc2 = emc[len(x):]
ehf2.reverse()
emc2.reverse()
with open('hf-scan.txt', 'w') as fout:
    fout.write('    HF 0.7->4.0    CAS(6,6)      HF 4.0->0.7   CAS(6,6)  \n')
    for i, xi in enumerate(x):
        fout.write('%2.1f  %12.8f  %12.8f  %12.8f  %12.8f\n'
                   % (xi, ehf1[i], emc1[i], ehf2[i], emc2[i]))

import matplotlib.pyplot as plt
plt.plot(x, ehf1, label='HF,0.7->4.0')
plt.plot(x, ehf2, label='HF,4.0->0.7')
plt.plot(x, emc1, label='CAS(6,6),0.7->4.0')
plt.plot(x, emc2, label='CAS(6,6),4.0->0.7')
plt.legend()
plt.show()