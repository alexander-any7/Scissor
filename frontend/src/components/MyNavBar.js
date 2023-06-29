import React from "react";
import Container from 'react-bootstrap/Container';
import Nav from 'react-bootstrap/Nav';
import Navbar from 'react-bootstrap/Navbar';
import { useAuth, logout } from "../auth";


const LoggedInLinks = () => {
  return (
    <>
      <Nav.Link href='/'>Home</Nav.Link>
      <Nav.Link href="#" onClick={() => { logout() }}>Logout</Nav.Link>
      <Nav.Link href='/shorten-url'>Shorten Url</Nav.Link>
      <Nav.Link href="/profile">My Profile</Nav.Link>
    </>
  )
}

const LoggedOutLinks = () => {
  return (
    <>
      <Nav.Link href="/register">Register</Nav.Link>
      <Nav.Link href="/login">Login</Nav.Link>
    </>
  )
}

const MyNavBar = () => {

  const [logged, session] = useAuth();

  return (
    <Navbar bg="primary" data-bs-theme="dark">
      <Container>
        <Navbar.Brand href="/">Scissor</Navbar.Brand>
        <Nav className="me-auto">
        {logged?<LoggedInLinks/>:<LoggedOutLinks/>}
        </Nav>
      </Container>
    </Navbar>
  )
}

export default MyNavBar;