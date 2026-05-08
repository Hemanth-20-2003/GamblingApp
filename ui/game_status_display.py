"""
Game Status Display - UC7 User Interaction
Displays current stake, game status, outcomes, and session summaries
"""

from config.db import get_connection, execute_one


class GameStatusDisplay:
    @staticmethod
    def header(title="GAMBLING APP"):
        width = 52
        print("\n" + "═" * width)
        print(f"  {title.center(width - 4)}")
        print("═" * width)

    @staticmethod
    def display_current_status(gambler_id: int):
        """UC7 – Use Case 1: Display current stake and game status."""
        conn = get_connection()
        try:
            g = execute_one(conn, "SELECT * FROM gamblers WHERE id=%s",
                            (gambler_id,))
            if not g:
                print(f"  No gambler with id={gambler_id}")
                return

            s = execute_one(conn,
                "SELECT * FROM gambler_statistics WHERE gambler_id=%s",
                (gambler_id,))

            # Latest active session
            sess = execute_one(conn,
                """SELECT * FROM game_sessions
                   WHERE gambler_id=%s AND status IN ('ACTIVE','PAUSED')
                   ORDER BY started_at DESC LIMIT 1""",
                (gambler_id,))

        finally:
            conn.close()

        print(f"\n  Gambler  : {g['name']}  (id={g['id']})")
        print(f"  Stake    : ₹{float(g['current_stake']):>12,.2f}")
        print(f"  Win ↑    : ₹{float(g['win_threshold']):>12,.2f}")
        print(f"  Loss ↓   : ₹{float(g['loss_threshold']):>12,.2f}")
        if s:
            total = (s['total_wins'] or 0) + (s['total_losses'] or 0)
            rate  = ((s['total_wins'] or 0) / total * 100) if total else 0
            print(f"  Bets     : {total}  (W:{s['total_wins']}  L:{s['total_losses']}  "
                  f"Rate:{rate:.1f}%)")
        if sess:
            print(f"  Session  : id={sess['id']}  status={sess['status']}  "
                  f"games={sess['total_games']}")

    @staticmethod
    def display_game_outcome(game_number: int, outcome: str,
                             bet_amount: float, payout: float,
                             stake_before: float, stake_after: float):
        """UC7 – Use Case 3: Show game outcome and updated stake."""
        icon = " WIN " if outcome == "WIN" else " LOSS"
        change = stake_after - stake_before
        sign   = "+" if change >= 0 else ""
        print(f"\n  Game #{game_number:<4} {icon}  "
              f"bet=₹{bet_amount:.2f}  "
              f"payout=₹{payout:.2f}  "
              f"stake: ₹{stake_before:.2f} → ₹{stake_after:.2f}  "
              f"({sign}{change:.2f})")

    @staticmethod
    def display_session_summary(session_summary: dict):
        """UC7 – Use Case 4: Present session summary at conclusion."""
        GameStatusDisplay.header("SESSION SUMMARY")
        labels = {
            "session_id":    "Session ID",
            "status":        "Final Status",
            "final_stake":   "Final Stake",
            "total_games":   "Games Played",
            "wins":          "Wins",
            "losses":        "Losses",
            "win_rate":      "Win Rate %",
            "active_seconds":"Active Time (s)",
        }
        for key, label in labels.items():
            val = session_summary.get(key, "—")
            if isinstance(val, float):
                print(f"  {label:<20}: {val:,.2f}")
            else:
                print(f"  {label:<20}: {val}")
        print("═" * 52)
