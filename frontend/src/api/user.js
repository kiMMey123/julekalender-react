import {processApiRequest} from "@/api/api.js";

export async function getUserData() {
    return await processApiRequest("user/me", "GET", {}, true)
}