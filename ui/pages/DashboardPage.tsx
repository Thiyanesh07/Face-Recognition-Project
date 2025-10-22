
import React, { useEffect, useState, useMemo } from 'react';
import { getStudents, getAttendance } from '../services/api';
import { Student, AttendanceRecord } from '../types';
import StatCard from '../components/StatCard';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const DashboardPage: React.FC = () => {
    const [students, setStudents] = useState<Student[]>([]);
    const [attendance, setAttendance] = useState<AttendanceRecord[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchData = async () => {
            try {
                setLoading(true);
                const [studentsData, attendanceData] = await Promise.all([getStudents(), getAttendance()]);
                setStudents(studentsData);
                setAttendance(attendanceData);
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to fetch data');
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    const todayString = new Date().toISOString().split('T')[0];
    const presentToday = useMemo(() => {
        const presentRollNos = new Set(
            attendance.filter(record => record.date === todayString).map(record => record.roll_no)
        );
        return presentRollNos.size;
    }, [attendance, todayString]);

    const absentToday = useMemo(() => {
        return students.length - presentToday;
    }, [students.length, presentToday]);

    const attendanceRate = useMemo(() => {
        if (students.length === 0) return 0;
        return ((presentToday / students.length) * 100).toFixed(1);
    }, [presentToday, students.length]);
    
    const chartData = useMemo(() => {
        const last7Days = Array.from({ length: 7 }, (_, i) => {
            const d = new Date();
            d.setDate(d.getDate() - i);
            return d.toISOString().split('T')[0];
        }).reverse();

        return last7Days.map(date => {
            const count = new Set(attendance.filter(a => a.date === date).map(a => a.roll_no)).size;
            return {
                name: new Date(date).toLocaleDateString('en-US', { weekday: 'short' }),
                present: count
            };
        });
    }, [attendance]);


    if (loading) return <div className="text-center p-8">Loading dashboard...</div>;
    if (error) return <div className="text-center text-red-500 p-8">Error: {error}</div>;

    return (
        <div className="container mx-auto">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                <StatCard 
                    title="Total Students" 
                    value={students.length} 
                    color="#4f46e5" 
                    icon={<svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.653-.122-1.28-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.653.122-1.28.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" /></svg>} 
                />
                <StatCard 
                    title="Present Today" 
                    value={presentToday} 
                    color="#10b981" 
                    icon={<svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>}
                />
                <StatCard 
                    title="Absent Today" 
                    value={absentToday}
                    color="#ef4444" 
                    icon={<svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7a4 4 0 11-8 0 4 4 0 018 0zM9 17v1a6 6 0 00-6 6h12a6 6 0 00-6-6v-1m9-4l-4 4m0-4l4 4" /></svg>}
                />
                <StatCard 
                    title="Attendance Rate Today" 
                    value={`${attendanceRate}%`}
                    color="#f59e0b" 
                    icon={<svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>} 
                />
            </div>

            <div className="bg-white p-6 rounded-xl shadow-lg">
                <h3 className="text-xl font-semibold text-gray-700 mb-4">Last 7 Days Attendance</h3>
                <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={chartData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" />
                        <YAxis allowDecimals={false} />
                        <Tooltip />
                        <Legend />
                        <Bar dataKey="present" fill="#4f46e5" name="Students Present" />
                    </BarChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
};

export default DashboardPage;
