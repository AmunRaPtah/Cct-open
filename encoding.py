"""
Layer 3: CCT Encoding Probability Module.

Computes the reward memory encoding probability from neural axis activation
scores using the CCT consolidation model.

The encoding probability represents the likelihood that a drug experience
or stimulation event will consolidate into a durable motivational memory,
as modelled by the molecular consolidation window formalism in CCT.

The output is a continuous score in [0, 1]. Risk classification thresholds
are applied in core.py, not here, to preserve the continuous output for
downstream use cases (e.g. dose-response curves, sensitivity analysis).

Theoretical basis: https://doi.org/10.5281/zenodo.20427785
"""

import math
from typing import Dict


# Axis weights for the encoding probability computation.
# Derived from the CCT consolidation model formalised in the preprint.
# DA axis is the primary driver; others modulate via interaction terms.
ENCODING_WEIGHTS = {
    "DA":  0.45,
    "OPI": 0.25,
    "GLU": 0.20,
    "5HT": 0.10,
}

# Interaction coefficient: DA x OPI synergy term.
# Models the potentiation of dopaminergic consolidation by co-activation
# of opioidergic pathways, documented in the CCT preprint.
DA_OPI_INTERACTION = 0.15


class EncodingProbabilityModule:
    """
    Computes encoding probability from neural axis activations.

    The encoding probability E is computed as:
        E = sigmoid(w_DA*DA + w_OPI*OPI + w_GLU*GLU + w_5HT*5HT
                    + alpha * DA * OPI)

    where sigmoid maps the weighted sum to [0, 1] and alpha is the
    DA-OPI interaction coefficient.

    The sigmoid is parameterised with a shift term to centre the
    decision boundary at 0.5 for a balanced prior (no bias toward
    high or low risk in the absence of receptor data).
    """

    def __init__(
        self,
        weights: Dict[str, float] = None,
        da_opi_interaction: float = DA_OPI_INTERACTION,
    ):
        self.weights = weights or ENCODING_WEIGHTS
        self.alpha = da_opi_interaction

    def compute_encoding_probability(
        self, axis_activations: Dict[str, float]
    ) -> float:
        """
        Compute encoding probability from axis activation scores.

        Args:
            axis_activations: Dict of axis name to activation score [0, 1].

        Returns:
            Encoding probability as float in [0, 1].
        """
        da  = axis_activations.get("DA",  0.0)
        opi = axis_activations.get("OPI", 0.0)
        glu = axis_activations.get("GLU", 0.0)
        sht = axis_activations.get("5HT", 0.0)

        linear = (
            self.weights.get("DA",  0.45) * da
            + self.weights.get("OPI", 0.25) * opi
            + self.weights.get("GLU", 0.20) * glu
            + self.weights.get("5HT", 0.10) * sht
            + self.alpha * da * opi
        )

        return self._sigmoid(linear)

    @staticmethod
    def _sigmoid(x: float, shift: float = 0.5) -> float:
        """Sigmoid function centred at shift."""
        return 1.0 / (1.0 + math.exp(-(x - shift) * 6.0))
