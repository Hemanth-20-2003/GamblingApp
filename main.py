# use_case_1_gambler_profile.py
"""
Use Case 1: Gambler Profile Management
- Create new gambler with initial stake, win threshold, and loss threshold
- Update gambler personal information and betting preferences
- Retrieve gambler statistics and current financial status
- Validate gambler eligibility based on minimum stake requirements
- Reset gambler profile to initial state for new gaming session

Updated to use reorganized package structure:
  - models: GamblerProfile, BettingPreferences, GamblerStatisticsDTO
  - service: GamblerProfileService
  - config: database connection (db.py)
"""

from service import GamblerProfileService


# ──────────────────────────────────────────────
# Demo
# ──────────────────────────────────────────────
if __name__ == "__main__":
    svc = GamblerProfileService()

    # 1. Create
    p = svc.create_gambler("Alice", "alice@example.com",
                           initial_stake=500.0,
                           win_threshold=1000.0,
                           loss_threshold=100.0)
    print(p)

    # 2. Update
    svc.update_gambler(p.id, name="Alice Smith", max_bet=200.0)

    # 3. Retrieve
    profile, prefs, stats = svc.retrieve_gambler(p.id)
    print(profile, prefs.__dict__, stats)

    # 4. Validate
    eligibility = svc.validate_eligibility(p.id)
    print("Eligible:", eligibility)

    # 5. Reset
    svc.reset_gambler(p.id, new_initial_stake=600.0)
