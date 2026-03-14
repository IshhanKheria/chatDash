import { useRef } from 'react';
import MessageList from './MessageList';
import MessageComposer from './MessageComposer';

export default function RoomConversationPanel({
  currentUser,
  room,
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
    send({ type: 'typing', room_id: room.id, is_typing: true });
    clearTimeout(typingTimer.current);
    typingTimer.current = setTimeout(() => {
      send({ type: 'typing', room_id: room.id, is_typing: false });
    }, 1500);
  };

  return (
    <div className="conversation-panel">
      <div className="conversation-header room-conversation-header">
        <div className="room-icon">#</div>
        <div className="contact-details">
          <h3>
            {room.name}
            <span className="room-badge" style={{ marginLeft: '0.5rem' }}>Room</span>
          </h3>
          {room.description && (
            <span className="contact-email">{room.description}</span>
          )}
        </div>
      </div>

      {loading ? (
        <div className="messages-loading">Loading messages...</div>
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
