import { NativeConnection, Worker } from "@temporalio/worker";
import * as activities from "./activities.js";

async function main() {
  if (process.env.KOVA_TEMPORAL_PILOT !== "enabled") throw new Error("Pilot disabled");
  const address = process.env.TEMPORAL_ADDRESS || "localhost:7233";
  const connection = await NativeConnection.connect({ address });
  const worker = await Worker.create({
    connection,
    namespace: process.env.TEMPORAL_NAMESPACE || "default",
    taskQueue: "kova-synthetic-pilot",
    workflowsPath: new URL("./workflows.ts", import.meta.url).pathname,
    activities,
  });
  await worker.run();
}
main().catch(error => { console.error("KOVA pilot worker failed", error.message); process.exitCode = 1; });
