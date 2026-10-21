import { proxyActivities, defineSignal, setHandler, condition } from "@temporalio/workflow";
import type * as activities from "./activities.js";

const { verifySyntheticTask } = proxyActivities<typeof activities>({
  startToCloseTimeout: "30 seconds",
  retry: { maximumAttempts: 3 },
});

const approve = defineSignal("approve");

export async function kovaPilotWorkflow(taskId: string): Promise<{taskId: string; verified: boolean}> {
  let approved = false;
  setHandler(approve, () => { approved = true; });
  // Approval must be explicitly signaled; no automatic external actions.
  await condition(() => approved);
  const verified = await verifySyntheticTask(taskId);
  return { taskId, verified };
}
