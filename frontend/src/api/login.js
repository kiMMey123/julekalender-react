import { baseUrl } from "./api.js";

export async function getToken( user ) {
    const { username, password } = user;
    const formData = new URLSearchParams();
    formData.append('grant_type', 'password');
    formData.append('username', username);
    formData.append('password', password);
    formData.append('scope', '');
    formData.append('client_id', '');
    formData.append('client_secret', '');

    try {
        const response = await fetch('http://localhost:8000/token', {
            method: 'POST',
            headers: {
                'accept': 'application/json',
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: formData
        });

        return  await response.json();
    } catch (error) {
        console.error('Error:', error);
    }
}