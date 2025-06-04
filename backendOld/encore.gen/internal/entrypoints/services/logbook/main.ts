import { registerHandlers, run, type Handler } from "encore.dev/internal/codegen/appinit";
import { Worker, isMainThread } from "node:worker_threads";
import { fileURLToPath } from "node:url";
import { availableParallelism } from "node:os";

import { getFlight as getFlightImpl0 } from "../../../../../logbook/get_flight";
import { listFlights as listFlightsImpl1 } from "../../../../../logbook/list_flights";
import { listPilots as listPilotsImpl2 } from "../../../../../logbook/list_pilots";
import { uploadTacview as uploadTacviewImpl3 } from "../../../../../logbook/upload";
import * as logbook_service from "../../../../../logbook/encore.service";

const handlers: Handler[] = [
    {
        apiRoute: {
            service:           "logbook",
            name:              "getFlight",
            handler:           getFlightImpl0,
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
            handler:           listFlightsImpl1,
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
            handler:           listPilotsImpl2,
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
            handler:           uploadTacviewImpl3,
            raw:               false,
            streamingRequest:  false,
            streamingResponse: false,
        },
        endpointOptions: {"expose":true,"auth":false,"isRaw":false,"isStream":false,"tags":[]},
        middlewares: logbook_service.default.cfg.middlewares || [],
    },
];

registerHandlers(handlers);

await run(import.meta.url);
