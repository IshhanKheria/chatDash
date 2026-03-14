import { useState, useEffect } from 'react';
import { getRooms, createRoom } from '../api/messages';

export default function RoomPanel({ onSelectRoom, activeRoom }) {
  const [rooms, setRooms] = useState([]);
  const [showCreate, setShowCreate] = useState(false);
  const [newRoomName, setNewRoomName] = useState('');
  const [newRoomDesc, setNewRoomDesc] = useState('');
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    getRooms().then(res => setRooms(res.data.rooms || [])).catch(() => {});
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!newRoomName.trim()) return;
    setCreating(true);
    try {
      const res = await createRoom({ name: newRoomName.trim(), description: newRoomDesc.trim() });
      setRooms(prev => [...prev, res.data.room]);
      setNewRoomName('');
      setNewRoomDesc('');
      setShowCreate(false);
    } catch (err) {
      alert(err.response?.data?.message || 'Failed to create room.');
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="room-panel">
      <div className="room-panel-header">
        <span className="list-label">Rooms</span>
        <button
          className="create-room-btn"
          onClick={() => setShowCreate(!showCreate)}
          title="Create room"
        >
          +
        </button>
      </div>

      {showCreate && (
        <form className="create-room-form" onSubmit={handleCreate}>
          <input
            value={newRoomName}
            onChange={e => setNewRoomName(e.target.value)}
            placeholder="Room name"
            required
          />
          <input
            value={newRoomDesc}
            onChange={e => setNewRoomDesc(e.target.value)}
            placeholder="Description (optional)"
          />
          <button type="submit" disabled={creating}>
            {creating ? 'Creating...' : 'Create'}
          </button>
        </form>
      )}

      {rooms.length === 0 ? (
        <div className="empty-list">No rooms yet.</div>
      ) : (
        rooms.map(room => (
          <div
            key={room.id}
            className={`contact-item ${activeRoom?.id === room.id ? 'active' : ''}`}
            onClick={() => onSelectRoom(room)}
          >
            <div className="room-icon">#</div>
            <div className="contact-info">
              <span className="contact-name">{room.name}</span>
              <span className="member-count">{room.member_count} members</span>
            </div>
          </div>
        ))
      )}
    </div>
  );
}
