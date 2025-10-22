
import React, { useEffect, useState, useMemo } from 'react';
import { getAttendance, getStudents } from '../services/api';
import { AttendanceRecordWithName, Student } from '../types';

const AttendanceLogPage: React.FC = () => {
    const [attendance, setAttendance] = useState<AttendanceRecordWithName[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [filterName, setFilterName] = useState('');
    const [filterRoll, setFilterRoll] = useState('');

    useEffect(() => {
        const fetchData = async () => {
            try {
                setLoading(true);
                const [attendanceData, studentsData] = await Promise.all([getAttendance(), getStudents()]);
                const studentsMap = new Map<string, string>(studentsData.map(s => [s.roll_no, s.name]));
                const attendanceWithNames = attendanceData.map(record => ({
                    ...record,
                    name: studentsMap.get(record.roll_no) || 'Unknown Student'
                }));
                setAttendance(attendanceWithNames.sort((a, b) => new Date(b.detected_time).getTime() - new Date(a.detected_time).getTime()));
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to fetch data');
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);
    
    const filteredAttendance = useMemo(() => {
        return attendance.filter(record => {
            const nameMatch = record.name.toLowerCase().includes(filterName.toLowerCase());
            const rollMatch = record.roll_no.toLowerCase().includes(filterRoll.toLowerCase());
            return nameMatch && rollMatch;
        });
    }, [attendance, filterName, filterRoll]);


    if (loading) return <div className="text-center p-8">Loading attendance logs...</div>;
    if (error) return <div className="text-center text-red-500 p-8">Error: {error}</div>;

    return (
        <div className="container mx-auto">
            <div className="bg-white p-6 rounded-xl shadow-lg">
                <div className="flex flex-col md:flex-row justify-between items-center mb-4 gap-4">
                    <h2 className="text-xl font-semibold text-gray-700">Attendance Records</h2>
                    <div className="flex flex-col md:flex-row gap-4 w-full md:w-auto">
                         <input
                            type="text"
                            placeholder="Filter by Name..."
                            value={filterName}
                            onChange={(e) => setFilterName(e.target.value)}
                            className="w-full md:w-auto px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                        />
                        <input
                            type="text"
                            placeholder="Filter by Roll No..."
                            value={filterRoll}
                            onChange={(e) => setFilterRoll(e.target.value)}
                            className="w-full md:w-auto px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                        />
                    </div>
                </div>

                <div className="overflow-x-auto">
                    <table className="w-full text-sm text-left text-gray-500">
                        <thead className="text-xs text-gray-700 uppercase bg-gray-50">
                            <tr>
                                <th scope="col" className="px-6 py-3">Roll No</th>
                                <th scope="col" className="px-6 py-3">Name</th>
                                <th scope="col" className="px-6 py-3">Date</th>
                                <th scope="col" className="px-6 py-3">Time</th>
                                <th scope="col" className="px-6 py-3">Camera ID</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filteredAttendance.map(record => (
                                <tr key={record.attendance_id} className="bg-white border-b hover:bg-gray-50">
                                    <td className="px-6 py-4 font-medium text-gray-900">{record.roll_no}</td>
                                    <td className="px-6 py-4">{record.name}</td>
                                    <td className="px-6 py-4">{new Date(record.date).toLocaleDateString()}</td>
                                    <td className="px-6 py-4">{new Date(record.detected_time).toLocaleTimeString()}</td>
                                    <td className="px-6 py-4">{record.camera_id}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                     {filteredAttendance.length === 0 && (
                        <p className="text-center text-gray-500 py-8">No matching records found.</p>
                    )}
                </div>
            </div>
        </div>
    );
};

export default AttendanceLogPage;
