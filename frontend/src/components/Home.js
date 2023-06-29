import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../auth";
import { Url, DetailedUrl } from "./Url";
import Container from 'react-bootstrap/Container';
import { useForm } from "react-hook-form";
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Modal from 'react-bootstrap/Modal';
import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';
import Alert from 'react-bootstrap/Alert';


const LoggedInHome = () => {
    const [urls, setUrls] = useState([]);
    const [urlUuid, setUrlUuid] = useState('')
    const navigate = useNavigate();
    const [show, setShow] = useState(false)
    const [showAlert, setShowAlert] = useState(false)
    const handleClose = () => setShow(false);
    const [serverResponse, setServerResponse] = useState('');
    const [updateResponse, setUpdateResponse] = useState('');
    const [alertVariant, setAlertVariant] = useState('');
    // url details
    const [urlTitle, setUrlTitle] = useState('');
    const [urlReferrer, setUrlReferrer] = useState('');
    const [urlUpdatedAt, setUrlUpdatedAt] = useState('');
    const [urlLongUrl, setUrlLongUrl] = useState('');
    const [urlClicks, setUrlClicks] = useState('')
    const [urlShortUrl, setUrlShortUrl] = useState('')
    const [urlHasQrCode, setUrlHasQrCode] = useState()
    const [urlCreatedAt, setUrlCreatedAt] = useState()


    const {
        register,
        handleSubmit,
        reset,
        setValue,
        formState: { errors },
    } = useForm();
    const tokens = JSON.parse(localStorage.getItem('REACT_TOKEN_AUTH_KEY'))
    const access_token = tokens.access_token

    const requestOptions = {
        method: "GET",
        headers: {
            "content-type": "application/json",
            "Authorization": `Bearer ${access_token}`
        },
    }

    useEffect(
        () => {
            fetch('/urls/all-urls', requestOptions)
                .then(res => res.json())
                .then(data => {
                    setUrls(data)
                })
                .catch(err => console.log(err))
        }, []
    );

    const getUserUrls = () => {
        fetch('/urls/all-urls', requestOptions)
            .then(res => res.json())
            .then(data => {
                setUrls(data)
            })
            .catch(err => console.log(err))
    }

    const handleShow = (uuid) => {
        setShow(true)
        setUrlUuid(uuid)
        urls.map(
            (url) => {
                if (url.uuid === uuid) {
                    setUrlTitle(url.title)
                    setUrlShortUrl(url.short_url)
                    setUrlClicks(url.clicks)
                    setUrlUpdatedAt(url.updated_at)
                    setUrlReferrer(url.referrer)
                    setUrlHasQrCode(url.has_qr_code)
                    setUrlCreatedAt(url.created_at)
                    setUrlLongUrl(url.long_url)
                    setValue('title', url.title)
                    setValue('url', url.long_url)
                }
            }
        )
    }

    const updateUrl = (data) => {
        const requestOptions = {
            method: "PUT",
            headers: {
                "content-type": "application/json",
                "Authorization": `Bearer ${access_token}`
            },
            body: JSON.stringify(data)
        };
        fetch(`/urls/${urlUuid}`, requestOptions)
            .then(res => res.json())
            .then(data => {
                if (data.message) {
                    console.log(data)
                    setUpdateResponse(data.message)
                    setAlertVariant('danger')
                    setShowAlert(true)
                    handleShow(urlUuid)
                }
                else {
                    window.location.reload()
                }
            })
            .catch(err => console.log(err))

        handleClose()
    }

    const generateQrCode = (uuid) => {
        const requestOptions = {
            method: "GET",
            headers: {
                "content-type": "application/json",
                "Authorization": `Bearer ${access_token}`
            },
        };
        fetch(`/urls/generate-qr-code/${uuid}`, requestOptions)
            .then(res => {
                if (res.status === 200) {

                }
            })
            .then(data => { })
            .catch(err => console.log(err))

    };

    const deleteURL = (uuid) => {
        const requestOptions = {
            method: "DELETE",
            headers: {
                "content-type": "application/json",
                "Authorization": `Bearer ${access_token}`
            },
        };
        fetch(`/urls/${uuid}`, requestOptions)
            .then(res => {
                if (res.status === 204) {
                    getUserUrls()
                    handleClose()
                }
            })
            .then(data => { })
            .catch(err => console.log(err))
    }

    try {
        return (
            <>
                <Modal show={show} onHide={handleClose} size='md'>
                    <Modal.Header closeButton>
                        <Modal.Title>{urlTitle}</Modal.Title>
                    </Modal.Header>
                    {showAlert ?
                        <>
                            <Alert variant={alertVariant} onClose={() => setShowAlert(false)} className="text-center" dismissible>
                                <p>
                                    {updateResponse}
                                </p>
                            </Alert>
                        </>
                        :
                        ''
                    }
                    <Modal.Body>
                        <DetailedUrl key={urlUuid}
                            uuid={urlUuid}
                            clicks={urlClicks}
                            updated_at={urlUpdatedAt}
                            long_url={urlLongUrl}
                            short_url={urlShortUrl}
                            has_qr_code={urlHasQrCode}
                            created_at={urlCreatedAt}
                            referrer={urlReferrer}
                        />
                        <form>
                            <h4 className="mt-5 text-center">Update Url</h4>
                            <Form.Group className="" controlId="shortenUrlForm.url">
                                <Form.Label>URL</Form.Label>
                                <Form.Control type="text"
                                    placeholder="https://www.example.com"
                                    {...register('url', { required: true, maxLength: 999 })}
                                />
                                {errors.url && <span className="text-danger">URL is required</span>}
                                <br></br>
                                {errors.url?.type === "maxLength" && <span className="text-danger">URL cannot be more than 999 characters</span>}
                            </Form.Group>
                            <Form.Group className="" controlId="shortenUrlForm.title">
                                <Form.Label>Title</Form.Label>
                                <Form.Control type="text"
                                    {...register('title', { required: true, maxLength: 20 })}
                                />
                                {errors.title && <span className="text-danger">Title is required</span>}
                                <br></br>
                                {errors.title?.type === "maxLength" && <span className="text-danger">Title cannot be more than 20 characters</span>}
                            </Form.Group>
                        </form>
                    </Modal.Body>
                    <Modal.Footer>
                        <Button variant="primary" onClick={handleSubmit(updateUrl)}>
                            Save Changes
                        </Button>

                        <Button variant="secondary" onClick={() => { generateQrCode(urlUuid) }}>
                            Generate QR Code
                        </Button>
                        <Button variant="danger" onClick={() => { deleteURL(urlUuid) }}>
                            Delete
                        </Button>
                    </Modal.Footer>
                </Modal>
                <h1>URLs Here</h1>
                <Container>
                    <Row>
                        {
                            urls.map(
                                (url) => (
                                    <Col key={url.uuid} md="auto">
                                        <div className="row" key={url.uuid}>
                                            <div className="col">
                                                <Url key={url.uuid} uuid={url.uuid} clicks={url.clicks} title={url.title} onClick={() => { handleShow(url.uuid) }} />
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
    } catch (errors) {
        navigate('/login')
    }
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