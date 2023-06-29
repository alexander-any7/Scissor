import React from "react";
import Card from 'react-bootstrap/Card';
import Button from 'react-bootstrap/Button';



const Url = ({title, clicks, onClick }) => {
    return (
        <div className="url">
            <Card style={{ width: '18rem' }} className="mb-5">
                <Card.Body>
                    <Card.Title>{title}</Card.Title>
                    <Card.Text>
                        Clicks: {clicks}
                    </Card.Text>
                    <Button variant="primary" onClick={onClick}>See Details</Button>
                </Card.Body>
            </Card>
        </div>
    )
}

const Referrer = (referrer) => {
    // const myObject = JSON.parse(referrer);
    const myObject = referrer;
    return (
      <>
        {Object.entries(myObject).map(([key, value]) => (
          <p key={key}>
            {key}: {value}
          </p>
        ))}
      </>
    );
  };

const DetailedUrl = ({ uuid, short_url, clicks, long_url, updated_at, referrer, has_qr_code, created_at }) => {
    
    return (
        <div className="detailed-url">
            {has_qr_code  &&  <img src={`/qr_codes/${uuid}_qrcode.png`}  className="d-block mx-auto"/>}
            <p>Short URL: {short_url}</p>
            <p>Long URL: {long_url}</p>
            <p>Clicks: {clicks}</p>
            <p>Created At: {created_at}</p>
            <p>Updated At: {updated_at}</p>
            <Referrer referrer={ referrer} />
        </div>
    )
}

  

export { Url, DetailedUrl }