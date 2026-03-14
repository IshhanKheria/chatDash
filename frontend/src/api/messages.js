import client from './client';

export const getHistory = (userId, page = 1, pageSize = 50) =>
  client.get(`/messages/history/${userId}/?page=${page}&page_size=${pageSize}`);

export const editMessage = (messageId, content) =>
  client.put(`/messages/${messageId}/`, { content });

export const deleteMessage = (messageId) =>
  client.delete(`/messages/${messageId}/delete/`);

export const getConversations = () => client.get('/conversations/');
