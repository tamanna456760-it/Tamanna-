import axios from "axios";

const safeAxios = axios.create();

safeAxios.interceptors.request.use(config => {
  const url = new URL(config.url, config.baseURL || "http://localhost");
  if (!ALLOWED_HOSTS.has(url.hostname)) {
    throw new Error(`Axios blocked: host "${url.hostname}" not allowed`);
  }
  return config;
});

// এখন থেকে সব জায়গায় axios এর বদলে safeAxios ব্যবহার করো
export { safeAxios };
