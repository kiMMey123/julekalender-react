export function getUserToken() {
    try {
        const tokenData = localStorage.getItem('userToken')
        return JSON.parse(tokenData)
    } catch(e) {
        throw e
    }
}

export function setUserToken(tokenData) {
    localStorage.setItem('userToken', JSON.stringify(tokenData))
}