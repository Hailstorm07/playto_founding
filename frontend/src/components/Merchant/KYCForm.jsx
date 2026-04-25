import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import api from '../../api';
import { Upload, CheckCircle, Clock, AlertCircle } from 'lucide-react';

const KYCForm = () => {
  const [step, setStep] = useState(1);
  const [submission, setSubmission] = useState(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState(null);

  const { register, handleSubmit, setValue, watch, formState: { errors } } = useForm();

  useEffect(() => {
    fetchSubmission();
  }, []);

  const fetchSubmission = async () => {
    try {
      const response = await api.get('submissions/');
      if (response.data.length > 0) {
        const sub = response.data[0];
        setSubmission(sub);
        // Pre-fill form
        setValue('full_name', sub.full_name);
        setValue('email', sub.email);
        setValue('phone', sub.phone);
        setValue('business_name', sub.business_name);
        setValue('business_type', sub.business_type);
        setValue('expected_monthly_volume', sub.expected_monthly_volume);
      }
    } catch (err) {
      console.error('Failed to fetch submission', err);
    } finally {
      setLoading(false);
    }
  };

  const saveProgress = async (data) => {
    try {
      if (submission) {
        const response = await api.patch(`submissions/${submission.id}/`, data);
        setSubmission(response.data);
      } else {
        const response = await api.post('submissions/', data);
        setSubmission(response.data);
      }
      setMessage({ type: 'success', text: 'Progress saved!' });
      setTimeout(() => setMessage(null), 3000);
    } catch (err) {
      setMessage({ type: 'error', text: 'Failed to save progress' });
    }
  };

  const handleFileUpload = async (file, type) => {
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);
    formData.append('document_type', type);

    setUploading(true);
    try {
      await api.post('documents/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      fetchSubmission();
      setMessage({ type: 'success', text: `${type} uploaded successfully` });
    } catch (err) {
      const errorData = err.response?.data;
      let errorMsg = 'Upload failed';
      
      if (typeof errorData === 'object' && errorData !== null) {
        // Try to get the first error message from any field
        const firstError = Object.values(errorData)[0];
        if (Array.isArray(firstError)) {
          errorMsg = firstError[0];
        } else if (typeof firstError === 'string') {
          errorMsg = firstError;
        } else if (errorData.detail) {
          errorMsg = errorData.detail;
        }
      }
      
      setMessage({ type: 'error', text: errorMsg });
    } finally {
      setUploading(false);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.currentTarget.classList.add('border-indigo-500', 'bg-indigo-50');
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.currentTarget.classList.remove('border-indigo-500', 'bg-indigo-50');
  };

  const handleDrop = (e, type) => {
    e.preventDefault();
    e.currentTarget.classList.remove('border-indigo-500', 'bg-indigo-50');
    const file = e.dataTransfer.files[0];
    handleFileUpload(file, type);
  };

  const submitKYC = async () => {
    try {
      await api.post(`submissions/${submission.id}/submit/`);
      fetchSubmission();
      setMessage({ type: 'success', text: 'KYC submitted successfully!' });
    } catch (err) {
      setMessage({ type: 'error', text: err.response?.data?.error || 'Submission failed' });
    }
  };

  if (loading) return <div className="text-center mt-20">Loading...</div>;

  if (submission && ['submitted', 'under_review', 'approved'].includes(submission.status)) {
    return (
      <div className="max-w-2xl mx-auto mt-10 p-8 bg-white rounded-xl shadow-lg text-center">
        {submission.status === 'approved' ? (
          <CheckCircle className="mx-auto text-green-500 mb-4" size={64} />
        ) : (
          <Clock className="mx-auto text-indigo-500 mb-4" size={64} />
        )}
        <h2 className="text-3xl font-bold mb-2">
          {submission.status === 'approved' ? 'KYC Approved!' : 'KYC Under Review'}
        </h2>
        <p className="text-gray-600 mb-6">
          {submission.status === 'approved' 
            ? 'Your account is now live. You can start collecting payments.'
            : 'We have received your details and documents. Our team is reviewing them.'}
        </p>
        <div className="bg-gray-50 p-4 rounded-lg text-left">
          <p><strong>Status:</strong> <span className="capitalize">{submission.status.replace('_', ' ')}</span></p>
          <p><strong>Submitted on:</strong> {new Date(submission.updated_at).toLocaleDateString()}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto bg-white rounded-xl shadow-lg overflow-hidden">
      <div className="flex bg-gray-50 border-b">
        {[1, 2, 3, 4].map((s) => (
          <div 
            key={s} 
            className={`flex-1 py-4 text-center font-medium border-b-2 transition ${
              step === s ? 'border-indigo-600 text-indigo-600' : 'border-transparent text-gray-400'
            }`}
          >
            Step {s}
          </div>
        ))}
      </div>

      <div className="p-8">
        {message && (
          <div className={`mb-6 p-4 rounded-lg flex items-center gap-3 ${
            message.type === 'success' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
          }`}>
            {message.type === 'success' ? <CheckCircle size={20} /> : <AlertCircle size={20} />}
            {message.text}
          </div>
        )}

        {submission?.status === 'rejected' && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <h3 className="text-red-800 font-bold mb-1 flex items-center gap-2">
              <AlertCircle size={18} /> KYC Rejected
            </h3>
            <p className="text-red-700">{submission.rejection_reason}</p>
          </div>
        )}

        {submission?.status === 'more_info_requested' && (
          <div className="mb-6 p-4 bg-amber-50 border border-amber-200 rounded-lg">
            <h3 className="text-amber-800 font-bold mb-1 flex items-center gap-2">
              <AlertCircle size={18} /> More Information Requested
            </h3>
            <p className="text-amber-700">{submission.rejection_reason}</p>
          </div>
        )}

        <form onSubmit={handleSubmit(saveProgress)}>
          {step === 1 && (
            <div className="space-y-4">
              <h3 className="text-xl font-bold mb-4">Personal Details</h3>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
                <input {...register('full_name', { required: true })} className="w-full p-2 border rounded" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                <input {...register('email', { required: true })} type="email" className="w-full p-2 border rounded" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Phone Number</label>
                <input {...register('phone', { required: true })} className="w-full p-2 border rounded" />
              </div>
            </div>
          )}

          {step === 2 && (
            <div className="space-y-4">
              <h3 className="text-xl font-bold mb-4">Business Details</h3>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Business Name</label>
                <input {...register('business_name', { required: true })} className="w-full p-2 border rounded" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Business Type</label>
                <select {...register('business_type', { required: true })} className="w-full p-2 border rounded">
                  <option value="">Select type</option>
                  <option value="individual">Individual / Freelancer</option>
                  <option value="proprietorship">Proprietorship</option>
                  <option value="pvt_ltd">Pvt Ltd Company</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Expected Monthly Volume (USD)</label>
                <input {...register('expected_monthly_volume', { required: true })} type="number" className="w-full p-2 border rounded" />
              </div>
            </div>
          )}

          {step === 3 && (
            <div className="space-y-6">
              <h3 className="text-xl font-bold mb-4">Document Upload</h3>
              <p className="text-sm text-gray-500 mb-4">Upload PDF, JPG, or PNG (Max 5MB each)</p>
              
              {['PAN', 'AADHAAR', 'BANK_STATEMENT'].map((type) => {
                const doc = submission?.documents.find(d => d.document_type === type);
                return (
                  <div 
                    key={type} 
                    onDragOver={handleDragOver}
                    onDragLeave={handleDragLeave}
                    onDrop={(e) => handleDrop(e, type)}
                    className="p-6 border-2 border-dashed rounded-xl flex items-center justify-between transition-all duration-200"
                  >
                    <div>
                      <p className="font-bold text-gray-800 text-lg">{type.replace('_', ' ')}</p>
                      {doc ? (
                        <span className="text-sm text-green-600 flex items-center gap-1 mt-1">
                          <CheckCircle size={14} /> Uploaded: {doc.file.split('/').pop()}
                        </span>
                      ) : (
                        <span className="text-sm text-gray-400 mt-1">Drag and drop or click to upload</span>
                      )}
                    </div>
                    <label className="cursor-pointer bg-indigo-600 text-white px-5 py-2.5 rounded-lg hover:bg-indigo-700 transition flex items-center gap-2 shadow-sm font-medium">
                      <Upload size={18} />
                      {doc ? 'Change' : 'Select File'}
                      <input 
                        type="file" 
                        className="hidden" 
                        onChange={(e) => handleFileUpload(e.target.files[0], type)}
                        disabled={uploading}
                      />
                    </label>
                  </div>
                );
              })}
            </div>
          )}

          {step === 4 && (
            <div className="space-y-4">
              <h3 className="text-xl font-bold mb-4">Review & Submit</h3>
              <div className="bg-gray-50 p-6 rounded-lg space-y-3">
                <p><strong>Name:</strong> {watch('full_name')}</p>
                <p><strong>Business:</strong> {watch('business_name')} ({watch('business_type')})</p>
                <p><strong>Documents:</strong> {submission?.documents.length} / 3 uploaded</p>
              </div>
              <p className="text-sm text-gray-500">
                By clicking submit, you agree that the information provided is accurate to the best of your knowledge.
              </p>
            </div>
          )}

          <div className="mt-10 flex justify-between">
            {step > 1 && (
              <button 
                type="button" 
                onClick={() => setStep(step - 1)}
                className="px-6 py-2 border rounded-lg hover:bg-gray-50"
              >
                Previous
              </button>
            )}
            <div className="ml-auto flex gap-3">
              <button 
                type="submit"
                className="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
              >
                Save Progress
              </button>
              {step < 4 ? (
                <button 
                  type="button" 
                  onClick={() => setStep(step + 1)}
                  className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
                >
                  Next
                </button>
              ) : (
                <button 
                  type="button"
                  onClick={submitKYC}
                  disabled={submission?.documents.length < 3}
                  className={`px-6 py-2 rounded-lg text-white ${
                    submission?.documents.length < 3 ? 'bg-gray-400 cursor-not-allowed' : 'bg-green-600 hover:bg-green-700'
                  }`}
                >
                  Submit KYC
                </button>
              )}
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};

export default KYCForm;
