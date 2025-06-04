import { apiCall, streamIn, streamOut, streamInOut } from "encore.dev/internal/codegen/api";

const TEST_ENDPOINTS = typeof ENCORE_DROP_TESTS === "undefined" && process.env.NODE_ENV === "test"
    ? await import("./endpoints_testing.js")
    : null;

export async function getFlight(params, opts) {
    if (typeof ENCORE_DROP_TESTS === "undefined" && process.env.NODE_ENV === "test") {
        return TEST_ENDPOINTS.getFlight(params, opts);
    }

    return apiCall("logbook", "getFlight", params, opts);
}
export async function listFlights(params, opts) {
    if (typeof ENCORE_DROP_TESTS === "undefined" && process.env.NODE_ENV === "test") {
        return TEST_ENDPOINTS.listFlights(params, opts);
    }

    return apiCall("logbook", "listFlights", params, opts);
}
export async function listPilots(opts) {
    const params = undefined;
    if (typeof ENCORE_DROP_TESTS === "undefined" && process.env.NODE_ENV === "test") {
        return TEST_ENDPOINTS.listPilots(params, opts);
    }

    return apiCall("logbook", "listPilots", params, opts);
}
export async function uploadTacview(params, opts) {
    if (typeof ENCORE_DROP_TESTS === "undefined" && process.env.NODE_ENV === "test") {
        return TEST_ENDPOINTS.uploadTacview(params, opts);
    }

    return apiCall("logbook", "uploadTacview", params, opts);
}
