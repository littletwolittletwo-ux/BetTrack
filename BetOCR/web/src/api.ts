export type Token = { access_token: string; role: "admin"|"employee" };
const BASE = ""; // proxied in dev, served by FastAPI in prod

function authHeader() {
  const t = localStorage.getItem("token");
  return t ? { Authorization: "Bearer " + t } : undefined;
}
async function jsonFetch<T>(url: string, init?: RequestInit): Promise<T> {
  const r = await fetch(url, init);
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function login(username: string, password: string): Promise<Token> {
  return jsonFetch<Token>(`${BASE}/auth/login`, {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password })
  });
}

export async function setStats(hours=72) {
  return jsonFetch<any[]>(`/stats/sets?hours=${hours}`, { headers: { ...authHeader() } });
}

export async function uploadBet(fd: FormData) {
  return jsonFetch(`/bets/upload`, { method: "POST", headers: { ...authHeader() }, body: fd });
}

export async function fetchSets(active?: boolean) {
  const url = new URL(`/admin/sets`, location.origin);
  if (active !== undefined) url.searchParams.set("active", String(active));
  return jsonFetch(url.toString().replace(location.origin, ""), { headers: { ...authHeader() } });
}

export async function createSet(name: string) {
  return jsonFetch(`/admin/sets`, { method: "POST", headers: { "Content-Type":"application/json", ...authHeader() }, body: JSON.stringify({ name }) });
}
export async function renameSet(id:number, name:string) {
  return jsonFetch(`/admin/sets/${id}`, { method: "PUT", headers: { "Content-Type":"application/json", ...authHeader() }, body: JSON.stringify({ name }) });
}
export async function toggleSet(id:number, is_active:boolean) {
  return jsonFetch(`/admin/sets/${id}/status`, { method: "PATCH", headers: { "Content-Type":"application/json", ...authHeader() }, body: JSON.stringify({ is_active }) });
}

export async function listUsers(params?: { role?: string; active?: boolean }) {
  const url = new URL(`/admin/users`, location.origin);
  if (params?.role) url.searchParams.set("role", params.role);
  if (params?.active !== undefined) url.searchParams.set("active", String(params.active));
  return jsonFetch(url.toString().replace(location.origin, ""), { headers: { ...authHeader() } });
}
export async function createUser(username:string, password:string, role:"admin"|"employee") {
  return jsonFetch(`/admin/users`, { method:"POST", headers:{ "Content-Type":"application/json", ...authHeader()}, body: JSON.stringify({ username, password, role }) });
}
export async function updateUser(id:number, payload: { username?:string; role?: "admin"|"employee" }) {
  return jsonFetch(`/admin/users/${id}`, { method:"PUT", headers:{ "Content-Type":"application/json", ...authHeader()}, body: JSON.stringify(payload) });
}
export async function patchUserStatus(id:number, is_active:boolean) {
  return jsonFetch(`/admin/users/${id}/status`, { method:"PATCH", headers:{ "Content-Type":"application/json", ...authHeader()}, body: JSON.stringify({ is_active }) });
}
export async function resetPassword(id:number, password:string) {
  return jsonFetch(`/admin/users/${id}/password`, { method:"POST", headers:{ "Content-Type":"application/json", ...authHeader()}, body: JSON.stringify({ password }) });
}

// Bet management functions for confirmation popup
export async function updateBet(betId: number, updates: any) {
  return jsonFetch(`/bets/${betId}`, { 
    method: "PATCH", 
    headers: { "Content-Type": "application/json", ...authHeader() }, 
    body: JSON.stringify(updates) 
  });
}

export async function deleteBet(betId: number) {
  return jsonFetch(`/bets/${betId}`, { 
    method: "DELETE", 
    headers: { ...authHeader() } 
  });
}

// CSV import function for both employees and admins
export async function importCSV(file: File, dryRun: boolean = false, defaultSet?: string) {
  const formData = new FormData();
  formData.append("file", file);
  const url = new URL(`/import/csv`, location.origin);
  url.searchParams.set("dry_run", String(dryRun));
  if (defaultSet) {
    url.searchParams.set("default_set", defaultSet);
  }
  return jsonFetch(url.toString().replace(location.origin, ""), {
    method: "POST",
    headers: { ...authHeader() },
    body: formData
  });
}