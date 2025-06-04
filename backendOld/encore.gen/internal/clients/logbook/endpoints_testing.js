import { apiCall, streamIn, streamOut, streamInOut } from "encore.dev/internal/codegen/api";
import { registerTestHandler } from "encore.dev/internal/codegen/appinit";

import * as logbook_service from "../../../../logbook/encore.service";

export async function getFlight(params, opts) {
    const handler = (await import("../../../../logbook/get_flight")).getFlight;
    registerTestHandler({
        apiRoute: { service: "logbook", name: "getFlight", raw: false, handler, streamingRequest: false, streamingResponse: false },
        middlewares: logbook_service.default.cfg.middlewares || [],
        endpointOptions: {"expose":true,"auth":false,"isRaw":false,"isStream":false,"tags":[]},
    });

    return apiCall("logbook", "getFlight", params, opts);
}

export async function listFlights(params, opts) {
    const handler = (await import("../../../../logbook/list_flights")).listFlights;
    registerTestHandler({
        apiRoute: { service: "logbook", name: "listFlights", raw: false, handler, streamingRequest: false, streamingResponse: false },
        middlewares: logbook_service.default.cfg.middlewares || [],
        endpointOptions: {"expose":true,"auth":false,"isRaw":false,"isStream":false,"tags":[]},
    });

    return apiCall("logbook", "listFlights", params, opts);
}

export async function listPilots(params, opts) {
    const handler = (await import("../../../../logbook/list_pilots")).listPilots;
    registerTestHandler({
        apiRoute: { service: "logbook", name: "listPilots", raw: false, handler, streamingRequest: false, streamingResponse: false },
        middlewares: logbook_service.default.cfg.middlewares || [],
        endpointOptions: {"expose":true,"auth":false,"isRaw":false,"isStream":false,"tags":[]},
    });

    return apiCall("logbook", "listPilots", params, opts);
}

export async function uploadTacview(params, opts) {
    const handler = (await import("../../../../logbook/upload")).uploadTacview;
    registerTestHandler({
        apiRoute: { service: "logbook", name: "uploadTacview", raw: false, handler, streamingRequest: false, streamingResponse: false },
        middlewares: logbook_service.default.cfg.middlewares || [],
        endpointOptions: {"expose":true,"auth":false,"isRaw":false,"isStream":false,"tags":[]},
    });

    return apiCall("logbook", "uploadTacview", params, opts);
}

