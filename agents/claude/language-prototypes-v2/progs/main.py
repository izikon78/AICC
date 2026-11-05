def main(self, num_of_runs: int) -> None:
    for i in range(num_of_runs):
        if i == 0:
            self.m_log.info(f"Starting controller service for {num_of_runs} runs")
        else:
            self.m_log.info(f"Restarting controller service for run {i + 1} of {num_of_runs}")
