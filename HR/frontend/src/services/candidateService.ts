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

  const response = await api.get(`/api/candidates/?${params.toString()}`);
  return response.data;
};

export const deleteCandidate = async (id: number) => {
  const response = await api.delete(`/api/candidates/${id}/`);
  return response.data;
};

export const fetchFilterOptions = async () => {
  const [jobTitles, cities, sources, communicationSkills] = await Promise.all([
    api.get('/api/jobtitles/'),
    api.get('/api/cities/'),
    api.get('/api/sources/'),
    api.get('/api/communicationskills/'),
  ]);

  return {
    jobTitles: jobTitles.data,
    cities: cities.data,
    sources: sources.data,
    communicationSkills: communicationSkills.data,
  };
}; 