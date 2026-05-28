"""
Layer 2: Receptor-to-Neural-Axis Transfer Module.

Maps receptor occupancy vectors to neural circuit axis activation scores
across four primary axes implicated in reward memory consolidation:
    - Dopaminergic (DA)
    - Opioidergic (OPI)
    - Serotonergic (5HT)
    - Glutamatergic (GLU)

Each axis activation score is a weighted sum of the occupancy values for
receptors that modulate that axis, normalised to [0, 1].

Weights are derived from published receptor pharmacology meta-analyses.
The parameterised weight matrix allows sensitivity analysis and can be
updated as new literature evidence accumulates.

Theoretical basis: https://doi.org/10.5281/zenodo.20427785
"""

from typing import Dict


# Weight matrix: receptor contributions to each neural axis.
# Values represent the relative contribution of each receptor's occupancy
# to axis activation. Rows are axes; columns are receptors.
# Derived from published meta-analyses of receptor-circuit relationships.
AXIS_WEIGHT_MATRIX = {
    "DA": {
        "DAT":  0.40,
        "D1":   0.25,
        "D2":   0.20,
        "D3":   0.10,
        "SIGMAR1": 0.05,
    },
    "OPI": {
        "MOR":  0.50,
        "KOR":  0.25,
        "DOR":  0.20,
        "SIGMAR1": 0.05,
    },
    "5HT": {
        "SERT":  0.55,
        "5HT2A": 0.35,
        "NET":   0.10,
    },
    "GLU": {
        "NMDA": 0.70,
        "D1":   0.15,
        "CB1":  0.15,
    },
}


class ReceptorAxisTransferModule:
    """
    Computes neural axis activation scores from receptor occupancy vectors.

    Each axis activation is a weighted sum of relevant receptor occupancies,
    normalised by the sum of weights for receptors present in the input profile
    (partial profiles are handled gracefully: weights are renormalised).
    """

    def __init__(self, weight_matrix: Dict[str, Dict[str, float]] = None):
        self.weight_matrix = weight_matrix or AXIS_WEIGHT_MATRIX

    def compute_axis_activations(
        self, occupancy_vector: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Compute activation scores for each neural axis.

        Args:
            occupancy_vector: Dict of receptor name to fractional occupancy [0, 1].

        Returns:
            Dict of axis name to activation score [0, 1].
        """
        activations = {}
        for axis, weights in self.weight_matrix.items():
            total_weight = 0.0
            weighted_sum = 0.0
            for receptor, weight in weights.items():
                if receptor in occupancy_vector:
                    weighted_sum += weight * occupancy_vector[receptor]
                    total_weight += weight
            if total_weight > 0:
                activations[axis] = weighted_sum / total_weight
            else:
                activations[axis] = 0.0
        return activations
