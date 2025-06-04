import { apiCall, streamIn, streamOut, streamInOut } from "encore.dev/internal/codegen/api";
import { registerTestHandler } from "encore.dev/internal/codegen/appinit";

import * as discord_service from "../../../../discord/encore.service";

export async function sendPilotStats(params, opts) {
    const handler = (await import("../../../../discord/send_pilot_stats")).sendPilotStats;
    registerTestHandler({
        apiRoute: { service: "discord", name: "sendPilotStats", raw: false, handler, streamingRequest: false, streamingResponse: false },
        middlewares: discord_service.default.cfg.middlewares || [],
        endpointOptions: {"expose":true,"auth":false,"isRaw":false,"isStream":false,"tags":[]},
    });

    return apiCall("discord", "sendPilotStats", params, opts);
}

export async function sendFlightSummary(params, opts) {
    const handler = (await import("../../../../discord/webhook")).sendFlightSummary;
    registerTestHandler({
        apiRoute: { service: "discord", name: "sendFlightSummary", raw: false, handler, streamingRequest: false, streamingResponse: false },
        middlewares: discord_service.default.cfg.middlewares || [],
        endpointOptions: {"expose":true,"auth":false,"isRaw":false,"isStream":false,"tags":[]},
    });

    return apiCall("discord", "sendFlightSummary", params, opts);
}

