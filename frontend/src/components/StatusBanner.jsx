export default function StatusBanner({ status }) {
  if (status === 'connected') return null;
  return (
    <div className={`status-banner ${status}`}>
      {status === 'connecting' ? 'Connecting to chat server...' : 'Disconnected. Reconnecting...'}
    </div>
  );
}
