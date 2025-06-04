import { CallOpts } from "encore.dev/api";

type Parameters<T> = T extends (...args: infer P) => unknown ? P : never;
type WithCallOpts<T extends (...args: any) => any> = (
  ...args: [...Parameters<T>, opts?: CallOpts]
) => ReturnType<T>;

import { sendPilotStats as sendPilotStats_handler } from "../../../../discord/send_pilot_stats.js";
declare const sendPilotStats: WithCallOpts<typeof sendPilotStats_handler>;
export { sendPilotStats };

import { sendFlightSummary as sendFlightSummary_handler } from "../../../../discord/webhook.js";
declare const sendFlightSummary: WithCallOpts<typeof sendFlightSummary_handler>;
export { sendFlightSummary };


