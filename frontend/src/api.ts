const API_BASE = '/api';

export async function listPilots() {
  const res = await fetch(`${API_BASE}/pilots`);
  if (!res.ok) throw new Error('Failed to fetch pilots');
  return res.json();
}

export async function listFlights(params: { limit?: number; offset?: number } = {}) {
  const query = new URLSearchParams();
  if (params.limit !== undefined) query.append('limit', String(params.limit));
  if (params.offset !== undefined) query.append('offset', String(params.offset));
  const res = await fetch(`${API_BASE}/flights?${query.toString()}`);
  if (!res.ok) throw new Error('Failed to fetch flights');
  return res.json();
}

export async function getFlight(id: number) {
  const res = await fetch(`${API_BASE}/flights/${id}`);
  if (!res.ok) throw new Error('Failed to fetch flight');
  return res.json();
}

export async function uploadXml(file: File) {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${API_BASE}/upload_xml`, { method: 'POST', body: formData });
  if (!res.ok) throw new Error('Failed to upload file');
  return res.json();
}

export async function sendPilotStats(data: any) {
  const res = await fetch(`${API_BASE}/discord/pilot-stats`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error('Failed to send pilot stats');
  return res.json();
}

export async function sendFlightSummary(data: any) {
  const res = await fetch(`${API_BASE}/discord/flight-summary`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error('Failed to send flight summary');
  return res.json();
}

export async function getSquadronCallsigns() {
  const res = await fetch(`${API_BASE}/squadron-callsigns`);
  if (!res.ok) throw new Error('Failed to fetch squadron callsigns');
  return res.json();
}

export async function updateSquadronCallsigns(callsigns: string[]) {
  const res = await fetch(`${API_BASE}/squadron-callsigns`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ callsigns }),
  });
  if (!res.ok) throw new Error('Failed to update squadron callsigns');
  return res.json();
}

export default {
  listPilots,
  listFlights,
  getFlight,
  uploadXml,
  sendPilotStats,
  sendFlightSummary,
  getSquadronCallsigns,
  updateSquadronCallsigns,
};
