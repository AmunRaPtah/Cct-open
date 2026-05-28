"""
CCT Core Model.

Orchestrates the three-layer CCT pipeline:
    Layer 1 (receptor.py)  -- receptor binding input module
    Layer 2 (transfer.py)  -- receptor-to-neural-axis transfer function
    Layer 3 (encoding.py)  -- encoding probability computation

Usage:
    from cct_open import CCTModel

    model = CCTModel()
    result = model.predict({
        "DAT": 45.2,
        "NET": 180.0,
        "SERT": 920.0,
        "D2": 310.0,
        "MOR": 1200.0,
    })
    print(result.encoding_probability)
    print(result.risk_class)

Theoretical basis: https://doi.org/10.5281/zenodo.20427785
"""

from dataclasses import dataclass
from typing import Dict, Optional

from cct_open.receptor import ReceptorBindingModule
from cct_open.transfer import ReceptorAxisTransferModule
from cct_open.encoding import EncodingProbabilityModule
from cct_open.utils import validate_binding_profile


@dataclass
class CCTPrediction:
    """Output container for a CCT model prediction."""

    encoding_probability: float
    risk_class: str
    axis_activations: Dict[str, float]
    occupancy_vector: Dict[str, float]
    confidence: Optional[float] = None

    def __repr__(self):
        return (
            f"CCTPrediction("
            f"encoding_probability={self.encoding_probability:.4f}, "
            f"risk_class='{self.risk_class}', "
            f"confidence={self.confidence})"
        )


class CCTModel:
    """
    Three-layer CCT pipeline for addiction liability prediction.

    Accepts a receptor binding affinity profile (Ki or IC50 values in nM)
    and returns an encoding probability score with risk classification.

    Risk classes:
        'low'      -- encoding_probability < 0.35
        'moderate' -- 0.35 <= encoding_probability < 0.65
        'high'     -- encoding_probability >= 0.65

    Threshold values are calibrated against a reference set of compounds
    with established DEA Schedule classifications. See validation report
    for sensitivity, specificity, and confidence interval data.
    """

    # Supported receptors. Extend in future versions.
    SUPPORTED_RECEPTORS = {
        "DAT",   # Dopamine transporter
        "NET",   # Norepinephrine transporter
        "SERT",  # Serotonin transporter
        "D1",    # Dopamine D1 receptor
        "D2",    # Dopamine D2 receptor
        "D3",    # Dopamine D3 receptor
        "MOR",   # Mu opioid receptor
        "KOR",   # Kappa opioid receptor
        "DOR",   # Delta opioid receptor
        "CB1",   # Cannabinoid CB1 receptor
        "NMDA",  # NMDA receptor (glutamate)
        "5HT2A", # Serotonin 2A receptor
        "SIGMAR1", # Sigma-1 receptor
    }

    LOW_THRESHOLD = 0.35
    HIGH_THRESHOLD = 0.65

    def __init__(self):
        self.receptor_module = ReceptorBindingModule()
        self.transfer_module = ReceptorAxisTransferModule()
        self.encoding_module = EncodingProbabilityModule()

    def predict(self, binding_profile: Dict[str, float]) -> CCTPrediction:
        """
        Run the full CCT pipeline on a receptor binding profile.

        Args:
            binding_profile: Dict mapping receptor names to binding affinity
                             values in nM (Ki or IC50). At least one receptor
                             from SUPPORTED_RECEPTORS required.

        Returns:
            CCTPrediction with encoding_probability, risk_class,
            axis_activations, and occupancy_vector.

        Raises:
            ValueError: if binding_profile is empty or contains no
                        supported receptor keys.
        """
        validate_binding_profile(binding_profile, self.SUPPORTED_RECEPTORS)

        occupancy_vector = self.receptor_module.compute_occupancy(binding_profile)
        axis_activations = self.transfer_module.compute_axis_activations(occupancy_vector)
        encoding_probability = self.encoding_module.compute_encoding_probability(axis_activations)

        risk_class = self._classify(encoding_probability)

        return CCTPrediction(
            encoding_probability=encoding_probability,
            risk_class=risk_class,
            axis_activations=axis_activations,
            occupancy_vector=occupancy_vector,
        )

    def _classify(self, probability: float) -> str:
        if probability >= self.HIGH_THRESHOLD:
            return "high"
        if probability >= self.LOW_THRESHOLD:
            return "moderate"
        return "low"
