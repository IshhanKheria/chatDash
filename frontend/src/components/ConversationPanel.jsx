import { useRef } from 'react';
import MessageList from './MessageList';
import MessageComposer from './MessageComposer';

export default function ConversationPanel({
  currentUser,
  contact,
  messages,
  loading,
  onSend,
  onEdit,
  onDelete,
  wsStatus,
  send,
}) {
  const typingTimer = useRef(null);

  const handleTyping = () => {
    send({ type: 'typing', receiver_id: contact.id, is_typing: true });
    clearTimeout(typingTimer.current);
    typingTimer.current = setTimeout(() => {
      send({ type: 'typing', receiver_id: contact.id, is_typing: false });
    }, 1500);
  };

  return (
    <div className="conversation-panel">
      {/* Header */}
      <div className="conversation-header">
        <div className="contact-avatar large">
          {contact.username?.[0]?.toUpperCase()}
        </div>
        <div className="contact-details">
          <h3>{contact.username}</h3>
          <div className="contact-status">{contact.email}</div>
        </div>
      </div>

      {loading ? (
        <div className="messages-loading">Loading messages…</div>
      ) : (
        <MessageList
          messages={messages}
          currentUser={currentUser}
          onEdit={onEdit}
          onDelete={onDelete}
        />
      )}

      <MessageComposer
        onSend={onSend}
        onTyping={handleTyping}
        disabled={wsStatus !== 'connected'}
      />
    </div>
  );
}
