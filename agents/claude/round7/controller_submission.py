"""Arm C: T1 authored as new Python, without importing the reference implementation.
Contamination note: this exact C# example was implemented repeatedly earlier in the same conversation (Rounds 2-5)."""


def controller_logs(n):
    if not isinstance(n, int) or isinstance(n, bool):  # mirror C#'s static int parameter
        raise TypeError("n must be an int")
    if n <= 0:
        return []
    return [f"Starting controller service for {n} runs"] + [
        f"Restarting controller service for run {i + 1} of {n}" for i in range(1, n)
    ]
