import { useRef, useEffect, useState } from 'react';

function formatTime(ts) {
  const d = new Date(ts);
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function formatDate(ts) {
  const d = new Date(ts);
  return d.toLocaleDateString([], { month: 'short', day: 'numeric' });
}

export default function MessageList({ messages, currentUser, onEdit, onDelete }) {
  const bottomRef = useRef(null);
  const [editingId, setEditingId] = useState(null);
  const [editContent, setEditContent] = useState('');

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const startEdit = (msg) => {
    setEditingId(msg.id);
    setEditContent(msg.content);
  };

  const submitEdit = async (msg) => {
    if (editContent.trim() && editContent !== msg.content) {
      await onEdit(msg.id, editContent.trim());
    }
    setEditingId(null);
  };

  if (messages.length === 0) {
    return (
      <div className="messages-empty">
        <p>No messages yet. Say hello!</p>
      </div>
    );
  }

  let lastDate = null;

  return (
    <div className="messages-container">
      {messages.map((msg) => {
        const isMine = msg.sender_id === currentUser.id;
        const dateStr = formatDate(msg.created_at);
        const showDate = dateStr !== lastDate;
        lastDate = dateStr;

        return (
          <div key={msg.id}>
            {showDate && <div className="date-divider">{dateStr}</div>}
            <div className={`message-wrapper ${isMine ? 'mine' : 'theirs'}`}>
              <div className={`message-bubble ${msg.is_deleted ? 'deleted' : ''}`}>
                {editingId === msg.id ? (
                  <div className="edit-form">
                    <input
                      value={editContent}
                      onChange={(e) => setEditContent(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') submitEdit(msg);
                        if (e.key === 'Escape') setEditingId(null);
                      }}
                      autoFocus
                    />
                    <button onClick={() => submitEdit(msg)}>Save</button>
                    <button onClick={() => setEditingId(null)}>Cancel</button>
                  </div>
                ) : (
                  <span className="message-content">
                    {msg.is_deleted ? <em>[Message deleted]</em> : msg.content}
                  </span>
                )}
                <div className="message-meta">
                  <span className="message-time">{formatTime(msg.created_at)}</span>
                  {msg.is_edited && !msg.is_deleted && <span className="edited-badge">edited</span>}
                </div>
                {isMine && !msg.is_deleted && editingId !== msg.id && (
                  <div className="message-actions">
                    <button className="action-btn" onClick={() => startEdit(msg)} title="Edit">✎</button>
                    <button className="action-btn danger" onClick={() => onDelete(msg.id)} title="Delete">✕</button>
                  </div>
                )}
              </div>
            </div>
          </div>
        );
      })}
      <div ref={bottomRef} />
    </div>
  );
}
