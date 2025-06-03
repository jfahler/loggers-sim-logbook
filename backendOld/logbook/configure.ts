import { api } from "encore.dev";

console.log("✅ configure.ts loaded by Encore"); // ← This is the key log

api.configure(() => ({
  cors: {
    allowOrigin: ["http://localhost:5173"],
    allowMethods: ["GET", "POST", "OPTIONS"],
    allowHeaders: ["Content-Type", "Authorization"],
    allowCredentials: true,
  },
  bodyParser: {
    jsonLimit: "50mb",
  },
}));
