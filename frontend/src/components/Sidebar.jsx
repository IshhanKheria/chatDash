import { useState } from 'react';
import { searchUsers } from '../api/auth';

export default function Sidebar({ user, conversations, allUsers, activeContact, onSelectContact, onLogout }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [searching, setSearching] = useState(false);

  const handleSearch = async (e) => {
    const q = e.target.value;
    setSearchQuery(q);
    if (q.trim().length < 1) {
      setSearchResults([]);
      return;
    }
    setSearching(true);
    try {
      const res = await searchUsers(q);
      setSearchResults(res.data.users || []);
    } catch {
      setSearchResults([]);
    } finally {
      setSearching(false);
    }
  };

  const displayUsers = searchQuery ? searchResults : conversations.length > 0 ? conversations : allUsers;

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <div className="user-info">
          <div className="avatar">{user?.username?.[0]?.toUpperCase()}</div>
          <span className="username">{user?.username}</span>
        </div>
        <button className="logout-btn" onClick={onLogout} title="Logout">⬡</button>
      </div>

      <div className="search-box">
        <input
          type="text"
          placeholder="Search users..."
          value={searchQuery}
          onChange={handleSearch}
          className="search-input"
        />
      </div>

      <div className="conversations-list">
        <div className="list-label">
          {searchQuery ? 'Search Results' : conversations.length > 0 ? 'Recent Chats' : 'All Users'}
        </div>
        {searching && <div className="list-loading">Searching...</div>}
        {displayUsers.length === 0 && !searching && (
          <div className="empty-list">
            {searchQuery ? 'No users found.' : 'No conversations yet.'}
          </div>
        )}
        {displayUsers.map((contact) => (
          <div
            key={contact.id}
            className={`contact-item ${activeContact?.id === contact.id ? 'active' : ''}`}
            onClick={() => onSelectContact(contact)}
          >
            <div className="contact-avatar">{contact.username?.[0]?.toUpperCase()}</div>
            <div className="contact-info">
              <span className="contact-name">{contact.username}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
