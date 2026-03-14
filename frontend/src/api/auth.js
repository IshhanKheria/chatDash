import client from './client';

export const register = (data) => client.post('/auth/register', data);
export const login = (data) => client.post('/auth/login', data);
export const me = () => client.get('/auth/me');
export const updateProfile = (data) => client.put('/auth/profile', data);
export const searchUsers = (q) => client.get(`/auth/users/search?q=${encodeURIComponent(q)}`);
export const listUsers = () => client.get('/auth/users');
