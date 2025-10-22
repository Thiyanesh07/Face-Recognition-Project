
import React, { useState, useEffect } from 'react';
import { getStudents, addStudent } from '../services/api';
import { Student } from '../types';

const ManageStudentsPage: React.FC = () => {
    const [students, setStudents] = useState<Student[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    
    const [newRollNo, setNewRollNo] = useState('');
    const [newName, setNewName] = useState('');
    const [formError, setFormError] = useState('');
    const [formSuccess, setFormSuccess] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);

    const fetchStudents = async () => {
        try {
            setLoading(true);
            const data = await getStudents();
            setStudents(data);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to fetch students');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchStudents();
    }, []);
    
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setFormError('');
        setFormSuccess('');
        setIsSubmitting(true);
        try {
            const response = await addStudent(newRollNo, newName);
            setFormSuccess(response.message);
            setNewName('');
            setNewRollNo('');
            fetchStudents(); // Refresh the list
        } catch (err) {
            setFormError(err instanceof Error ? err.message : 'Failed to add student');
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="container mx-auto grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-1 bg-white p-6 rounded-xl shadow-lg h-fit">
                 <h2 className="text-xl font-semibold text-gray-700 mb-4">Add New Student</h2>
                {formError && <p className="text-red-500 mb-4">{formError}</p>}
                {formSuccess && <p className="text-green-500 mb-4">{formSuccess}</p>}
                <form onSubmit={handleSubmit}>
                    <div className="mb-4">
                        <label htmlFor="rollNo" className="block text-sm font-medium text-gray-700">Roll Number</label>
                        <input type="text" id="rollNo" value={newRollNo} onChange={(e) => setNewRollNo(e.target.value)} required className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary sm:text-sm" />
                    </div>
                    <div className="mb-4">
                        <label htmlFor="name" className="block text-sm font-medium text-gray-700">Student Name</label>
                        <input type="text" id="name" value={newName} onChange={(e) => setNewName(e.target.value)} required className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary sm:text-sm" />
                    </div>
                    <button type="submit" disabled={isSubmitting} className="w-full bg-primary text-white py-2 px-4 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary disabled:bg-indigo-300">
                        {isSubmitting ? 'Adding...' : 'Add Student'}
                    </button>
                </form>
            </div>
            <div className="lg:col-span-2 bg-white p-6 rounded-xl shadow-lg">
                <h2 className="text-xl font-semibold text-gray-700 mb-4">Registered Students</h2>
                {loading && <p>Loading...</p>}
                {error && <p className="text-red-500">{error}</p>}
                <div className="overflow-x-auto max-h-96">
                     <table className="w-full text-sm text-left text-gray-500">
                        <thead className="text-xs text-gray-700 uppercase bg-gray-50 sticky top-0">
                            <tr>
                                <th scope="col" className="px-6 py-3">Roll No</th>
                                <th scope="col" className="px-6 py-3">Name</th>
                            </tr>
                        </thead>
                        <tbody>
                            {students.map(student => (
                                <tr key={student.roll_no} className="bg-white border-b hover:bg-gray-50">
                                    <td className="px-6 py-4 font-medium text-gray-900">{student.roll_no}</td>
                                    <td className="px-6 py-4">{student.name}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default ManageStudentsPage;
