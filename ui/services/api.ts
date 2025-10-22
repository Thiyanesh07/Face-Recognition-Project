import { Student, Camera, AttendanceRecord } from '../types';

const BASE_URL = 'http://127.0.0.1:5000'; // Your Flask backend URL

// Helper to get authorization headers
const getAuthHeaders = () => {
    const token = localStorage.getItem('authToken');
    const headers: HeadersInit = {
        'Content-Type': 'application/json',
    };
    if (token) {
        headers['Authorization'] = token;
    }
    return headers;
};

// Helper to handle API responses
const handleResponse = async (response: Response) => {
    if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: 'An unknown network error occurred' }));
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }
    return response.json();
};


// --- Authentication ---
export const login = async (email: string, password: string): Promise<{ token: string }> => {
    const response = await fetch(`${BASE_URL}/auth/login`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
    });
    return handleResponse(response);
};

// --- Students ---
export const getStudents = async (): Promise<Student[]> => {
    const response = await fetch(`${BASE_URL}/students`, {
        headers: getAuthHeaders(),
    });
    return handleResponse(response);
};

export const addStudent = async (roll_no: string, name: string): Promise<{ message: string }> => {
    const response = await fetch(`${BASE_URL}/students`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ roll_no, name }),
    });
    return handleResponse(response);
};

// --- Cameras ---
export const getCameras = async (): Promise<Camera[]> => {
    const response = await fetch(`${BASE_URL}/cameras`, {
        headers: getAuthHeaders(),
    });
    return handleResponse(response);
};

export const addCamera = async (ip_address: string): Promise<{ message: string }> => {
    const response = await fetch(`${BASE_URL}/cameras`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ ip_address }),
    });
    return handleResponse(response);
};

// --- Attendance ---
export const getAttendance = async (): Promise<AttendanceRecord[]> => {
    const response = await fetch(`${BASE_URL}/attendance`, {
        headers: getAuthHeaders(),
    });
    return handleResponse(response);
};
