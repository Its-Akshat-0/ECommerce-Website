import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import { GoogleLogin } from '@react-oauth/google';
import { useAuth } from '../context/AuthContext';
import { toast } from 'react-toastify';

const Login = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const { login } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const res = await axios.post('http://localhost:8000/login', { email, password });
            login(res.data);
            toast.success("Successfully logged in!");
        } catch (error) {
            toast.error(error.response?.data?.detail || "Login failed");
        }
    };

    const handleGoogleSuccess = async (credentialResponse) => {
        try {
            const res = await axios.post('http://localhost:8000/google-login', {
                token: credentialResponse.credential
            });
            login(res.data);
            toast.success("Logged in with Google!");
        } catch (error) {
            toast.error(error.response?.data?.detail || "Google Login failed");
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-100 px-4">
            <div className="bg-white p-8 rounded-lg shadow-lg w-full max-w-md">
                <h2 className="text-3xl font-bold mb-6 text-center text-gray-800">Login</h2>
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-gray-700 font-semibold mb-2">Email</label>
                        <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} 
                            className="w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" 
                            placeholder="Enter your email" />
                    </div>
                    <div>
                        <label className="block text-gray-700 font-semibold mb-2">Password</label>
                        <input type="password" required value={password} onChange={(e) => setPassword(e.target.value)} 
                            className="w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" 
                            placeholder="Enter your password" />
                    </div>
                    <button type="submit" className="w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700 transition">
                        Sign In
                    </button>
                </form>
                <div className="my-6 flex items-center justify-center">
                    <span className="w-full border-b border-gray-300"></span>
                    <span className="px-4 text-gray-500">OR</span>
                    <span className="w-full border-b border-gray-300"></span>
                </div>
                <div className="flex justify-center flex-col items-center gap-4">
                    <GoogleLogin
                        onSuccess={handleGoogleSuccess}
                        onError={() => toast.error("Google Login Failed")}
                    />
                    <p className="text-gray-600 mt-4">
                        Don't have an account? <Link to="/register" className="text-blue-500 font-semibold hover:underline">Register</Link>
                    </p>
                </div>
            </div>
        </div>
    );
};

export default Login;
