import dotenv from "dotenv"
import postgres from "postgres";
import { drizzle } from "drizzle-orm/postgres-js";
import {schema} from "./schema";

dotenv.config()

if (!process.env.PSQL_URL){
    throw new Error("Postgres URL couldn't find")
}

const client = postgres(process.env.PSQL_URL)
export const db = drizzle(client, {
    schema: schema
})