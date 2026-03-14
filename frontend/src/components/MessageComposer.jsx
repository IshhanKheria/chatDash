import { useState } from 'react';

export default function MessageComposer({ onSend, onTyping, disabled }) {
  const [content, setContent] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    const trimmed = content.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setContent('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form className="message-composer" onSubmit={handleSubmit}>
      <textarea
        value={content}
        onChange={(e) => {
          setContent(e.target.value);
          onTyping();
        }}
        onKeyDown={handleKeyDown}
        placeholder={disabled ? 'Connecting...' : 'Type a message... (Enter to send)'}
        disabled={disabled}
        rows={1}
        className="composer-input"
      />
      <button type="submit" className="send-btn" disabled={disabled || !content.trim()}>
        Send
      </button>
    </form>
  );
}
