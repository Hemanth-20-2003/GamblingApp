# main.py
"""
Main demo file for Gambling App
Demonstrates Use Case 5: Win/Loss Calculation
"""

from service import WinLossCalculator
from models import OddsType, OddsConfig, WeightedProbabilityStrategy


def demo_use_case_5(session_id=1, gambler_id=1):
    """Use Case 5: Win/Loss Calculation"""
    print("\n" + "="*60)
    print("USE CASE 5: WIN/LOSS CALCULATION")
    print("="*60)
    
    init_bal = 500.0
    calc = WinLossCalculator(
        session_id, gambler_id, init_bal,
        outcome_strategy=WeightedProbabilityStrategy(house_edge=0.02),
        odds_config=OddsConfig(OddsType.DECIMAL, 1.95))

    # 1. Play 20 games
    print("\n[1] Playing 20 games...")
    for i in range(20):
        r = calc.play_game(bet_amount=25.0, win_probability=0.50)
        print(f"Game {r.game_number:>3}: {r.outcome:<4}  "
              f"stake: {r.stake_before:>8.2f} → {r.stake_after:>8.2f}")

    # 2. Calculate winnings
    print("\n[2] Calculating winnings...")
    winning = calc.calculate_winnings(50.0, 0.5)
    print(f"Winning on $50 bet: ${winning:.2f}")

    # 3. Calculate losses
    print("\n[3] Calculating losses...")
    loss = calc.calculate_loss(25.0)
    print(f"Loss on $25 bet: ${loss:.2f}")

    # 4. Win/Loss ratio
    print("\n[4] Win/Loss Ratio:")
    ratio_info = calc.get_win_loss_ratio()
    for k, v in ratio_info.items():
        print(f"  {k:<20}: {v}")

    # 5. Streak information
    print("\n[5] Streak Information:")
    streak_info = calc.get_streak_info()
    for k, v in streak_info.items():
        print(f"  {k:<25}: {v}")

    # 6. Full report
    print("\n[6] FULL REPORT:")
    for k, v in calc.full_report().items():
        print(f"  {k:<25}: {v}")


if __name__ == "__main__":
    print("\n" + "#"*60)
    print("# GAMBLING APP - WIN/LOSS CALCULATION DEMO")
    print("#"*60)
    
    # Run Use Case 5
    demo_use_case_5()
    
    print("\n" + "#"*60)
    print("# DEMO COMPLETE")
    print("#"*60 + "\n")
