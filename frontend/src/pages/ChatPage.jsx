import { useState, useEffect, useCallback, useRef } from 'react';
import { useAuth } from '../hooks/useAuth';
import { useWebSocket } from '../hooks/useWebSocket';
import { getHistory, getConversations, editMessage, deleteMessage } from '../api/messages';
import { listUsers, searchUsers } from '../api/auth';
import Sidebar from '../components/Sidebar';
import ConversationPanel from '../components/ConversationPanel';
import StatusBanner from '../components/StatusBanner';

export default function ChatPage() {
  const { user, logout } = useAuth();
  const [activeContact, setActiveContact] = useState(null);
  const [messages, setMessages] = useState([]);
  const [conversations, setConversations] = useState([]);
  const [allUsers, setAllUsers] = useState([]);
  const [wsStatus, setWsStatus] = useState('disconnected');
  const [loadingMessages, setLoadingMessages] = useState(false);

  const handleWsMessage = useCallback((data) => {
    switch (data.type) {
      case 'connected':
        setWsStatus('connected');
        break;
      case 'message_sent':
      case 'receive_message':
        setMessages((prev) => {
          const exists = prev.find((m) => m.id === data.message.id);
          if (exists) return prev;
          return [...prev, data.message];
        });
        setConversations((prev) => {
          const senderId = data.message.sender_id;
          const receiverId = data.message.receiver_id;
          const partnerId = senderId === user.id ? receiverId : senderId;
          if (!prev.find((c) => c.id === partnerId)) {
            // Will refresh on next load
          }
          return prev;
        });
        break;
      case 'message_edited':
        setMessages((prev) =>
          prev.map((m) => (m.id === data.message.id ? data.message : m))
        );
        break;
      case 'message_deleted':
        setMessages((prev) =>
          prev.map((m) => (m.id === data.message.id ? data.message : m))
        );
        break;
      case 'typing':
        // handled in ConversationPanel
        break;
    }
  }, [user]);

  const { send, status } = useWebSocket({
    onMessage: handleWsMessage,
    enabled: !!user,
  });

  useEffect(() => {
    setWsStatus(status);
  }, [status]);

  useEffect(() => {
    if (!user) return;
    Promise.all([getConversations(), listUsers()])
      .then(([convRes, usersRes]) => {
        setConversations(convRes.data.conversations || []);
        setAllUsers(usersRes.data.users || []);
      })
      .catch(console.error);
  }, [user]);

  const openConversation = useCallback(async (contact) => {
    setActiveContact(contact);
    setLoadingMessages(true);
    try {
      const res = await getHistory(contact.id);
      setMessages(res.data.results?.messages || res.data.messages || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingMessages(false);
    }
    setConversations((prev) => {
      if (!prev.find((c) => c.id === contact.id)) return [...prev, contact];
      return prev;
    });
  }, []);

  const sendMessage = useCallback((content) => {
    if (!activeContact) return;
    send({ type: 'send_message', receiver_id: activeContact.id, content });
  }, [activeContact, send]);

  const handleEditMessage = async (messageId, content) => {
    try {
      await editMessage(messageId, content);
    } catch (err) {
      console.error(err);
    }
  };

  const handleDeleteMessage = async (messageId) => {
    try {
      const res = await deleteMessage(messageId);
      if (res.data.success) {
        setMessages((prev) =>
          prev.map((m) => m.id === messageId ? { ...m, is_deleted: true, content: '[Message deleted]' } : m)
        );
      }
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="chat-layout">
      <Sidebar
        user={user}
        conversations={conversations}
        allUsers={allUsers}
        activeContact={activeContact}
        onSelectContact={openConversation}
        onLogout={logout}
      />
      <div className="chat-main">
        <StatusBanner status={wsStatus} />
        {activeContact ? (
          <ConversationPanel
            currentUser={user}
            contact={activeContact}
            messages={messages}
            loading={loadingMessages}
            onSend={sendMessage}
            onEdit={handleEditMessage}
            onDelete={handleDeleteMessage}
            wsStatus={wsStatus}
            send={send}
          />
        ) : (
          <div className="empty-state">
            <div className="empty-icon">💬</div>
            <h2>Welcome to ChatDash</h2>
            <p>Select a conversation or search for a user to start chatting.</p>
          </div>
        )}
      </div>
    </div>
  );
}
