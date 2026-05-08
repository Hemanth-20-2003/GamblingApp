# Gambling App

A Python-based gambling simulation application that models a calculative gambler managing stakes through strategic betting with defined upper and lower limits.

## Features

- **Gambler Profile Management** - Create and manage gambler profiles with betting preferences
- **Stake Management** - Real-time stake tracking with transaction history and boundary validation
- **Betting System** - Multiple betting strategies (Fixed, Percentage, Martingale, Fibonacci, D'Alembert)
- **Game Sessions** - Complete session lifecycle management with pause/resume functionality
- **Win/Loss Tracking** - Comprehensive statistics including streaks, win rates, and profit calculations
- **Input Validation** - Robust error handling and validation for all user inputs
- **Interactive UI** - Menu-driven interface for user interaction

## Project Structure

```
├── config/          - Database and configuration
├── exceptions/      - Custom exception classes
├── models/          - Data models and entities
├── service/         - Business logic and services
├── ui/              - User interface components
├── main.py          - Application entry point
└── README.md        - This file
```

## Getting Started

### Requirements
- Python 3.7+

### Running the Application

```bash
python main.py
```

## Core Components

- **GamblerProfile** - Manages gambler information and statistics
- **StakeManagementService** - Handles stake tracking and validation
- **BettingService** - Processes bets and betting strategies
- **GameSessionManager** - Manages gaming sessions
- **WinLossCalculator** - Calculates and tracks outcomes
- **InputValidator** - Validates all user inputs

## Usage

1. Start the application
2. Create a gambler profile with initial stake and thresholds
3. Begin a gaming session
4. Place bets using various strategies
5. View session statistics and summaries