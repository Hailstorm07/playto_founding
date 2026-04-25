import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../../api';
import { ChevronLeft, FileText, Check, X, Info, ExternalLink } from 'lucide-react';

const SubmissionDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [submission, setSubmission] = useState(null);
  const [loading, setLoading] = useState(true);
  const [reason, setReason] = useState('');
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    fetchSubmission();
  }, [id]);

  const fetchSubmission = async () => {
    try {
      const response = await api.get(`submissions/${id}/`);
      setSubmission(response.data);
      
      // Automatically move to under_review if currently submitted
      if (response.data.status === 'submitted') {
        await api.post(`submissions/${id}/start_review/`);
        // Refresh to show updated status
        const updated = await api.get(`submissions/${id}/`);
        setSubmission(updated.data);
      }
    } catch (err) {
      console.error('Failed to fetch submission', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAction = async (status) => {
    if (['rejected', 'more_info_requested'].includes(status) && !reason) {
      alert('Please provide a reason');
      return;
    }

    setActionLoading(true);
    try {
      await api.post(`submissions/${id}/review_action/`, { status, reason });
      navigate('/reviewer/dashboard');
    } catch (err) {
      alert(err.response?.data?.error || 'Action failed');
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) return <div className="text-center mt-20">Loading details...</div>;
  if (!submission) return <div className="text-center mt-20">Submission not found</div>;

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <button 
        onClick={() => navigate('/reviewer/dashboard')}
        className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4"
      >
        <ChevronLeft size={20} /> Back to Queue
      </button>

      <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
        <div className="p-6 border-b flex justify-between items-center bg-gray-50">
          <div>
            <h2 className="text-2xl font-bold">{submission.merchant_name}</h2>
            <p className="text-sm text-gray-500">Submission ID: {submission.id} | Assigned to: {submission.assigned_reviewer_name || 'Unassigned'}</p>
          </div>
          <span className={`px-4 py-1.5 rounded-full text-sm font-bold capitalize ${
            submission.status === 'approved' ? 'bg-green-100 text-green-700' :
            submission.status === 'rejected' ? 'bg-red-100 text-red-700' :
            'bg-amber-100 text-amber-700'
          }`}>
            {submission.status.replace('_', ' ')}
          </span>
        </div>

        <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Details Section */}
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-bold mb-3 border-b pb-1">Personal Details</h3>
              <div className="space-y-2">
                <p><span className="text-gray-500">Full Name:</span> {submission.full_name || <span className="text-gray-400 italic">Not provided</span>}</p>
                <p><span className="text-gray-500">Email:</span> {submission.email || <span className="text-gray-400 italic">Not provided</span>}</p>
                <p><span className="text-gray-500">Phone:</span> {submission.phone || <span className="text-gray-400 italic">Not provided</span>}</p>
              </div>
            </div>

            <div>
              <h3 className="text-lg font-bold mb-3 border-b pb-1">Business Details</h3>
              <div className="space-y-2">
                <p><span className="text-gray-500">Business Name:</span> {submission.business_name || <span className="text-gray-400 italic">Not provided</span>}</p>
                <p><span className="text-gray-500">Type:</span> {submission.business_type || <span className="text-gray-400 italic">Not provided</span>}</p>
                <p><span className="text-gray-500">Monthly Volume:</span> {submission.expected_monthly_volume ? `$${submission.expected_monthly_volume}` : <span className="text-gray-400 italic">Not provided</span>}</p>
              </div>
            </div>
          </div>

          {/* Documents Section */}
          <div>
            <h3 className="text-lg font-bold mb-3 border-b pb-1">Documents</h3>
            <div className="space-y-3">
              {submission.documents.map((doc) => (
                <div key={doc.id} className="p-3 border rounded-lg flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <FileText className="text-gray-400" size={24} />
                    <div>
                      <p className="text-sm font-medium">{doc.document_type}</p>
                      <p className="text-xs text-gray-400">{new Date(doc.uploaded_at).toLocaleDateString()}</p>
                    </div>
                  </div>
                  <a 
                    href={`http://127.0.0.1:8000${doc.file}`} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-indigo-600 hover:text-indigo-900 flex items-center gap-1 text-sm font-medium"
                  >
                    View <ExternalLink size={14} />
                  </a>
                </div>
              ))}
              {submission.documents.length === 0 && (
                <p className="text-sm text-gray-500">No documents uploaded</p>
              )}
            </div>
          </div>
        </div>

        {/* Action Section */}
        {['under_review', 'more_info_requested'].includes(submission.status) && (
          <div className="p-6 bg-gray-50 border-t">
            <h3 className="text-lg font-bold mb-4">Take Action</h3>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Reason (Required for Rejection or More Info)
              </label>
              <textarea 
                className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
                rows="3"
                placeholder="Explain the decision..."
                value={reason}
                onChange={(e) => setReason(e.target.value)}
              ></textarea>
            </div>
            <div className="flex flex-wrap gap-4">
              <button 
                onClick={() => handleAction('approved')}
                disabled={actionLoading}
                className="flex-1 bg-green-600 text-white py-2.5 rounded-lg hover:bg-green-700 transition flex items-center justify-center gap-2 font-bold"
              >
                <Check size={20} /> Approve
              </button>
              <button 
                onClick={() => handleAction('rejected')}
                disabled={actionLoading}
                className="flex-1 bg-red-600 text-white py-2.5 rounded-lg hover:bg-red-700 transition flex items-center justify-center gap-2 font-bold"
              >
                <X size={20} /> Reject
              </button>
              <button 
                onClick={() => handleAction('more_info_requested')}
                disabled={actionLoading}
                className="flex-1 bg-amber-500 text-white py-2.5 rounded-lg hover:bg-amber-600 transition flex items-center justify-center gap-2 font-bold"
              >
                <Info size={20} /> Request More Info
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SubmissionDetail;
