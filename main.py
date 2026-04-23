# main.py
"""
Main demo file for Gambling App
Demonstrates Use Case 2: Stake Management
"""

from service import StakeManagementService


def demo_use_case_2(gambler_id=1):
    """Use Case 2: Stake Management Operations"""
    print("\n" + "="*60)
    print("USE CASE 2: STAKE MANAGEMENT OPERATIONS")
    print("="*60)
    
    svc = StakeManagementService()

    # 1. Initialize stake
    print("\n[1] Initializing stake with boundaries...")
    monitor = svc.initialize_stake(gambler_id, 500.0, 1000.0, 100.0)
    print(f"Current stake: {monitor.current_stake}")

    # 2. Simulate betting
    print("\n[2] Simulating bet outcomes...")
    svc.calculate_after_bet(gambler_id, 50.0, won=True, payout=50.0)
    svc.calculate_after_bet(gambler_id, 30.0, won=False)
    svc.calculate_after_bet(gambler_id, 75.0, won=True, payout=150.0)

    # 3. Monitor fluctuations
    print("\n[3] Monitoring stake fluctuations...")
    fluctuations = svc.monitor_fluctuations(gambler_id)
    print(f"Fluctuations: {fluctuations}")

    # 4. Validate boundaries
    print("\n[4] Validating stake boundaries...")
    boundaries = svc.validate_boundaries(gambler_id)
    print(f"Boundaries: {boundaries}")

    # 5. Generate report
    print("\n[5] Generating stake history report...")
    report = svc.generate_report(gambler_id)
    report.print_report()


if __name__ == "__main__":
    print("\n" + "#"*60)
    print("# GAMBLING APP - STAKE MANAGEMENT DEMO")
    print("#"*60)
    
    # Run Use Case 2
    demo_use_case_2()
    
    print("\n" + "#"*60)
    print("# DEMO COMPLETE")
    print("#"*60 + "\n")
