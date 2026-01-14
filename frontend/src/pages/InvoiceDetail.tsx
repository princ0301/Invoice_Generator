import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { apiClient } from '../lib/api';
import type { Invoice } from '../types';
import { Layout } from '../components/Layout';

export const InvoiceDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [invoice, setInvoice] = useState<Invoice | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchInvoice();
  }, [id]);

  const fetchInvoice = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get(`/api/invoices/${id}`);
      setInvoice(response.data);
      setError('');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch invoice');
    } finally {
      setLoading(false);
    }
  };

  const handleMarkAsSent = async () => {
    try {
      await apiClient.post(`/api/invoices/${id}/send`);
      fetchInvoice();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to mark invoice as sent');
    }
  };

  const handleMarkAsPaid = async () => {
    try {
      await apiClient.post(`/api/invoices/${id}/pay`);
      fetchInvoice();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to mark invoice as paid');
    }
  };

  const handleDownloadPDF = async () => {
    if (!invoice) return;
    try {
      const response = await apiClient.get(`/api/invoices/${id}/pdf`, {
        responseType: 'blob',
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `invoice-${invoice.invoiceNumber}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err: any) {
      setError('Failed to download PDF');
    }
  };

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this invoice?')) return;
    try {
      await apiClient.delete(`/api/invoices/${id}`);
      navigate('/invoices');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete invoice');
    }
  };

  const calculateSubtotal = () => {
    if (!invoice) return 0;
    return invoice.lineItems.reduce(
      (sum, item) => sum + Number(item.quantity) * Number(item.unitRate),
      0
    );
  };

  const calculateTax = () => {
    if (!invoice) return 0;
    return calculateSubtotal() * (Number(invoice.taxRate) / 100);
  };

  const calculateTotal = () => {
    return calculateSubtotal() + calculateTax();
  };

  const getStatusBadgeClass = (status: string) => {
    switch (status) {
      case 'draft':
        return 'bg-gray-100 text-gray-800';
      case 'sent':
        return 'bg-blue-100 text-blue-800';
      case 'paid':
        return 'bg-green-100 text-green-800';
      case 'overdue':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <Layout>
        <div className="text-center py-12">
          <p className="text-gray-500">Loading invoice...</p>
        </div>
      </Layout>
    );
  }

  if (error || !invoice) {
    return (
      <Layout>
        <div className="text-center py-12">
          <p className="text-red-600">{error || 'Invoice not found'}</p>
          <Link to="/invoices" className="text-indigo-600 hover:text-indigo-900 mt-4 inline-block">
            Back to Invoices
          </Link>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="px-4 sm:px-6 lg:px-8">
        <div className="md:flex md:items-center md:justify-between mb-8">
          <div className="flex-1 min-w-0">
            <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">
              Invoice {invoice.invoiceNumber}
            </h2>
          </div>
          <div className="mt-4 flex md:mt-0 md:ml-4 space-x-3">
            <button
              onClick={handleDownloadPDF}
              className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-purple-600 hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500"
            >
              Download PDF
            </button>
            <button
              onClick={handleDelete}
              className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
            >
              Delete
            </button>
          </div>
        </div>

        {error && (
          <div className="mb-4 rounded-md bg-red-50 p-4">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        <div className="bg-white shadow overflow-hidden sm:rounded-lg">
          <div className="px-4 py-5 sm:px-6 flex justify-between items-center">
            <div>
              <h3 className="text-lg leading-6 font-medium text-gray-900">
                Invoice Details
              </h3>
              <p className="mt-1 max-w-2xl text-sm text-gray-500">
                Invoice information and line items
              </p>
            </div>
            <span
              className={`inline-flex rounded-full px-3 py-1 text-sm font-semibold ${getStatusBadgeClass(
                invoice.status
              )}`}
            >
              {invoice.status.toUpperCase()}
            </span>
          </div>
          <div className="border-t border-gray-200 px-4 py-5 sm:px-6">
            <dl className="grid grid-cols-1 gap-x-4 gap-y-8 sm:grid-cols-2">
              <div className="sm:col-span-1">
                <dt className="text-sm font-medium text-gray-500">Invoice Number</dt>
                <dd className="mt-1 text-sm text-gray-900">{invoice.invoiceNumber}</dd>
              </div>
              <div className="sm:col-span-1">
                <dt className="text-sm font-medium text-gray-500">Status</dt>
                <dd className="mt-1 text-sm text-gray-900 capitalize">{invoice.status}</dd>
              </div>
              <div className="sm:col-span-1">
                <dt className="text-sm font-medium text-gray-500">Invoice Date</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {new Date(invoice.invoiceDate).toLocaleDateString()}
                </dd>
              </div>
              <div className="sm:col-span-1">
                <dt className="text-sm font-medium text-gray-500">Due Date</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {new Date(invoice.dueDate).toLocaleDateString()}
                </dd>
              </div>
              {invoice.sentDate && (
                <div className="sm:col-span-1">
                  <dt className="text-sm font-medium text-gray-500">Sent Date</dt>
                  <dd className="mt-1 text-sm text-gray-900">
                    {new Date(invoice.sentDate).toLocaleDateString()}
                  </dd>
                </div>
              )}
              {invoice.paidDate && (
                <div className="sm:col-span-1">
                  <dt className="text-sm font-medium text-gray-500">Paid Date</dt>
                  <dd className="mt-1 text-sm text-gray-900">
                    {new Date(invoice.paidDate).toLocaleDateString()}
                  </dd>
                </div>
              )}
            </dl>
          </div>

          <div className="border-t border-gray-200 px-4 py-5 sm:px-6">
            <h4 className="text-sm font-medium text-gray-500 mb-4">Client Information</h4>
            {invoice.client ? (
              <dl className="grid grid-cols-1 gap-x-4 gap-y-4 sm:grid-cols-2">
                <div>
                  <dt className="text-sm font-medium text-gray-500">Name</dt>
                  <dd className="mt-1 text-sm text-gray-900">{invoice.client.name}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Email</dt>
                  <dd className="mt-1 text-sm text-gray-900">{invoice.client.email}</dd>
                </div>
                <div className="sm:col-span-2">
                  <dt className="text-sm font-medium text-gray-500">Address</dt>
                  <dd className="mt-1 text-sm text-gray-900">
                    {invoice.client.street && <div>{invoice.client.street}</div>}
                    {(invoice.client.city || invoice.client.state || invoice.client.zipCode) && (
                      <div>
                        {invoice.client.city}
                        {invoice.client.city && invoice.client.state && ', '}
                        {invoice.client.state} {invoice.client.zipCode}
                      </div>
                    )}
                    {invoice.client.country && <div>{invoice.client.country}</div>}
                  </dd>
                </div>
                {invoice.client.phone && (
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Phone</dt>
                    <dd className="mt-1 text-sm text-gray-900">{invoice.client.phone}</dd>
                  </div>
                )}
              </dl>
            ) : (
              <p className="text-sm text-gray-500">No client information available</p>
            )}
          </div>

          <div className="border-t border-gray-200 px-4 py-5 sm:px-6">
            <h4 className="text-sm font-medium text-gray-500 mb-4">Line Items</h4>
            <table className="min-w-full divide-y divide-gray-300">
              <thead>
                <tr>
                  <th className="py-3 text-left text-sm font-semibold text-gray-900">
                    Description
                  </th>
                  <th className="py-3 text-right text-sm font-semibold text-gray-900">
                    Quantity
                  </th>
                  <th className="py-3 text-right text-sm font-semibold text-gray-900">
                    Rate
                  </th>
                  <th className="py-3 text-right text-sm font-semibold text-gray-900">
                    Amount
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {invoice.lineItems.map((item) => (
                  <tr key={item.id}>
                    <td className="py-4 text-sm text-gray-900">{item.description}</td>
                    <td className="py-4 text-sm text-gray-900 text-right">
                      {item.quantity}
                    </td>
                    <td className="py-4 text-sm text-gray-900 text-right">
                      {Number(item.unitRate).toFixed(2)}
                    </td>
                    <td className="py-4 text-sm text-gray-900 text-right">
                      {(Number(item.quantity) * Number(item.unitRate)).toFixed(2)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            <div className="mt-6 flex justify-end">
              <div className="w-64 space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="font-medium text-gray-700">Subtotal:</span>
                  <span className="text-gray-900">{calculateSubtotal().toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="font-medium text-gray-700">
                    Tax ({invoice.taxRate}%):
                  </span>
                  <span className="text-gray-900">{calculateTax().toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-lg font-bold border-t pt-2">
                  <span className="text-gray-700">Total:</span>
                  <span className="text-gray-900">{calculateTotal().toFixed(2)}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};
