export const baseUrl = 'http://localhost:8000'

export async function processApiRequest(endpoint, method, args) {
    const uri = `${baseUrl}/${endpoint}`;

    let urlWithParams = uri;
    let fetchOptions = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        },
    };

    if (method === 'GET') {
        const queryParams = new URLSearchParams(args).toString();
        urlWithParams = queryParams ? `${uri}?${queryParams}` : uri;
    } else {
        fetchOptions.body = JSON.stringify(args);
    }

    const response = await fetch(urlWithParams, fetchOptions);

    if (!response.ok) {
        const errorMsg = await response.json();
        const errorMessage = errorMsg.error || 'generic_error';
        throw new Error(errorMessage);
    }
    if (method === "DEL") {
        return
    }

    return await response.json();
}
