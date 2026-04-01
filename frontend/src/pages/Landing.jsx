import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";
import { useEffect } from "react";

export default function Landing() {
  const { user, loginWithGoogle } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (user) navigate("/dashboard");
  }, [user]);

  return (
    <div className="min-h-screen bg-gray-950 text-white flex flex-col items-center justify-center px-4">
      
      {/* Logo */}
      <div className="text-5xl mb-4">🎬</div>

      {/* Headline */}
      <h1 className="text-4xl font-bold mb-3 text-center">
        Never miss a show again.
      </h1>
      <p className="text-gray-400 text-center max-w-md mb-10 text-lg">
        CineAlert watches BookMyShow for you and notifies you the moment 
        your preferred movie, format, and timing becomes available.
      </p>

      {/* Sign in button */}
      <button
        onClick={loginWithGoogle}
        className="flex items-center gap-3 bg-white text-gray-900 font-semibold px-6 py-3 rounded-full hover:bg-gray-100 transition text-lg"
      >
        <img
          src="https://www.google.com/favicon.ico"
          alt="Google"
          className="w-5 h-5"
        />
        Continue with Google
      </button>

      {/* How it works */}
      <div className="mt-16 grid grid-cols-1 sm:grid-cols-3 gap-6 max-w-2xl w-full text-center">
        {[
          { icon: "🔍", title: "Search any movie", desc: "Pick the movie you want to watch" },
          { icon: "⚙️", title: "Set your preferences", desc: "Choose city, format, and timing" },
          { icon: "🔔", title: "Get notified instantly", desc: "We alert you the moment seats open" },
        ].map((item) => (
          <div key={item.title} className="bg-gray-900 rounded-2xl p-6">
            <div className="text-3xl mb-3">{item.icon}</div>
            <h3 className="font-semibold mb-1">{item.title}</h3>
            <p className="text-gray-400 text-sm">{item.desc}</p>
          </div>
        ))}
      </div>

    </div>
  );
}