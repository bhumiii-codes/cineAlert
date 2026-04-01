import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import axios from "axios";

const API = "http://localhost:5000";

export default function Dashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user) navigate("/");
  }, [user]);

  useEffect(() => {
    if (user) fetchAlerts();
  }, [user]);

  const fetchAlerts = async () => {
    try {
      const res = await axios.get(`${API}/alerts/${user.uid}`);
      setAlerts(res.data.alerts);
    } catch {
      setAlerts([]);
    } finally {
      setLoading(false);
    }
  };

  const deleteAlert = async (id) => {
    await axios.delete(`${API}/alerts/${id}`);
    fetchAlerts();
  };

  const toggleAlert = async (id) => {
    await axios.patch(`${API}/alerts/${id}/toggle`);
    fetchAlerts();
  };

  return (
    <div className="min-h-screen bg-gray-950 text-white px-4 py-8 max-w-2xl mx-auto">
      
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-3">
          <img src={user?.photoURL} className="w-9 h-9 rounded-full" />
          <div>
            <p className="font-semibold">{user?.displayName}</p>
            <p className="text-gray-400 text-sm">{user?.email}</p>
          </div>
        </div>
        <button
          onClick={logout}
          className="text-sm text-gray-400 hover:text-white transition"
        >
          Sign out
        </button>
      </div>

      {/* New Alert Button */}
      <button
        onClick={() => navigate("/create")}
        className="w-full bg-indigo-600 hover:bg-indigo-500 transition rounded-2xl py-4 font-semibold text-lg mb-8"
      >
        + Create New Alert
      </button>

      {/* Alerts List */}
      <h2 className="text-xl font-bold mb-4">Your Alerts</h2>

      {loading ? (
        <p className="text-gray-400">Loading...</p>
      ) : alerts.length === 0 ? (
        <div className="bg-gray-900 rounded-2xl p-8 text-center text-gray-400">
          <div className="text-4xl mb-3">🔔</div>
          <p>No alerts yet. Create one and we'll watch for you!</p>
        </div>
      ) : (
        <div className="flex flex-col gap-4">
          {alerts.map((alert) => (
            <div key={alert.id} className="bg-gray-900 rounded-2xl p-5">
              <div className="flex justify-between items-start mb-3">
                <h3 className="font-semibold text-lg">{alert.movie_name}</h3>
                <span className={`text-xs px-2 py-1 rounded-full ${
                  alert.is_active 
                    ? "bg-green-900 text-green-400" 
                    : "bg-gray-800 text-gray-400"
                }`}>
                  {alert.is_active ? "Active" : "Paused"}
                </span>
              </div>
              <div className="text-sm text-gray-400 flex flex-wrap gap-2 mb-4">
                <span className="bg-gray-800 px-3 py-1 rounded-full">📍 {alert.city}</span>
                <span className="bg-gray-800 px-3 py-1 rounded-full">📺 {alert.format}</span>
                <span className="bg-gray-800 px-3 py-1 rounded-full">🕐 {alert.preferred_time}</span>
                {alert.venue !== "ANY" && (
                  <span className="bg-gray-800 px-3 py-1 rounded-full">🏟 {alert.venue}</span>
                )}
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => toggleAlert(alert.id)}
                  className="flex-1 py-2 rounded-xl text-sm font-medium bg-gray-800 hover:bg-gray-700 transition"
                >
                  {alert.is_active ? "Pause" : "Resume"}
                </button>
                <button
                  onClick={() => deleteAlert(alert.id)}
                  className="flex-1 py-2 rounded-xl text-sm font-medium bg-red-950 text-red-400 hover:bg-red-900 transition"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}