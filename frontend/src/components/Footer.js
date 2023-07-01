import React from 'react';

const Footer = () => {
    const currentYear = new Date().getFullYear();
    return (
        <>
            <br /><br /><br /><br /><br />
            <div class="text-md-center text-muted bg-primary fixed-bottom footer">
                <footer style={{ textAlign: 'center' }}>
                    <p class="text-light">
                        <small>
                            &copy; Alexander {currentYear}{" "}
                            | AltSchool Africa School of Engineering | Capstone Project - 2023
                        </small>
                    </p>
                </footer>
            </div>
        </>
    )
};

export default Footer;