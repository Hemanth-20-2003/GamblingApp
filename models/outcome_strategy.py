"""Outcome determination strategies for UC5 Win/Loss Calculation"""
import random


class RandomOutcomeStrategy:
    def determine(self, win_probability: float) -> bool:
        return random.random() < win_probability


class WeightedProbabilityStrategy:
    """Applies a house edge that reduces effective win probability."""
    def __init__(self, house_edge: float = 0.02):
        self.house_edge = house_edge

    def determine(self, win_probability: float) -> bool:
        effective_prob = win_probability * (1 - self.house_edge)
        return random.random() < effective_prob
