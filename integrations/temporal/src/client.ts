import { Connection, Client } from "@temporalio/client";
import { kovaPilotWorkflow } from "./workflows.js";

async function main() {
  if (process.env.KOVA_TEMPORAL_PILOT !== "enabled") throw new Error("Pilot disabled");
  const connection = await Connection.connect({ address: process.env.TEMPORAL_ADDRESS || "localhost:7233" });
  const client = new Client({ connection, namespace: process.env.TEMPORAL_NAMESPACE || "default" });
  const taskId = "kova-test-first";
  const handle = await client.workflow.start(kovaPilotWorkflow, {
    taskQueue: "kova-synthetic-pilot",
    workflowId: taskId,
    args: [taskId],
  });
  console.log("Created approval-paused synthetic workflow", handle.workflowId);
  // Approval signal deliberately not sent by client.
}
main().catch(error => { console.error("KOVA pilot submission failed", error.message); process.exitCode = 1; });
