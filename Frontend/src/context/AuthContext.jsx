import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { jwtDecode } from 'jwt-decode';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(localStorage.getItem('access_token') || null);
    const navigate = useNavigate();

    useEffect(() => {
        if (token) {
            try {
                const decoded = jwtDecode(token);
                // check if expired
                if (decoded.exp * 1000 < Date.now()) {
                    logout();
                } else {
                    setUser({ email: decoded.sub, name: decoded.name });
                    localStorage.setItem('access_token', token);
                    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
                }
            } catch (error) {
                logout();
            }
        }
    }, [token]);

    const login = (data) => {
        setToken(data.access_token);
        navigate('/');
    };

    const logout = () => {
        setUser(null);
        setToken(null);
        localStorage.removeItem('access_token');
        delete axios.defaults.headers.common['Authorization'];
        navigate('/login');
    };

    return (
        <AuthContext.Provider value={{ user, token, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
