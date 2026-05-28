"""
Layer 1: Receptor Binding Input Module.

Converts raw receptor binding affinity values (Ki or IC50, in nM) into a
normalised occupancy vector using the Hill equation at assumed physiological
neurotransmitter concentrations.

The occupancy vector is the input to the receptor-to-axis transfer function
(Layer 2). Each value represents fractional receptor occupancy [0, 1].

Theoretical basis: https://doi.org/10.5281/zenodo.20427785
"""

import math
from typing import Dict


# Assumed synaptic neurotransmitter concentrations (nM) at baseline.
# Derived from published receptor pharmacology literature.
# These are parameterised priors; sensitivity analysis across binding
# affinity ranges is documented in the validation report.
BASELINE_CONCENTRATIONS = {
    "DAT":    200.0,
    "NET":    150.0,
    "SERT":   100.0,
    "D1":     500.0,
    "D2":     500.0,
    "D3":     200.0,
    "MOR":    50.0,
    "KOR":    50.0,
    "DOR":    50.0,
    "CB1":    100.0,
    "NMDA":   5000.0,
    "5HT2A":  200.0,
    "SIGMAR1": 100.0,
}

HILL_COEFFICIENT = 1.0  # Simplified; extended model supports n != 1


class ReceptorBindingModule:
    """
    Converts binding affinity values to fractional receptor occupancy.

    Occupancy is computed via the Hill equation:
        occupancy = [L]^n / (Ki^n + [L]^n)

    where [L] is the assumed baseline neurotransmitter concentration
    for each receptor and Ki is the provided binding affinity.
    """

    def __init__(
        self,
        baseline_concentrations: Dict[str, float] = None,
        hill_coefficient: float = HILL_COEFFICIENT,
    ):
        self.baseline_concentrations = baseline_concentrations or BASELINE_CONCENTRATIONS
        self.n = hill_coefficient

    def compute_occupancy(self, binding_profile: Dict[str, float]) -> Dict[str, float]:
        """
        Compute fractional receptor occupancy for each receptor in the profile.

        Args:
            binding_profile: Dict of receptor name to Ki/IC50 (nM).

        Returns:
            Dict of receptor name to fractional occupancy [0, 1].
        """
        occupancy = {}
        for receptor, ki in binding_profile.items():
            if receptor not in self.baseline_concentrations:
                continue
            concentration = self.baseline_concentrations[receptor]
            occupancy[receptor] = self._hill(concentration, ki)
        return occupancy

    def _hill(self, concentration: float, ki: float) -> float:
        n = self.n
        conc_n = math.pow(concentration, n)
        ki_n = math.pow(ki, n)
        return conc_n / (ki_n + conc_n)
