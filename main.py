# main.py
"""
Main demo file for Gambling App
Demonstrates Use Case 6: Input Validation and Error Handling
"""

from service import InputValidator, SafeInputHandler
from models import ValidationConfig


def demo_use_case_6(gambler_id=1):
    """Use Case 6: Input Validation and Error Handling"""
    print("\n" + "="*60)
    print("USE CASE 6: INPUT VALIDATION AND ERROR HANDLING")
    print("="*60)
    
    v = InputValidator(gambler_id=gambler_id)

    cases = [
        ("Stake", v.validate_initial_stake, [500.0]),
        ("Stake (too low)", v.validate_initial_stake, [5.0]),
        ("Stake (negative)", v.validate_initial_stake, [-100]),
        ("Stake (NaN)", v.validate_initial_stake, [float("nan")]),
        ("Bet OK", v.validate_bet_amount, [50.0, 500.0]),
        ("Bet exceeds stake", v.validate_bet_amount, [600.0, 500.0]),
        ("Limits OK", v.validate_limits, [1000.0, 100.0, 500.0]),
        ("Limits bad", v.validate_limits, [100.0, 1000.0]),
        ("Prob OK", v.validate_probability, [0.5]),
        ("Prob out of range", v.validate_probability, [1.5]),
        ("Parse 'abc'", lambda x: v.parse_and_validate_numeric(x, "value")[1], ["abc"]),
    ]

    print("\n[1] Testing validation cases...")
    for name, fn, args in cases:
        r = fn(*args)
        print(f"\n[{name}]")
        print(r.report())

    # Test comprehensive validation
    print("\n\n[2] Comprehensive validation...")
    config = ValidationConfig()
    v_comp = InputValidator(config=config, gambler_id=gambler_id)
    r_all = v_comp.validate_all(
        initial_stake=500.0,
        bet_amount=50.0,
        upper_limit=1000.0,
        lower_limit=100.0,
        probability=0.5
    )
    print(r_all.report())

    # Test stake non-negative validation
    print("\n\n[3] Stake non-negative validation...")
    r_stake = v.validate_stake_non_negative(500.0)
    print(r_stake.report())

    # Test probability validation edge cases
    print("\n\n[4] Probability edge cases...")
    for prob in [0.05, 0.95, 0.02, 0.98]:
        r_prob = v.validate_probability(prob)
        print(f"\nProbability {prob}:")
        print(r_prob.report())


if __name__ == "__main__":
    print("\n" + "#"*60)
    print("# GAMBLING APP - INPUT VALIDATION AND ERROR HANDLING DEMO")
    print("#"*60)
    
    # Run Use Case 6
    demo_use_case_6()
    
    print("\n" + "#"*60)
    print("# DEMO COMPLETE")
    print("#"*60 + "\n")
