"""
Unit tests for services/scheduler.py

Phases used across tests:
  Foundation  order=1  duration=10  (starts at day 0)
  Framing     order=2  duration=15  (starts at day 10)
  MEP         order=3  duration=20  (starts at day 25)
  Interior    order=4  duration=12  (starts at day 45)
"""
import pytest
from datetime import datetime, timedelta

from app.models.material import Material
from app.models.phase import Phase
from services.scheduler import calculate_earliest_start
from utils.exceptions import SchedulingError

START = datetime(2026, 1, 1)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def phases() -> list[Phase]:
    return [
        Phase(id=1, name="Foundation", order=1, duration_days=10),
        Phase(id=2, name="Framing",    order=2, duration_days=15),
        Phase(id=3, name="MEP",        order=3, duration_days=20),
        Phase(id=4, name="Interior",   order=4, duration_days=12),
    ]


# ---------------------------------------------------------------------------
# Happy-path tests
# ---------------------------------------------------------------------------

def test_no_delay_when_all_materials_arrive_in_time(phases):
    """Materials whose lead times are covered by preceding phase durations cause no delay."""
    # All materials are assigned to phases 2+ where phase_start_offset >= lead_time.
    materials = [
        Material(name="Lumber",    lead_time_days=8,  phase_id=2),  # phase starts day 10 → shortfall -2
        Material(name="HVAC Unit", lead_time_days=20, phase_id=3),  # phase starts day 25 → shortfall -5
        Material(name="Flooring",  lead_time_days=40, phase_id=4),  # phase starts day 45 → shortfall -5
    ]
    result = calculate_earliest_start(materials, phases, START)
    assert result == START


def test_single_material_drives_delay(phases):
    """A single long-lead material correctly pushes the start date."""
    # Custom windows: lead_time=30, assigned to Framing (starts day 10) → shortfall=20
    materials = [Material(name="Custom Windows", lead_time_days=30, phase_id=2)]
    result = calculate_earliest_start(materials, phases, START)
    assert result == START + timedelta(days=20)


def test_critical_path_is_longest_shortfall(phases):
    """The returned date reflects the maximum shortfall, not the first or last material."""
    materials = [
        Material(name="Concrete",       lead_time_days=5,  phase_id=1),  # shortfall  5
        Material(name="Structural Steel", lead_time_days=40, phase_id=2),  # shortfall 30  ← critical
        Material(name="HVAC Unit",      lead_time_days=22, phase_id=3),  # shortfall -3
    ]
    result = calculate_earliest_start(materials, phases, START)
    assert result == START + timedelta(days=30)


def test_material_in_last_phase_with_sufficient_lead_time(phases):
    """Material in the last phase with lead_time < phase_start_offset causes no delay."""
    # Interior starts at day 45; lead_time=40 → shortfall=-5
    materials = [Material(name="Flooring", lead_time_days=40, phase_id=4)]
    result = calculate_earliest_start(materials, phases, START)
    assert result == START


def test_material_in_last_phase_causes_delay(phases):
    """Material in the last phase with lead_time > phase_start_offset causes delay."""
    # Interior starts at day 45; lead_time=50 → shortfall=5
    materials = [Material(name="Custom Cabinetry", lead_time_days=50, phase_id=4)]
    result = calculate_earliest_start(materials, phases, START)
    assert result == START + timedelta(days=5)


def test_zero_lead_time_material_never_delays(phases):
    """A material with zero lead time should never cause a delay."""
    materials = [Material(name="Paint", lead_time_days=0, phase_id=1)]
    result = calculate_earliest_start(materials, phases, START)
    assert result == START


def test_multiple_materials_same_phase(phases):
    """When multiple materials share a phase, the worst one drives the schedule."""
    # Framing starts day 10; shortfalls: 5, 15, 0
    materials = [
        Material(name="Lumber A",  lead_time_days=15, phase_id=2),  # shortfall  5
        Material(name="Lumber B",  lead_time_days=25, phase_id=2),  # shortfall 15  ← critical
        Material(name="Bolts",     lead_time_days=10, phase_id=2),  # shortfall  0
    ]
    result = calculate_earliest_start(materials, phases, START)
    assert result == START + timedelta(days=15)


def test_phases_evaluated_in_order_regardless_of_input_order(phases):
    """Phase ordering must be derived from Phase.order, not list position."""
    shuffled = [phases[3], phases[1], phases[0], phases[2]]  # 4,2,1,3
    materials = [Material(name="Steel", lead_time_days=40, phase_id=2)]  # shortfall 30
    result = calculate_earliest_start(materials, shuffled, START)
    assert result == START + timedelta(days=30)


def test_desired_start_is_preserved_as_base(phases):
    """The delay is always relative to the caller-supplied desired_start."""
    custom_start = datetime(2027, 6, 15)
    materials = [Material(name="Steel", lead_time_days=40, phase_id=2)]  # shortfall 30
    result = calculate_earliest_start(materials, phases, custom_start)
    assert result == custom_start + timedelta(days=30)


# ---------------------------------------------------------------------------
# Validation / error-path tests
# ---------------------------------------------------------------------------

def test_raises_when_no_phases():
    materials = [Material(name="Concrete", lead_time_days=5, phase_id=1)]
    with pytest.raises(SchedulingError, match="phase"):
        calculate_earliest_start(materials, [], START)


def test_raises_when_no_materials(phases):
    with pytest.raises(SchedulingError, match="material"):
        calculate_earliest_start([], phases, START)


def test_raises_on_negative_lead_time(phases):
    materials = [Material(name="Bad Material", lead_time_days=-1, phase_id=1)]
    with pytest.raises(SchedulingError, match="negative"):
        calculate_earliest_start(materials, phases, START)


def test_raises_when_material_references_nonexistent_phase(phases):
    materials = [Material(name="Ghost Material", lead_time_days=5, phase_id=99)]
    with pytest.raises(SchedulingError, match="non-existent phase"):
        calculate_earliest_start(materials, phases, START)
