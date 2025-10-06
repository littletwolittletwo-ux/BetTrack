export function saveAuth(token: string, role: "admin"|"employee") {
  localStorage.setItem("token", token);
  localStorage.setItem("role", role);
}
export function logout() {
  localStorage.removeItem("token");
  localStorage.removeItem("role");
  location.href = "/admin/";
}
export function getRole(): "admin"|"employee"|null {
  return (localStorage.getItem("role") as any) || null;
}
export function hasAuth() { return !!localStorage.getItem("token"); }

// API utility for authenticated requests
export const api = {
  get: async (url: string) => {
    const token = localStorage.getItem("token");
    const response = await fetch(url, {
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json"
      }
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return { data: await response.json() };
  },
  
  post: async (url: string, data?: any) => {
    const token = localStorage.getItem("token");
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json"
      },
      body: data ? JSON.stringify(data) : undefined
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return { data: await response.json() };
  },
  
  postForm: async (url: string, formData: FormData) => {
    const token = localStorage.getItem("token");
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`
      },
      body: formData
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return { data: await response.json() };
  },
  
  delete: async (url: string) => {
    const token = localStorage.getItem("token");
    const response = await fetch(url, {
      method: "DELETE",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json"
      }
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return { data: await response.json() };
  }
};