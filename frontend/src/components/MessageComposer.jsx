import { useState } from 'react';

// Send arrow icon
function SendIcon() {
  return (
    <svg
      width="20"
      height="20"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2.2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <line x1="22" y1="2" x2="11" y2="13" />
      <polygon points="22 2 15 22 11 13 2 9 22 2" />
    </svg>
  );
}

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
          onTyping?.();
        }}
        onKeyDown={handleKeyDown}
        placeholder={disabled ? 'Connecting to server…' : 'Type a message'}
        disabled={disabled}
        rows={1}
        className="composer-input"
      />
      <button
        type="submit"
        className="send-btn"
        disabled={disabled || !content.trim()}
        title="Send (Enter)"
      >
        <SendIcon />
      </button>
    </form>
  );
}
