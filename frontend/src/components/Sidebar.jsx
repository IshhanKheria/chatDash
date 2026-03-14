import { useState } from 'react';
import { searchUsers } from '../api/auth';
import RoomPanel from './RoomPanel';
import ProfileModal from './ProfileModal';

export default function Sidebar({
  user,
  conversations,
  allUsers,
  activeContact,
  onSelectContact,
  onLogout,
  onlineUsers,
  activeRoom,
  onSelectRoom,
}) {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [searching, setSearching] = useState(false);
  const [showProfile, setShowProfile] = useState(false);

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

  const displayUsers = searchQuery
    ? searchResults
    : conversations.length > 0
    ? conversations
    : allUsers;

  const sectionLabel = searchQuery
    ? 'Search results'
    : conversations.length > 0
    ? 'Recent chats'
    : 'All users';

  return (
    <div className="sidebar">
      {/* Header */}
      <div className="sidebar-header">
        <div className="user-info">
          <button
            className="avatar"
            onClick={() => setShowProfile(true)}
            title="Edit profile"
          >
            {user?.username?.[0]?.toUpperCase()}
          </button>
          <div className="user-meta">
            <span className="username">{user?.username}</span>
            <button className="profile-btn" onClick={() => setShowProfile(true)}>
              Edit profile
            </button>
          </div>
        </div>

        <div className="sidebar-actions">
          <button className="icon-btn danger" onClick={onLogout} title="Sign out">
            {/* Simple exit icon */}
            <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
              <polyline points="16 17 21 12 16 7"/>
              <line x1="21" y1="12" x2="9" y2="12"/>
            </svg>
          </button>
        </div>
      </div>

      {showProfile && <ProfileModal onClose={() => setShowProfile(false)} />}

      {/* Search */}
      <div className="search-box">
        <div className="search-input-wrap">
          <span className="search-icon">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
          </span>
          <input
            type="text"
            placeholder="Search or start new chat"
            value={searchQuery}
            onChange={handleSearch}
            className="search-input"
          />
        </div>
      </div>

      {/* Conversations list */}
      <div className="conversations-list">
        <div className="list-section-label">{sectionLabel}</div>

        {searching && <div className="list-loading">Searching…</div>}

        {!searching && displayUsers.length === 0 && (
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
            <div className="contact-avatar-wrap">
              <div className="contact-avatar">
                {contact.username?.[0]?.toUpperCase()}
              </div>
              <div className={`online-dot ${onlineUsers?.has(contact.id) ? 'online' : ''}`} />
            </div>

            <div className="contact-info">
              <span className="contact-name">{contact.username}</span>
              <span className="contact-preview">{contact.email}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Rooms section */}
      <RoomPanel onSelectRoom={onSelectRoom} activeRoom={activeRoom} />
    </div>
  );
}
