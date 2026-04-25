import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/Auth/Login';
import Signup from './components/Auth/Signup';
import KYCForm from './components/Merchant/KYCForm';
import Dashboard from './components/Reviewer/Dashboard';
import SubmissionDetail from './components/Reviewer/SubmissionDetail';

const PrivateRoute = ({ children, role }) => {
  const token = localStorage.getItem('token');
  const userRole = localStorage.getItem('role');

  if (!token) {
    return <Navigate to="/login" />;
  }

  if (role && userRole !== role) {
    return <Navigate to="/" />;
  }

  return children;
};

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <nav className="bg-white shadow-sm py-4 px-8 flex justify-between items-center">
          <h1 className="text-xl font-bold text-indigo-600">Playto Pay</h1>
          <button 
            onClick={() => {
              localStorage.clear();
              window.location.href = '/login';
            }}
            className="text-gray-600 hover:text-gray-900"
          >
            Logout
          </button>
        </nav>
        <main className="container mx-auto py-8 px-4">
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
            
            <Route 
              path="/merchant/kyc" 
              element={
                <PrivateRoute role="merchant">
                  <KYCForm />
                </PrivateRoute>
              } 
            />
            
            <Route 
              path="/reviewer/dashboard" 
              element={
                <PrivateRoute role="reviewer">
                  <Dashboard />
                </PrivateRoute>
              } 
            />
            
            <Route 
              path="/reviewer/submission/:id" 
              element={
                <PrivateRoute role="reviewer">
                  <SubmissionDetail />
                </PrivateRoute>
              } 
            />

            <Route path="/" element={<Navigate to="/login" />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
