# main.py
"""
Main demo file for Gambling App
Demonstrates Use Case 4: Game Session Management
"""

import time
from service import GameSessionManager
from models import SessionParameters, SessionEndReason


def demo_use_case_4(gambler_id=1):
    """Use Case 4: Game Session Management"""
    print("\n" + "="*60)
    print("USE CASE 4: GAME SESSION MANAGEMENT")
    print("="*60)
    
    mgr = GameSessionManager()
    params = SessionParameters(upper_limit=1000.0, lower_limit=100.0,
                                min_bet=5.0, max_bet=200.0, win_probability=0.5)

    # 1. Start new session
    print("\n[1] Starting new gaming session...")
    gs = mgr.start_new_session(gambler_id, initial_stake=500.0, params=params)
    print(f"Session ID: {gs.session_id}, Initial Stake: {gs.current_stake:.2f}")

    # 2. Continue session with games
    print("\n[2] Playing 5 games...")
    mgr.continue_session(gambler_id, bet_amount=20.0, n_games=5)
    gs = mgr.get_session(gambler_id)
    if gs:
        print(f"Games played: {gs.total_games}, Wins: {gs.wins}, Losses: {gs.losses}, Stake: {gs.current_stake:.2f}")
    else:
        print("Session already ended (boundary reached)")
        return

    # 3. Pause session
    print("\n[3] Pausing session...")
    pr = mgr.pause_session(gambler_id, reason="Bio break")
    time.sleep(0.5)

    # 4. Resume session
    print("\n[4] Resuming session...")
    mgr.resume_session(gambler_id)

    # 5. Play more games
    print("\n[5] Playing 3 more games...")
    mgr.continue_session(gambler_id, bet_amount=20.0, n_games=3)
    gs = mgr.get_session(gambler_id)
    if gs:
        print(f"Total games: {gs.total_games}, Current stake: {gs.current_stake:.2f}")

    # 6. End session
    print("\n[6] Ending session...")
    gs = mgr.get_session(gambler_id)
    if gs:
        summary = mgr.end_session(gambler_id, SessionEndReason.MANUAL)
        print(f"\nFinal Summary:")
        for key, value in summary.items():
            print(f"  {key:<20}: {value}")
    else:
        print("Session already ended (boundary reached)")


if __name__ == "__main__":
    print("\n" + "#"*60)
    print("# GAMBLING APP - GAME SESSION MANAGEMENT DEMO")
    print("#"*60)
    
    # Run Use Case 4
    demo_use_case_4()
    
    print("\n" + "#"*60)
    print("# DEMO COMPLETE")
    print("#"*60 + "\n")
