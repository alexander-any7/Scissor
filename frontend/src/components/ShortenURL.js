import React, { useState } from "react";
import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';
import { useForm } from "react-hook-form";
import Alert from 'react-bootstrap/Alert';

const ShortenUrl = () => {
    const {
        register,
        handleSubmit,
        reset,
        formState: { errors },
    } = useForm();

    const [show, setShow] = useState(false)
    const [serverResponse, setServerResponse] = useState('')
    const [alertVariant, setAlertVariant] = useState('')

    const shortenUrl = (data) => {
        const tokens = JSON.parse(localStorage.getItem('REACT_TOKEN_AUTH_KEY'))
        const access_token = tokens.access_token
        const requestOptions = {
            method: "POST",
            headers: {
                "content-type": "application/json",
                "Authorization": `Bearer ${access_token}`
            },
            body: JSON.stringify(data)
        }
        fetch('/urls/shorten-url', requestOptions)
            .then(res => res.json())
            .then(data => {
                if (data.message) {
                    setServerResponse(data.message)
                    setAlertVariant('danger')
                    setShow(true)
                }
                else if (data.uuid) {
                    setServerResponse('Operation Success')
                    setAlertVariant('success')
                    setShow(true)
                }
            })
            .catch(err => console.log(err))


        reset()
    }

    return (
        <div className="shorten-url container">
            {show ?
                <>
                    <h3 className="mt-5 text-center">Shorten a URL</h3>
                    <Alert variant={alertVariant} onClose={() => setShow(false)} dismissible>
                        <p>
                            {serverResponse}
                        </p>
                    </Alert>
                </>
                :
                <h3 className="mt-5 text-center">Shorten a URL</h3>

            }
            <form>
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
                <Form.Group>
                    <div className="">
                        <Button variant="primary" as="sub" onClick={handleSubmit(shortenUrl)}>
                            Shorten
                        </Button>
                    </div>
                </Form.Group>
            </form>
        </div>
    )
}

export default ShortenUrl