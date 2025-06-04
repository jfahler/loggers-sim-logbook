import { registerGateways, registerHandlers, run, type Handler } from "encore.dev/internal/codegen/appinit";

import { sendPilotStats as discord_sendPilotStatsImpl0 } from "../../../../discord/send_pilot_stats";
import { sendFlightSummary as discord_sendFlightSummaryImpl1 } from "../../../../discord/webhook";
import { getFlight as logbook_getFlightImpl2 } from "../../../../logbook/get_flight";
import { listFlights as logbook_listFlightsImpl3 } from "../../../../logbook/list_flights";
import { listPilots as logbook_listPilotsImpl4 } from "../../../../logbook/list_pilots";
import { uploadTacview as logbook_uploadTacviewImpl5 } from "../../../../logbook/upload";
import * as discord_service from "../../../../discord/encore.service";
import * as frontend_service from "../../../../frontend/encore.service";
import * as logbook_service from "../../../../logbook/encore.service";

const gateways: any[] = [
];

const handlers: Handler[] = [
    {
        apiRoute: {
            service:           "discord",
            name:              "sendPilotStats",
            handler:           discord_sendPilotStatsImpl0,
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
            handler:           discord_sendFlightSummaryImpl1,
            raw:               false,
            streamingRequest:  false,
            streamingResponse: false,
        },
        endpointOptions: {"expose":true,"auth":false,"isRaw":false,"isStream":false,"tags":[]},
        middlewares: discord_service.default.cfg.middlewares || [],
    },
    {
        apiRoute: {
            service:           "logbook",
            name:              "getFlight",
            handler:           logbook_getFlightImpl2,
            raw:               false,
            streamingRequest:  false,
            streamingResponse: false,
        },
        endpointOptions: {"expose":true,"auth":false,"isRaw":false,"isStream":false,"tags":[]},
        middlewares: logbook_service.default.cfg.middlewares || [],
    },
    {
        apiRoute: {
            service:           "logbook",
            name:              "listFlights",
            handler:           logbook_listFlightsImpl3,
            raw:               false,
            streamingRequest:  false,
            streamingResponse: false,
        },
        endpointOptions: {"expose":true,"auth":false,"isRaw":false,"isStream":false,"tags":[]},
        middlewares: logbook_service.default.cfg.middlewares || [],
    },
    {
        apiRoute: {
            service:           "logbook",
            name:              "listPilots",
            handler:           logbook_listPilotsImpl4,
            raw:               false,
            streamingRequest:  false,
            streamingResponse: false,
        },
        endpointOptions: {"expose":true,"auth":false,"isRaw":false,"isStream":false,"tags":[]},
        middlewares: logbook_service.default.cfg.middlewares || [],
    },
    {
        apiRoute: {
            service:           "logbook",
            name:              "uploadTacview",
            handler:           logbook_uploadTacviewImpl5,
            raw:               false,
            streamingRequest:  false,
            streamingResponse: false,
        },
        endpointOptions: {"expose":true,"auth":false,"isRaw":false,"isStream":false,"tags":[]},
        middlewares: logbook_service.default.cfg.middlewares || [],
    },
];

registerGateways(gateways);
registerHandlers(handlers);

await run(import.meta.url);
