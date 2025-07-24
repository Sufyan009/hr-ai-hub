import api from './api';

export const fetchCandidates = async (page: number, search: string, filters: any) => {
  const params = new URLSearchParams();
  params.append('page', String(page));
  if (search) {
    params.append('search', search);
  }
  Object.keys(filters).forEach(key => {
    if (filters[key]) {
      params.append(key, filters[key]);
    }
  });

  const response = await api.get(`/candidates/?${params.toString()}`);
  return response.data;
};

export const getCandidate = async (id: number) => {
  const response = await api.get(`/candidates/${id}/`);
  return response.data;
};

export const createCandidate = async (data: any) => {
  const response = await api.post('/candidates/', data);
  return response.data;
};

export const updateCandidate = async (id: number, data: any) => {
  const response = await api.put(`/candidates/${id}/`, data);
  return response.data;
};

export const deleteCandidate = async (id: number) => {
  const response = await api.delete(`/candidates/${id}/`);
  return response.data;
};

export const fetchFilterOptions = async () => {
  const [jobTitles, cities, sources, communicationSkills] = await Promise.all([
    api.get('/jobtitles/'),
    api.get('/cities/'),
    api.get('/sources/'),
    api.get('/communicationskills/'),
  ]);

  return {
    jobTitles: jobTitles.data,
    cities: cities.data,
    sources: sources.data,
    communicationSkills: communicationSkills.data,
  };
}; 