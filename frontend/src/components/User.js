import React, { useEffect, useState } from "react";
import Card from 'react-bootstrap/Card';
import Button from 'react-bootstrap/Button';
import Modal from 'react-bootstrap/Modal';
import Form from 'react-bootstrap/Form';
import Alert from 'react-bootstrap/Alert';
import { useForm } from "react-hook-form";



const UserProfile = () => {

    const [userDetails, setUserDetails] = useState('');
    const [show, setShow] = useState(false);
    const handleClose = () => setShow(false);
    const [alertVariant, setAlertVariant] = useState('');
    const [showErrorAlert, setShowErrorAlert] = useState(false);
    const [showAlert, setShowAlert] = useState(false);
    const [updateResponse, setUpdateResponse] = useState('');



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
            fetch('/users/profile', requestOptions)
                .then(res => res.json())
                .then(data => {
                    console.log(data)
                    setUserDetails(data)
                })
                .catch(err => console.log(err))
        }, []
    );

    const updateProfile = (data) => {
        const body = {
            firstname: data.firstname,
            lastname: data.lastname,
            remove_custom_domain: data.removeCustomDomain,
            custom_domain: data.customDomain
        }
        const requestOptions = {
            method: "PUT",
            headers: {
                "content-type": "application/json",
                "Authorization": `Bearer ${access_token}`
            },
            body: JSON.stringify(body)
        };
        fetch('/users/update-profile', requestOptions)
            .then(res => res.json())
            .then(data => {
                try {
                    if (data.message) {
                        setAlertVariant('danger')
                        setShowErrorAlert(true)
                        setUpdateResponse(data.message)
                    }
                } catch { }
                if (data.username) {
                    setUserDetails(data)
                    handleClose()
                }
            })
    }

    const handleShow = () => {
        setShow(true)
        setValue('customDomain', userDetails.custom_domain)
        setValue('firstname', userDetails.firstname)
        setValue('lastname', userDetails.lastname)

    };

    return (
        <div className="container">
            <Modal
                show={show}
                onHide={handleClose}
                backdrop="static"
                keyboard={true}
            >
                <Modal.Header closeButton>
                    <Modal.Title>Update Profile</Modal.Title>
                </Modal.Header>
                {showErrorAlert ?
                    <>
                        <Alert variant={alertVariant} onClose={() => setShowErrorAlert(false)} className="text-center" dismissible>
                            <p>
                                {updateResponse}
                            </p>
                        </Alert>
                    </>
                    :
                    ''
                }
                <Modal.Body>
                    <form>
                        <Form.Group className="" controlId="updateProfileForm.customDomain">
                            <Form.Label>Custom Domain</Form.Label>
                            <Form.Control type="text"
                                {...register('customDomain', { maxLength: 200 })}
                            />
                            {errors.customDomain?.type === "maxLength" && <span className="text-danger">Custom Domain cannot be more than 200 characters</span>}
                        </Form.Group>
                        <Form.Group className="mb-3" controlId="registerForm.FirstName">
                            <Form.Label>First Name</Form.Label>
                            <Form.Control type="text"
                                {...register('firstname', { maxLength: 45 })}
                            />
                            {errors.firstname?.type === "maxLength" && <span className="text-danger">First Name cannot be more than 45 characters</span>}
                        </Form.Group>
                        <Form.Group className="mb-3" controlId="registerForm.LastName">
                            <Form.Label>Last Name</Form.Label>
                            <Form.Control type="text"
                                {...register('lastname', { maxLength: 45 })}
                            />
                            {errors.lastname?.type === "maxLength" && <span className="text-danger">Last Name cannot be more than 45 characters</span>}
                        </Form.Group>
                        {userDetails.custom_domain && <Form.Group>
                            <Form.Check // prettier-ignore
                                type="switch"
                                id="updateProfileForm.removeCustomDomain"
                                label="Remove Custom Domain"
                                {...register('removeCustomDomain')}
                            />
                        </Form.Group>}
                    </form>
                </Modal.Body>
                <Modal.Footer>
                    <Button variant="secondary" onClick={handleClose}>
                        Close
                    </Button>
                    <Button variant="primary" onClick={handleSubmit(updateProfile)}>Save Changes</Button>
                </Modal.Footer>
            </Modal>
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
            <h1>My Profile</h1>
            {userDetails.email && <p>Email: {userDetails.email}</p>}
            {userDetails.username && <p>Username: {userDetails.username}</p>}
            {userDetails.firstname && <p>FirstName: {userDetails.firstname}</p>}
            {userDetails.lastname && <p>LastName: {userDetails.lastname}</p>}
            {userDetails.custom_domain && <p>Custom Domain: {userDetails.custom_domain}</p>}
            <Button variant="primary" as="sub" onClick={handleShow}>
                Update Profile
            </Button>
        </div>
    )
}

export default UserProfile