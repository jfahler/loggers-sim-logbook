import { SQLDatabase } from "encore.dev/storage/sqldb";

export const logbookDB = new SQLDatabase("logbook", {
  migrations: "./migrations",
});
