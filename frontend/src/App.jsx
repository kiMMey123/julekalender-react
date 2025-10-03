// 'use client'

import {useEffect, useState} from 'react'
import { BrowserRouter } from 'react-router-dom';
import {AbsoluteCenter} from "@chakra-ui/react";
import {processApiRequest} from "./api/api.js";
import { fetchImage} from "./api/media.js";
import LoginForm from "./views/login/LoginForm.jsx";
import {ColorModeButton} from "@/components/ui/color-mode.jsx";
import {getToken} from "@/api/login.js";

// import './App.css'


function App() {
    const [time, setTime] = useState(null)
    const [img, setImg] = useState(null)
    const [user, setUser] = useState(null)
    const [token, setToken] = useState(null)


    async function getTime() {
        const data = await processApiRequest('time', 'GET')

        setTime(data.time)
    }

    async function loginUser(formData) {
        try {
            await getToken(formData).then((data) => {
                setToken(data)
            })
        } catch(e) {
            console.log(e)
        }
    }



    useEffect(() => {
        setTime(getTime())
        fetchImage("3beab014-33b1-460b-920c-c278466eb321.png").then((res) => {setImg(res)})
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
                        <div>
                            <img src={img}  alt={"benus"}/>

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
