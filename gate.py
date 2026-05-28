"""
GATE: BCI Stimulation Safety Module.

Extends CCT-Open to accept neurostimulation parameters as input and
predict addiction encoding risk for BCI stimulation protocols.

GATE maps stimulation parameters to a synthetic receptor activation
profile, then routes through the standard CCT encoding pipeline.
This provides a mechanistic, receptor-level risk estimate for
stimulation protocols targeting reward-relevant brain regions.

Input schema is designed as a protocol-level abstraction above
device-specific formats. The minimal biologically informative
parameter set is compatible with BrainFlow-structured data and
extensible to IEEE P2731 dosimetry parameters.

Usage:
    from cct_open.gate import GATEModel

    gate = GATEModel()
    result = gate.predict({
        "target_region": "nucleus_accumbens",
        "frequency_hz": 130,
        "amplitude_ma": 2.5,
        "pulse_width_us": 90,
        "session_duration_min": 60,
    })
    print(result.encoding_probability)
    print(result.risk_class)

Theoretical basis: https://doi.org/10.5281/zenodo.20427785
"""

from dataclasses import dataclass
from typing import Dict, Optional

from cct_open.transfer import ReceptorAxisTransferModule
from cct_open.encoding import EncodingProbabilityModule
from cct_open.utils import validate_stimulation_params


# Supported target regions and their primary receptor pathway mappings.
# Each region maps to a dict of receptor axes and baseline activation
# coefficients derived from the CCT stimulation model.
REGION_PATHWAY_MAP = {
    "nucleus_accumbens": {"DA": 0.85, "GLU": 0.60, "OPI": 0.40},
    "ventral_tegmental_area": {"DA": 0.90, "GLU": 0.45, "OPI": 0.35},
    "prefrontal_cortex": {"DA": 0.55, "GLU": 0.70, "5HT": 0.45},
    "hippocampus": {"GLU": 0.80, "DA": 0.30, "5HT": 0.35},
    "amygdala": {"OPI": 0.65, "DA": 0.45, "GLU": 0.55},
    "striatum": {"DA": 0.75, "GLU": 0.55, "OPI": 0.30},
    "subthalamic_nucleus": {"GLU": 0.70, "DA": 0.50},
    "globus_pallidus": {"DA": 0.60, "GLU": 0.45, "OPI": 0.40},
}

SUPPORTED_REGIONS = set(REGION_PATHWAY_MAP.keys())


@dataclass
class GATEPrediction:
    """Output container for a GATE model prediction."""

    encoding_probability: float
    risk_class: str
    target_region: str
    axis_activations: Dict[str, float]
    confidence: Optional[float] = None

    def __repr__(self):
        return (
            f"GATEPrediction("
            f"encoding_probability={self.encoding_probability:.4f}, "
            f"risk_class='{self.risk_class}', "
            f"target_region='{self.target_region}')"
        )


class GATEModel:
    """
    BCI stimulation safety predictor using the CCT encoding framework.

    Maps stimulation parameters to neural axis activations via a
    region-specific pathway model, then computes encoding probability
    using the standard CCT Layer 3 module.

    Required input parameters:
        target_region (str)        -- brain target region (see SUPPORTED_REGIONS)
        frequency_hz (float)       -- stimulation frequency in Hz
        amplitude_ma (float)       -- stimulation amplitude in mA
        pulse_width_us (float)     -- pulse width in microseconds
        session_duration_min (float) -- session duration in minutes

    Optional:
        sessions_per_week (int)    -- for cumulative encoding estimation
    """

    LOW_THRESHOLD = 0.35
    HIGH_THRESHOLD = 0.65

    def __init__(self):
        self.transfer_module = ReceptorAxisTransferModule()
        self.encoding_module = EncodingProbabilityModule()

    def predict(self, stimulation_params: Dict) -> GATEPrediction:
        """
        Predict addiction encoding risk for a stimulation protocol.

        Args:
            stimulation_params: Dict with required keys:
                target_region, frequency_hz, amplitude_ma,
                pulse_width_us, session_duration_min.

        Returns:
            GATEPrediction with encoding_probability and risk_class.

        Raises:
            ValueError: if required parameters are missing or
                        target_region is not supported.
        """
        validate_stimulation_params(stimulation_params, SUPPORTED_REGIONS)

        axis_activations = self._params_to_axis_activations(stimulation_params)
        encoding_probability = self.encoding_module.compute_encoding_probability(
            axis_activations
        )
        risk_class = self._classify(encoding_probability)

        return GATEPrediction(
            encoding_probability=encoding_probability,
            risk_class=risk_class,
            target_region=stimulation_params["target_region"],
            axis_activations=axis_activations,
        )

    def _params_to_axis_activations(
        self, params: Dict
    ) -> Dict[str, float]:
        """
        Map stimulation parameters to neural axis activation scores.

        Stimulation intensity is computed as a function of frequency,
        amplitude, and pulse width, then scaled against the region-specific
        pathway map to produce axis activations.
        """
        region = params["target_region"]
        freq = float(params["frequency_hz"])
        amp = float(params["amplitude_ma"])
        pw = float(params["pulse_width_us"])
        duration = float(params["session_duration_min"])

        # Charge per second as a proxy for stimulation intensity.
        # Units: mC/s (millicoulombs per second).
        charge_per_second = (amp * pw * 1e-6) * freq

        # Duration scaling: longer sessions increase cumulative encoding risk.
        duration_factor = min(1.0, duration / 120.0)

        # Combined stimulation intensity index [0, 1].
        intensity = min(1.0, charge_per_second * duration_factor * 2.0)

        pathway_priors = REGION_PATHWAY_MAP[region]
        axis_activations = {
            axis: min(1.0, prior * intensity)
            for axis, prior in pathway_priors.items()
        }

        return axis_activations

    def _classify(self, probability: float) -> str:
        if probability >= self.HIGH_THRESHOLD:
            return "high"
        if probability >= self.LOW_THRESHOLD:
            return "moderate"
        return "low"
