import React from "react";
import Card from 'react-bootstrap/Card';
import Button from 'react-bootstrap/Button';



const Url = ({ uuid, short_url, qr_code, clicks, long_url }) => {
    return (
        <div className="url">
            <Card style={{ width: '18rem' }} className="mb-5">
                <Card.Img variant="top" src={qr_code} />
                <Card.Body>
                    <Card.Title>{uuid }</Card.Title>
                    <Card.Text>
                        Clicks: {clicks}
                        <br></br>
                        Long Url: {long_url}
                    </Card.Text>
                    <Button variant="primary">See Details</Button>
                </Card.Body>
            </Card>
        </div>
    )
}

const DetailedUrl = ({ uuid, short_url, qr_code, clicks, long_url, updated_at, referrer }) => {
    return (
        <div className="detailed-url">
            <p>{short_url}</p>
            <p>{uuid}</p>
            <p>{qr_code}</p>
            <p>{clicks}</p>
            <p>{long_url}</p>
            <p>{updated_at}</p>
            <p>{referrer}</p>
        </div>
    )
}

export { Url, DetailedUrl }