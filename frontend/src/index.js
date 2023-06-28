import React from 'react';
import './styles/main.css'
import ReactDOM from 'react-dom/client';
import 'bootstrap/dist/css/bootstrap.min.css';
import MyNavBar from './components/MyNavBar';
import {
    BrowserRouter as Router,
    Routes,
    Route
} from 'react-router-dom'
import HomePage from './components/Home';
import RegisterPage from './components/Register';
import LoginPage from './components/Login';

const App = () => {
    return (

        <Router>
            <MyNavBar />
            <Routes>
                <Route path='/login' element={<LoginPage />} />
                <Route path='/register' element={<RegisterPage />} />
                <Route path='/' element={<HomePage />} />
            </Routes>
        </Router>

    )
}


const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);