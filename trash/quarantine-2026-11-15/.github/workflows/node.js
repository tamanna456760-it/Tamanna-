import http from "http";
import https from "https";
import { URL } from "url";

// শুধু এই host গুলোতে request যেতে পারবে
const ALLOWED_HOSTS = new Set([
  "api.my-internal-service.local",
  "internal-db.local",
  "127.0.0.1",
  "localhost"
]);

function isAllowedHost(options) {
  try {
    let hostname;

    if (typeof options === "string") {
      const url = new URL(options);
      hostname = url.hostname;
    } else if (options instanceof URL) {
      hostname = options.hostname;
    } else {
      hostname = options.hostname || options.host;
    }

    return ALLOWED_HOSTS.has(hostname);
  } catch {
    return false;
  }
}

// Original methods রেখে দিচ্ছি
const originalHttpRequest = http.request;
const originalHttpsRequest = https.request;

// http.request patch
http.request = function patchedHttpRequest(options, callback) {
  if (!isAllowedHost(options)) {
    throw new Error("Outbound HTTP blocked: host not allowed");
  }
  return originalHttpRequest.call(http, options, callback);
};

// https.request patch
https.request = function patchedHttpsRequest(options, callback) {
  if (!isAllowedHost(options)) {
    throw new Error("Outbound HTTPS blocked: host not allowed");
  }
  return originalHttpsRequest.call(https, options, callback);
};

console.log("🔒 Global outbound guard enabled (deny-all except allow-list)");
