# main.py
"""
Main demo file for Gambling App
Demonstrates Use Case 3: Betting Mechanism
"""

from service import BettingService


def demo_use_case_3(gambler_id=1):
    """Use Case 3: Betting Mechanism"""
    print("\n" + "="*60)
    print("USE CASE 3: BETTING MECHANISM")
    print("="*60)
    
    svc = BettingService()

    # 1. Single bet
    print("\n[1] Placing a single bet...")
    bet = svc.place_bet(gambler_id, 50.0, win_probability=0.5, odds=2.0)
    won = svc.determine_outcome(0.5)
    print(f"Bet outcome: {'WIN' if won else 'LOSS'}")
    svc.settle_bet(bet, won)

    # 2. Validate bet amount
    print("\n[2] Validating bet amount...")
    validation = svc.validate_bet_amount(gambler_id, 75.0)
    print(f"Validation result: {validation}")

    # 3. Bet with strategy
    print("\n[3] Placing bet with Martingale strategy...")
    strategy_bet = svc.place_bet_with_strategy(gambler_id, "MARTINGALE", 
                                                base_bet=20.0,
                                                win_probability=0.5)
    won = svc.determine_outcome(0.5)
    svc.settle_bet(strategy_bet, won)

    # 4. Multiple consecutive bets
    print("\n[4] Placing 5 consecutive bets...")
    session = svc.place_consecutive_bets(gambler_id, count=5, 
                                         bet_amount=30.0,
                                         win_probability=0.48)
    print(f"Session summary: {session.summary()}")


if __name__ == "__main__":
    print("\n" + "#"*60)
    print("# GAMBLING APP - BETTING MECHANISM DEMO")
    print("#"*60)
    
    # Run Use Case 3
    demo_use_case_3()
    
    print("\n" + "#"*60)
    print("# DEMO COMPLETE")
    print("#"*60 + "\n")
