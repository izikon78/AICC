def main(self,num_of_runs):
	A=num_of_runs
	for B in range(A):
		if B==0:self.m_log.info(f"Starting controller service for {A} runs")
		else:self.m_log.info(f"Restarting controller service for run {B+1} of {A}")