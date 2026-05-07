from datetime import datetime, timedelta
from typing import List

from app.models.material import Material
from app.models.phase import Phase
from utils.exceptions import SchedulingError


def calculate_earliest_start(
    materials: List[Material],
    phases: List[Phase],
    desired_start: datetime,
) -> datetime:
    """
    Return the earliest safe project start date given material lead times.

    Critical-path logic:
      For each material, compute the latest date by which it must be ordered
      so it arrives before its phase begins.  A phase begins after all
      preceding phases have completed (sum of their duration_days).

      If a material's lead time exceeds the time available before its phase
      starts, the project start must be pushed back by the shortfall.

      earliest_start = desired_start + max(shortfall across all materials)
    """
    if not phases:
        raise SchedulingError("At least one phase is required.")
    if not materials:
        raise SchedulingError("At least one material is required.")

    # Pre-compute the day offset at which each phase begins (0-indexed from start).
    phases_sorted = sorted(phases, key=lambda p: p.order)
    phase_start_offset: dict[int, int] = {}
    cumulative = 0
    for phase in phases_sorted:
        phase_start_offset[phase.id] = cumulative
        cumulative += phase.duration_days

    max_shortfall = 0

    for material in materials:
        if material.lead_time_days < 0:
            raise SchedulingError(
                f"Material '{material.name}' has a negative lead time."
            )

        phase_offset = phase_start_offset.get(material.phase_id)
        if phase_offset is None:
            raise SchedulingError(
                f"Material '{material.name}' references a non-existent phase."
            )

        # Shortfall: how many extra days before desired_start must we order?
        # lead_time_days must be <= phase_offset for the material to arrive in time.
        shortfall = material.lead_time_days - phase_offset
        max_shortfall = max(max_shortfall, shortfall)

    return desired_start + timedelta(days=max(0, max_shortfall))
