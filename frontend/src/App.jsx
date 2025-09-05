import {useEffect, useState} from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

function App() {
    const [time, setTime] = useState(null)

    async function getTime() {
        const response = await fetch("http://localhost:8000/time/")
        const data = await response.json()
        setTime(data.time)
    }

    useEffect(() => {

        setTimeout(getTime, 60 * 1000)
    })
    return (
        <div className="App">
            <header className="App-header">time is {time}</header>
        </div>
    )
}

export default App
