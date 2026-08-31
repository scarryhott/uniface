from __future__ import annotations

from copy import deepcopy

from closure_supernet.closure_ui_contract import (
    derive_open_ui_contract,
    validate_ui_contract,
)
from closure_supernet.interactive_natural_form_solver import (
    derive_interactive_natural_form_solver,
    solve_natural_form_point,
    validate_interactive_natural_form_solver,
)


def test_solver_is_the_exact_natural_form_of_interactive_equality_closure() -> None:
    contract = derive_open_ui_contract(
        perspective_id="perspective:solver-exactness"
    )
    solver = contract["interactive_natural_form_solver"]
    expected = derive_interactive_natural_form_solver(contract)
    validation = validate_interactive_natural_form_solver(
        solver,
        contract=contract,
    )

    assert solver == expected
    assert validation["valid"] is True
    assert solver["solver_kind"] == (
        "CANONICAL_CONSTRAINT_SOLUTION_OVER_INTERACTIVE_EQUALITY_CLOSURE"
    )
    assert solver["natural_form_is_interactive_interface_equality_closure"] is True
    assert solver["natural_form_is_posthoc_visual_template"] is False
    assert solver["family_switch_present"] is False
    assert solver["named_geometry_templates_present"] is False
    assert solver["family_name_authors_geometry"] is False
    assert solver["visual_resemblance_authors_geometry"] is False
    assert solver["rendering_can_witness_equality"] is False
    assert solver["solutions"]
    assert all(
        solution["solver_basis"]
        == "GENERIC_BOUNDED_HARMONIC_EQUALITY_CLOSURE_BASIS"
        for solution in solver["solutions"]
    )
    assert all(
        solution["constraints"]["linear_invertibility_witnessed"] is True
        and solution["constraints"]["family_name_used_as_geometry_selector"]
        is False
        and solution["constraints"]["named_geometry_template_present"] is False
        and solution["constraints"]["rendering_executes_as_equality"] is False
        for solution in solver["solutions"]
    )
    assert contract["supernet_closure_certificate"][
        "interactive_natural_form_solver_id"
    ] == solver["id"]
    assert validate_ui_contract(contract)["valid"] is True


def test_one_generic_solution_is_bounded_origin_fixed_and_hair_relative() -> None:
    contract = derive_open_ui_contract(
        perspective_id="perspective:solver-hair"
    )
    solution = contract["interactive_natural_form_solver"]["solutions"][0]

    assert solve_natural_form_point(solution, (500.0, 500.0)) == (500.0, 500.0)
    without_hair = solve_natural_form_point(solution, (760.0, 380.0))
    with_hair = solve_natural_form_point(
        solution,
        (760.0, 380.0),
        hair_millidegrees=90_000,
    )
    assert without_hair != with_hair
    for point in (without_hair, with_hair):
        assert 20.0 <= point[0] <= 980.0
        assert 20.0 <= point[1] <= 980.0

    # Hair changes presentation only; it is not an input to the content-
    # addressed server solver receipt or its equality closure signature.
    assert contract["interactive_natural_form_solver"]["id"] == (
        derive_interactive_natural_form_solver(contract)["id"]
    )


def test_tampered_or_template_authored_solver_is_rejected() -> None:
    contract = derive_open_ui_contract(
        perspective_id="perspective:solver-tamper"
    )

    forged = deepcopy(contract)
    forged_solver = forged["interactive_natural_form_solver"]
    forged_solver["solutions"][0]["coefficients"]["radial_milli"] += 1
    direct = validate_interactive_natural_form_solver(
        forged_solver,
        contract=forged,
    )
    assert direct["valid"] is False
    assert validate_ui_contract(forged)["valid"] is False

    template_authored = deepcopy(contract)
    template_authored["interactive_natural_form_solver"][
        "family_switch_present"
    ] = True
    template_authored["interactive_natural_form_solver"][
        "named_geometry_templates_present"
    ] = True
    template_authored["atlas_semantics"][
        "natural_form_is_posthoc_visual_template"
    ] = True
    assert validate_ui_contract(template_authored)["valid"] is False
