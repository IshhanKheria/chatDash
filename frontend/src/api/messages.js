import client from './client';

export const getHistory = (userId, page = 1, pageSize = 50) =>
  client.get(`/messages/history/${userId}/?page=${page}&page_size=${pageSize}`);

export const editMessage = (messageId, content) =>
  client.put(`/messages/${messageId}/`, { content });

export const deleteMessage = (messageId) =>
  client.delete(`/messages/${messageId}/delete/`);

export const getConversations = () => client.get('/conversations/');

export const getRooms = () => client.get('/rooms/');
export const createRoom = (data) => client.post('/rooms/', data);
export const getRoomDetail = (roomId) => client.get(`/rooms/${roomId}/`);
export const getRoomMessages = (roomId, page = 1) => client.get(`/rooms/${roomId}/messages/?page=${page}`);
export const addRoomMember = (roomId, userId) => client.post(`/rooms/${roomId}/members/`, { user_id: userId });
