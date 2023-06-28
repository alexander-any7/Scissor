import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../auth";
import { Url } from "./Url";
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';



const LoggedInHome = () => {
    const [urls, setUrls] = useState([]);


    const requestOptions = {
        method: "GET",
        headers: {
            "content-type": "application/json",
        },
    }

    useEffect(
        () => {
            fetch('/urls/all-urls')
                .then(res => res.json())
                .then(data => {
                    console.log(data)
                    setUrls(data)
                })
                .catch(err => console.log(err))
        }, []
    );

    return (
        <>
            <h1>URLs Here</h1>
            <Container>
                <Row>
                    {
                        urls.map(
                            (url) => (
                                <Col key={url.uuid}>
                                    <div className="row" key={url.uuid}>
                                        <div className="col">
                                            <Url key={url.uuid} short_url={url.short_url} uuid={url.uuid} qr_code={url.qr_code} clicks={url.clicks} long_url={url.long_url} />
                                        </div>
                                    </div>
                                </Col>
                            )
                        )
                    }
                </Row>
            </Container>


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
            {logged ? <LoggedInHome /> : <LoggedOutHome />}
        </div>
    )
}

export default HomePage;