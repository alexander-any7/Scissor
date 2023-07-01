import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth, logout } from "../auth";
import { Url, DetailedUrl } from "./Url";
import Container from 'react-bootstrap/Container';
import { useForm } from "react-hook-form";
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Modal from 'react-bootstrap/Modal';
import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';
import Alert from 'react-bootstrap/Alert';
import Image from 'react-bootstrap/Image';
import Footer from "./Footer";


const LoggedInHome = () => {
    const [urls, setUrls] = useState([]);
    const [urlUuid, setUrlUuid] = useState('')
    const navigate = useNavigate();
    const [show, setShow] = useState(false)
    const [showAlert, setShowAlert] = useState(false)
    const handleClose = () => setShow(false);
    const [updateResponse, setUpdateResponse] = useState('');
    const [alertVariant, setAlertVariant] = useState('');
    const [fullscreen, setFullscreen] = useState(true);
    const [confirmDeleteShow, setConfirmDeleteShow] = useState(false);
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
        }
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
                    const reload = window.location.reload()
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
                    setConfirmDeleteShow(false);

                }
            })
            .then(data => { })
            .catch(err => console.log(err))
    }

    const cancelConfirmDelete = () => {
        setConfirmDeleteShow(false)
    }

    const confirmDelete = () => {
        setFullscreen('sm-down');
        handleClose()
        setConfirmDeleteShow(true);
    }

    try {
        return (
            <>
                <h1 className="text-center">Welcome To Scissor</h1>
                <Modal show={confirmDeleteShow} fullscreen={fullscreen} onHide={() => setConfirmDeleteShow(false)}>
                    <Modal.Header closeButton>
                        <Modal.Title>Confirm URL Delete</Modal.Title>
                    </Modal.Header>
                    <Modal.Body> Are you sure you want to delete <span className="fw-bold">{urlTitle}</span></Modal.Body>
                    <Modal.Footer>
                        <Button variant="secondary" onClick={cancelConfirmDelete}>
                            Cancel
                        </Button>
                        <Button variant="danger" onClick={() => { deleteURL(urlUuid) }}>
                            Delete
                        </Button>
                    </Modal.Footer>
                </Modal>
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

                        {!urlHasQrCode && <Button variant="secondary" onClick={() => { generateQrCode(urlUuid) }}>
                            Generate QR Code
                        </Button>}
                        <Button variant="danger" onClick={confirmDelete}>
                            Delete
                        </Button>
                    </Modal.Footer>
                </Modal>
                <h4 className="text-center">You have {urls.length} URLs</h4>
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
        logout()
    }
}

const LoggedOutHome = () => {
    return (
        <>
            <h1 className="text-center mb-5">Welcome To Scissor</h1>
            <Container>
                <Row className="mb-5">
                    <div className="d-flex align-items-center">
                        <Col>
                            <p className="text-center fst-italic">
                                Scissor is the URL shortener app that does it all.
                                Create, customize, and track your links with Scissor.
                                Scissor helps you shorten your URLs, generate QR codes, and get analytics on your clicks.
                                Scissor is the best way to optimize your online marketing and grow your business.
                            </p>
                            <div className="text-center">
                                <Link to='/register' className="btn btn-primary">Get Started</Link>
                            </div>
                        </Col>
                        <Col><Image src="home_images/no_domain.png" rounded fluid /></Col>
                    </div>
                </Row>

                <Row className="mb-5">
                    <div className="d-flex align-items-center">
                        <Col>
                            <Image src="home_images/shorten.png" rounded fluid />
                        </Col>
                        <Col>
                            <p className="text-center fst-italic">
                                Scissor makes it easy to create a QR code for your shortened URL, so you can share it with your offline audience.
                                Scissor generates a scannable code for your link and displays it next to the link, so you can download it or print it with one click.
                                Scissor helps you connect your online and offline marketing and reach more customers.
                            </p>
                        </Col>
                    </div>
                </Row>
                <Row className="mb-5">
                    <div className="d-flex align-items-center">

                        <Col>
                            <p className="text-center fst-italic">With Scissor, you can not only shorten your long URLs, but also track where your clicks are coming from.
                                Scissor provides you with detailed analytics of the clicks, so you can optimize your marketing campaigns and reach your target audience.
                                Scissor helps you cut through the noise and get insights on your online performance.
                            </p></Col>
                        <Col><Image src="home_images/clicks.png" rounded fluid /></Col>
                    </div>
                </Row>
                <Row className="mb-5">
                    <div className="d-flex align-items-center">

                        <Col><Image src="home_images/custom_domain.png" rounded fluid /></Col>
                        <Col>
                            <p className="text-center fst-italic">
                                Scissor lets you customize your shortened URLs with your own domain name, so you can build your brand and increase your trust.
                                Whether you want to use your company name, your product name, or your slogan, Scissor allows you to create memorable and professional links that suit your business.
                                Scissor helps you stand out from the crowd and grow your online presence.
                            </p>
                        </Col>
                    </div>

                </Row>
                <Row className="mb-5">
                    <div className="d-flex align-items-center">

                        <Col>
                            <p className="text-center fst-italic">
                                Scissor gives you the flexibility to update your shortened URLs anytime, without changing the link.
                                Whether you want to redirect your visitors to a different page or fix a typo, Scissor allows you to edit your destination URL and keep your link intact.
                                Scissor helps you avoid broken links and maintain your online reputation.
                            </p>
                        </Col>
                        <Col><Image src="home_images/update.png" rounded fluid /></Col>
                    </div>
                </Row>
            </Container>
            <Footer />
        </>
    )
}

const HomePage = () => {
    const [logged] = useAuth();


    return (
        <div className="home container mt-4">
            {logged ? <LoggedInHome /> : <LoggedOutHome />}
        </div>
    )
}

export default HomePage;