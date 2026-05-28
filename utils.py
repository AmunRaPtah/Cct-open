"""
Shared validation utilities for CCT-Open.
"""

from typing import Dict, Set


def validate_binding_profile(
    binding_profile: Dict[str, float],
    supported_receptors: Set[str],
) -> None:
    if not binding_profile:
        raise ValueError("binding_profile cannot be empty.")

    recognised = set(binding_profile.keys()) & supported_receptors
    if not recognised:
        raise ValueError(
            f"No supported receptors found in binding_profile. "
            f"Supported receptors: {sorted(supported_receptors)}"
        )

    for receptor, value in binding_profile.items():
        if receptor in supported_receptors:
            if not isinstance(value, (int, float)):
                raise TypeError(
                    f"Binding affinity for {receptor} must be numeric, "
                    f"got {type(value).__name__}."
                )
            if value <= 0:
                raise ValueError(
                    f"Binding affinity for {receptor} must be positive (nM), "
                    f"got {value}."
                )


def validate_stimulation_params(
    params: Dict,
    supported_regions: Set[str],
) -> None:
    required = {
        "target_region",
        "frequency_hz",
        "amplitude_ma",
        "pulse_width_us",
        "session_duration_min",
    }
    missing = required - set(params.keys())
    if missing:
        raise ValueError(
            f"Missing required stimulation parameters: {sorted(missing)}"
        )

    region = params["target_region"]
    if region not in supported_regions:
        raise ValueError(
            f"Unsupported target_region '{region}'. "
            f"Supported regions: {sorted(supported_regions)}"
        )

    numeric_fields = {
        "frequency_hz", "amplitude_ma", "pulse_width_us", "session_duration_min"
    }
    for field in numeric_fields:
        value = params[field]
        if not isinstance(value, (int, float)):
            raise TypeError(
                f"Parameter '{field}' must be numeric, got {type(value).__name__}."
            )
        if value <= 0:
            raise ValueError(f"Parameter '{field}' must be positive, got {value}.")
