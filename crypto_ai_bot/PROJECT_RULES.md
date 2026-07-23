# PROJECT_RULES.md

# Crypto AI Bot

Version: 1.0

---

# Project Goal

The goal of this project is to build a professional AI-powered Futures Trading Bot capable of scanning the Top 50 Futures markets 24/7 and automatically selecting the best trading opportunity based on multiple analysis engines.

The bot will eventually execute trades automatically on a VPS.

---

# Trading Mode

Current Development Target:

FUTURES ONLY

The project was originally created for Spot Trading.

From this point forward every new implementation must be designed for Futures Trading.

Spot logic may only be reused if it is also valid for Futures.

---

# Risk Management

The following rules are mandatory.

1. Maximum one open position at any time.

2. Risk exactly 1% of Futures account balance per trade.

3. Minimum Risk Reward Ratio:

RR >= 2

4. Position Size and Leverage must always be calculated from the 1% risk rule.

5. LONG and SHORT positions must both be supported.

---

# Development Rules

Development must always be completed step by step.

A new step must NEVER begin before:

- Implementation is complete
- Testing is complete
- Bugs are fixed
- Step is approved

Never skip steps.

---

# Phase Order

Phase 1
Technical Analysis Engine

Phase 2
Fundamental Analysis Engine

Phase 3
Market Sentiment Engine

Phase 4
Final Scoring Engine

Phase 5
Trade Management

Phase 6
Risk Management

Phase 7
Execution Engine

Phase 8
Backtesting

Phase 9
Paper Trading

Phase 10
Live Trading

---

# Scoring System

Final Score consists of:

Technical Score = 80%

Fundamental Score = 10%

Sentiment Score = 10%

Final Score = Weighted Combination

---

# Technical Analysis Components

Technical Score will eventually include:

1. Market Structure

2. Order Block

3. Liquidity

4. Fair Value Gap

5. Breakout

6. Volume

7. Multi Timeframe

8. EMA

9. RSI

10. MACD

11. ADX

12. ATR

13. Support & Resistance

14. Divergence

Each component will be implemented separately and tested separately.

---

# Code Quality Rules

Every module must:

- Be modular
- Be reusable
- Have clean architecture
- Use clear comments
- Include docstrings
- Avoid hardcoded values
- Read configuration from config.py whenever possible

---

# Codex Rules

Before every task Codex must:

Read this PROJECT_RULES.md file.

Only perform the requested Step.

Never continue to another Step automatically.

Never redesign unrelated files.

Never change project architecture unless requested.

Always explain changes briefly after implementation.

---

# Testing Rules

Every implementation must be tested before moving to the next step.

If any bug exists:

Fix first.

Continue later.

---

End of Version 1.0
