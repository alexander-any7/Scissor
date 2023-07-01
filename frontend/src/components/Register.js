import React, { useState } from "react";
import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';
import { Link } from "react-router-dom";
import { useForm } from "react-hook-form";
import Alert from 'react-bootstrap/Alert';


const RegisterPage = () => {

    const {
        register,
        handleSubmit,
        reset,
        formState: { errors },
    } = useForm();
    const [show, setShow] = useState(false)
    const [serverResponse, setServerResponse] = useState('')
    const [alertVariant, setAlertVariant] = useState('')

    const registerUser = (data) => {
        if (data.password === data.confirmPassword) {
            const body = {
                username: data.username,
                email: data.email,
                firstname: data.firstname,
                lastname: data.lastname,
                password: data.password,
                confirm_password: data.confirmPassword
            }
            const requestOptions = {
                method: "POST",
                headers: {
                    "content-type": "application/json",
                },
                body: JSON.stringify(body)
            }
            fetch('/auth/register', requestOptions)
                .then(res => res.json())
                .then(data => {
                    if (data.message) {
                        setServerResponse(data.message)
                        setAlertVariant('danger')
                        setShow(true)
                    }
                    else if (data.id) {
                        setServerResponse('User registered successfully')
                        setAlertVariant('success')
                        setShow(true)
                    }

                })
                .catch(err => console.log(err))
            reset()
        } else {
            alert('Passwords do not match!')
        }
    }

    return (
        <div className="register container mt-4">
            <div className="form">
                {show ?
                    <>
                        <h1 className="text-center">Register</h1>
                        <Alert variant={alertVariant} onClose={() => setShow(false)} dismissible>
                            <p>
                                {serverResponse}
                            </p>
                        </Alert>
                    </>
                    :
                    <h1 className="text-center">Register</h1>

                }
                <form>
                    <Form.Group className="mb-3" controlId="registerForm.Username">
                        <Form.Label>Username</Form.Label>
                        <Form.Control type="text"
                            {...register('username', { required: true, maxLength: 45 })}
                        />
                        {errors.username && <span className="text-danger">Username is required</span>}
                        <br></br>
                        {errors.username?.type === "maxLength" && <span className="text-danger">Username cannot be more than 45 characters</span>}
                    </Form.Group>

                    <Form.Group className="mb-3" controlId="registerForm.Email">
                        <Form.Label>Email address</Form.Label>
                        <Form.Control type="email"
                            placeholder="name@example.com"
                            {...register('email', { required: true, maxLength: 50 })}
                        />
                        {errors.email && <span className="text-danger">Email is required</span>}
                        <br></br>
                        {errors.email?.type === "maxLength" && <span className="text-danger">Email cannot be more than 50 characters</span>}
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
                    <Form.Group className="mb-3" controlId="registerForm.Password">
                        <Form.Label>Password</Form.Label>
                        <Form.Control type="password"
                            {...register('password', { required: true, minLength: 6 })}
                        />
                        {errors.password && <span className="text-danger">Password is required</span>}
                        <br></br>
                        {errors.password?.type === "minLength" && <span className="text-danger">Password cannot be less than 6 characters</span>}
                    </Form.Group>
                    <Form.Group className="mb-3" controlId="registerForm.ConfirmPassword">
                        <Form.Label>Confirm Password</Form.Label>
                        <Form.Control type="password"
                            {...register('confirmPassword', { required: true, minLength: 6 })}
                        />
                        {errors.confirmPassword && <span className="text-danger">Confirm Password is required</span>}
                        <br></br>
                        {errors.confirmPassword?.type === "minLength" && <span className="text-danger">Confirm Password cannot be less than 6 characters</span>}
                    </Form.Group>
                    <Form.Group>
                        <div className="d-grid gap-2 mt-5">
                            <Button variant="primary" as="sub" onClick={handleSubmit(registerUser)}>
                                Register
                            </Button>
                        </div>
                    </Form.Group>
                    <Form.Group id="registerBlock" muted className="mt-3">
                        <small>Already have an account? <Link to='/login'>Login</Link></small>
                    </Form.Group>
                </form>
            </div>

        </div>
    )
}

export default RegisterPage;