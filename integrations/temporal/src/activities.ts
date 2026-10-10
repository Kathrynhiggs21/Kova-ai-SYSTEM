export async function verifySyntheticTask(taskId: string): Promise<boolean> {
  // Synthetic pilot only. No real account or personal-data access.
  if (!/^kova-test-[a-z0-9-]{1,48}$/.test(taskId)) throw new Error("Invalid synthetic task ID");
  return true;
}
