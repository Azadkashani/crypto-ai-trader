# PROJECT RULES

Project Name:
Crypto AI Bot

Version:
1.0

---

# Project Goal

Build a professional AI-powered Futures Trading Bot capable of scanning the Top 50 Futures markets 24/7 and automatically selecting the best trading opportunity based on Technical Analysis, Fundamental Analysis and Market Sentiment.

The bot will eventually execute trades automatically on a VPS.

---

# Trading Mode

FUTURES ONLY

This project was originally developed for Spot Trading.

From this version onward every new implementation must be designed for Futures Trading.

---

# Risk Management

1. Only one open position at any time.

2. Risk exactly 1% of Futures account balance per trade.

3. Minimum Risk Reward Ratio = 2

4. Position Size and Leverage must always be calculated from the 1% risk rule.

5. LONG and SHORT positions must both be supported.

---

# Final Scoring

Technical Score = 80%

Fundamental Score = 10%

Sentiment Score = 10%

Final Score = Weighted Combination

---

# Technical Analysis Components

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

---

# Development Rules

Development must always be completed step by step.

No new step may begin until:

- Implementation is complete.
- Testing is complete.
- Bugs are fixed.
- Step is approved.

---

# Code Quality

Every module must:

- Be modular.
- Be reusable.
- Use clean architecture.
- Use config.py whenever possible.
- Avoid hardcoded values.
- Include comments and docstrings.

---

# Codex Rules

Before every task:

Read PROJECT_RULES.md

Read PROJECT_PROGRESS.md

Only implement the requested step.

Never continue automatically.

Never modify unrelated modules.

Always stop after finishing the requested step.
