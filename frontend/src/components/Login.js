import React from "react";
import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';
import { Link, useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { login } from "../auth";


const LoginPage = () => {
    const {
        register,
        handleSubmit,
        reset,
        formState: { errors },
    } = useForm();

    const navigate = useNavigate();

    const loginUser = (data) => {
        const body = {
            username_or_email: data.usernameOrEmail,
            password: data.password
        }
        const requestOptions = {
            method: "POST",
            headers: {
                "content-type": "application/json",
            },
            body: JSON.stringify(body)
        }
        fetch('/auth/login', requestOptions)
            .then(res => res.json())
            .then(data => {
                login(data)
                navigate('/')
            })
        reset()
    }

    return (
        <div className="login container mt-4">
            <div className="form">
                <h1 className="text-center">Login</h1>
                <form>
                    <Form.Group className="mb-3" controlId="LoginForm.UsernameOrEmail">
                        <Form.Label>Username or Email</Form.Label>
                        <Form.Control type="text"
                            placeholder="Your username or email"
                            {...register('usernameOrEmail', { required: true, maxLength: 50 })}
                        />
                        {errors.usernameOrEmail && <span className="text-danger">Password is required</span>}
                        <br></br>
                        {errors.usernameOrEmail?.type === "maxLength" && <span className="text-danger">Username or Email cannot be more than 50 characters</span>}
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
                    <Form.Group>
                        <div className="d-grid gap-2 mt-5">
                            <Button variant="primary" as="sub" onClick={handleSubmit(loginUser)}>
                                Login
                            </Button>
                        </div>
                    </Form.Group>
                    <Form.Group id="registerBlock" muted className="mt-3">
                        <small>Need an account? <Link to='/register'>Register</Link></small>
                    </Form.Group>

                </form>
            </div>
        </div>
    )
}

export default LoginPage;