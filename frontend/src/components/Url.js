import React, { useState } from "react";
import Card from 'react-bootstrap/Card';
import Button from 'react-bootstrap/Button';
import Collapse from 'react-bootstrap/Collapse';
import ListGroup from 'react-bootstrap/ListGroup';
import Badge from 'react-bootstrap/Badge';


const Url = ({ title, clicks, onClick }) => {
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

const Referrer = ({ referrer }) => {
  return (
    <div className="mt-3">
      {Object.entries(referrer)
        .sort(([, a], [, b]) => b - a)
        .map(([key, value]) => (
        <>
          <ListGroup as="ul" key={key}>
            <ListGroup.Item
              as="li"
              className="d-flex justify-content-between align-items-start"
            >
              <div className="ms-2 me-auto">
                {key}
              </div>
              <Badge bg="secondary" pill>
                {value}
              </Badge>
            </ListGroup.Item>
          </ListGroup>
        </>
      ))}
    </div>
  );
};

const DetailedUrl = ({ uuid, short_url, clicks, long_url, updated_at, referrer, has_qr_code, created_at }) => {
  const [open, setOpen] = useState(false);

  return (
    <div className="detailed-url">
      {has_qr_code && <img src={`/qr_codes/${uuid}_qrcode.png`} className="d-block mx-auto" thumbnail />}
      <ListGroup as="ul">
        <ListGroup.Item as="li"><span className="fw-semibold">Short Url:</span> {short_url}</ListGroup.Item>
        <ListGroup.Item as="li"><span className="fw-semibold">Long URL:</span> {long_url}</ListGroup.Item>
        <ListGroup.Item as="li"><span className="fw-semibold">Created At:</span> {created_at}</ListGroup.Item>
        <ListGroup.Item as="li"><span className="fw-semibold">Updated At:</span> {updated_at}</ListGroup.Item>
      </ListGroup>
      <br></br>
      <ListGroup as="ul">

      <ListGroup.Item as="li" action active
        onClick={() => setOpen(!open)}
        aria-controls="example-collapse-text"
        aria-expanded={open}
        >
        Clicks Origins
      </ListGroup.Item>
      </ListGroup>
      <Collapse in={open}>
        <div id="example-collapse-text">
          <Referrer referrer={referrer} />
        </div>
      </Collapse>
    </div>
  )
}



export { Url, DetailedUrl }