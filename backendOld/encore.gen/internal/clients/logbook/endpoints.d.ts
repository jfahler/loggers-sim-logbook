import { CallOpts } from "encore.dev/api";

type Parameters<T> = T extends (...args: infer P) => unknown ? P : never;
type WithCallOpts<T extends (...args: any) => any> = (
  ...args: [...Parameters<T>, opts?: CallOpts]
) => ReturnType<T>;

import { getFlight as getFlight_handler } from "../../../../logbook/get_flight.js";
declare const getFlight: WithCallOpts<typeof getFlight_handler>;
export { getFlight };

import { listFlights as listFlights_handler } from "../../../../logbook/list_flights.js";
declare const listFlights: WithCallOpts<typeof listFlights_handler>;
export { listFlights };

import { listPilots as listPilots_handler } from "../../../../logbook/list_pilots.js";
declare const listPilots: WithCallOpts<typeof listPilots_handler>;
export { listPilots };

import { uploadTacview as uploadTacview_handler } from "../../../../logbook/upload.js";
declare const uploadTacview: WithCallOpts<typeof uploadTacview_handler>;
export { uploadTacview };


