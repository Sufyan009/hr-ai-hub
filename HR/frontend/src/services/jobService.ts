import api from './api';

export const getJobs = (params = {}) => api.get('/jobposts/', { params });
export const getJob = (id: number | string) => api.get(`/jobposts/${id}/`);
export const createJob = (data: any) => api.post('/jobposts/', data);
export const updateJob = (id: number | string, data: any) => api.patch(`/jobposts/${id}/`, data);
export const deleteJob = (id: number | string) => api.delete(`/jobposts/${id}/`); 