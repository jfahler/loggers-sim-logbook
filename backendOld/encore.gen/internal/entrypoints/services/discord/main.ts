import { registerHandlers, run, type Handler } from "encore.dev/internal/codegen/appinit";
import { Worker, isMainThread } from "node:worker_threads";
import { fileURLToPath } from "node:url";
import { availableParallelism } from "node:os";

import { sendPilotStats as sendPilotStatsImpl0 } from "../../../../../discord/send_pilot_stats";
import { sendFlightSummary as sendFlightSummaryImpl1 } from "../../../../../discord/webhook";
import * as discord_service from "../../../../../discord/encore.service";

const handlers: Handler[] = [
    {
        apiRoute: {
            service:           "discord",
            name:              "sendPilotStats",
            handler:           sendPilotStatsImpl0,
            raw:               false,
            streamingRequest:  false,
            streamingResponse: false,
        },
        endpointOptions: {"expose":true,"auth":false,"isRaw":false,"isStream":false,"tags":[]},
        middlewares: discord_service.default.cfg.middlewares || [],
    },
    {
        apiRoute: {
            service:           "discord",
            name:              "sendFlightSummary",
            handler:           sendFlightSummaryImpl1,
            raw:               false,
            streamingRequest:  false,
            streamingResponse: false,
        },
        endpointOptions: {"expose":true,"auth":false,"isRaw":false,"isStream":false,"tags":[]},
        middlewares: discord_service.default.cfg.middlewares || [],
    },
];

registerHandlers(handlers);

await run(import.meta.url);
