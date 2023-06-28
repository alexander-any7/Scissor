import React from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../auth";


const LoggedInHome = () => {
    return (
        <>
            <h1>DO SOMETHING FOR LOGGED IN USER</h1>
        </>
    )
}

const LoggedOutHome = () => {
    return (
        <>
            <h1>DO SOMETHING FOR LOGGED OUT USER</h1>
            <Link to='/register' className="btn btn-primary">Get Started</Link>
        </>
    )
}

const HomePage = () => {

    const [logged, session] = useAuth();

    return (
        <div className="home container mt-4">
            <h1>Welcome To Scissor</h1>
            {logged?<LoggedInHome/>:<LoggedOutHome/>}
        </div>
    )
}

export default HomePage;