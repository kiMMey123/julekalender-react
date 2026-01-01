// 'use client'

import {useEffect, useState} from 'react'
import { BrowserRouter } from 'react-router-dom';
import {AbsoluteCenter} from "@chakra-ui/react";
import {processApiRequest} from "./api/api.js";
import { fetchImage} from "./api/media.js";
import LoginForm from "./views/login/LoginForm.jsx";
import {ColorModeButton} from "@/components/ui/color-mode.jsx";
import {getToken} from "@/api/login.js";
import {setUserToken} from "@/utils/token.js";
import {getUserData} from "@/api/user.js";

// import './App.css'


function App() {
    const [time, setTime] = useState(null)
    const [user, setUser] = useState(null)


    async function getTime() {
        const data = await processApiRequest('time', 'GET')
        setTime(data.time)
    }

    async function loginUser(formData) {
        try {
            await getToken(formData).then((data) => {
                setUserToken(data)
                getUserData().then((data) => {setUser(data)})
            })
        } catch(e) {
            console.log(e)
        }
    }

    useEffect(() => {
        setTime(getTime())
    }, [])

    return (
        <BrowserRouter>
            <ColorModeButton />
            <div className="App">
                { user ? (
                    <AbsoluteCenter axis={"horizontal"}>
                        <div>
                            <p>Benus aaa {time}</p>

                        </div>

                    </AbsoluteCenter>
                ) : (
                    <LoginForm
                        handleSubmit={loginUser}
                    />
                )}
            </div>
        </BrowserRouter>
    )
}

export default App
